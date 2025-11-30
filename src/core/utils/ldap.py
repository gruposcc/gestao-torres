import asyncio
from contextlib import contextmanager
from functools import partial
from logging import getLogger

from ldap3 import ALL, Connection, Server

from core.settings import (
    LDAP_BASE_DN,
    LDAP_SERVER,
    LDAP_UPN_SUFFIX,
    LDAP_USE_SSL,
)

logger = getLogger("app.ldap-client")
logger.setLevel("DEBUG")

SERVER = Server(LDAP_SERVER, get_info=ALL, use_ssl=LDAP_USE_SSL)


@contextmanager
def _connect(username: str, password: str):
    try:
        conn = Connection(
            SERVER,
            user=f"{username}@{LDAP_UPN_SUFFIX}",
            password=password,
            authentication="SIMPLE",
            auto_bind=True,
        )
        yield conn
        conn.unbind()
    # except :  LDAPBindError: automatic bind not successful - invalidCredentials
    # TODO

    except Exception as e:
        # logger.warning("ERRO NA CONEXÃO DO LDAP")
        raise e


def _get_user_info(username: str, password: str):
    search_filter = (
        f"(sAMAccountName={username})"  # Usuário que logou busca por si mesmo
    )

    with _connect(username, password) as conn:
        conn.search(
            search_base=LDAP_BASE_DN,  # pyright: ignore[reportArgumentType]
            search_filter=search_filter,
            attributes=["distinguishedName", "displayName", "mail", "memberOf"],
        )

        entry = conn.entries[
            0
        ]  # Verificar a len ? pelo menos esse deve ter se não daria erro na conexão, auto_bind

    logger.debug(f"entry LDAP : {entry}")

    result = {
        "dn": entry.distinguishedName.value,
        "displayName": entry.displayName.value if "displayName" in entry else None,
        "mail": entry.mail.value if "mail" in entry else None,
        "memberOf": entry.memberOf.values if "memberOf" in entry else [],
    }

    return result


async def ldap_get_user_info(username: str, password: str):
    loop = asyncio.get_running_loop()
    func = partial(_get_user_info, username, password)
    return await loop.run_in_executor(None, func)
