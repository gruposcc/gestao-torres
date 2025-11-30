from jinja2 import nodes
from jinja2.ext import Extension


class CommentExtension(Extension):
    tags = {"comment"}

    def parse(self, parser):
        # pega o token {% comment %}
        lineno = next(parser.stream).lineno

        # consome tudo até {% endcomment %}
        parser.parse_statements(["name:endcomment"], drop_needle=True)  # pyright: ignore[reportArgumentType]

        # retorna "nada"
        return nodes.Const("").set_lineno(lineno)
