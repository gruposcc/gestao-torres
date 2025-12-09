__all__ = ["get_notifier", "Notifier"]

from .notifier import Notifier, notifier


def get_notifier() -> Notifier:
    return notifier
