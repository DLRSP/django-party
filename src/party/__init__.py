"""django-party — shared party identity for Django sites."""

__version__ = "0.2.0"
__version_info__ = tuple(
    int(i) if i.isdigit() else i for i in __version__.split(".")
)
__license__ = "MIT"
__title__ = "party"

VERSION = __version_info__
