from pytest_plone import fixtures_factory
from rss_provider.testing import INTEGRATION_TESTING


pytest_plugins = ["pytest_plone"]


globals().update(fixtures_factory(((INTEGRATION_TESTING, "integration"),)))
