from plone import schema
from plone.dexterity.content import Container
from plone.supermodel import model
from zope.interface import implementer


class IRSSFeed(model.Schema):
    """Dexterity-Schema for RSS Feed"""

    max_title_length = schema.Int(
        title="Maximum Title Length",
        description="Maximum number of characters allowed for titles.",
        required=True,
        default=150,
    )

    max_description_length = schema.Int(
        title="Maximum Description Length",
        description="Maximum number of characters allowed for descriptions.",
        required=True,
        default=400,
    )


@implementer(IRSSFeed)
class RSSFeed(Container):
    """Content-type class for IRSSFeed"""
