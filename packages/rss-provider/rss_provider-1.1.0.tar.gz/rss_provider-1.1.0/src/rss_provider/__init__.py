"""Init and utils."""

from zope.i18nmessageid import MessageFactory


__version__ = "1.1.0"
import logging

PACKAGE_NAME = "rss_provider"

_ = MessageFactory("rss_provider")

logger = logging.getLogger("rss_provider")
