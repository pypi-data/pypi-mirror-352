"""Installer for the rss_provider package."""

from pathlib import Path
from setuptools import find_packages
from setuptools import setup


long_description = f"""
{Path("README.md").read_text()}\n
{Path("CONTRIBUTORS.md").read_text()}\n
{Path("CHANGES.md").read_text()}\n
"""


setup(
    name="rss_provider",
    version="1.1.0",
    description="Plone backend addon for volto-rss-provider",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS",
    author="Ziming Yuan",
    author_email="zimingyuan2017@gmail.com",
    url="https://github.com/collective/rss-provider",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/rss_provider",
        "Source": "https://github.com/collective/rss-provider",
        "Tracker": "https://github.com/collective/rss-provider/issues",
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "setuptools",
        "Plone",
        "prettyconf",
        "plone.api",
    ],
    extras_require={
        "test": [
            "pytest-plone>=0.5.0",
            "pytest-cov",
            "pytest",
            "zope.pytestlayer",
            "zest.releaser[recommended]",
            "plone.app.testing[robot]",
            "plone.restapi[test]",
            "collective.MockMailHost",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = rss_provider.locales.update:update_locale
    """,
)
