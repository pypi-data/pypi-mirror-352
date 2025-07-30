from __future__ import absolute_import


import re

from ._version import __versionstr__

from .attestation import Attestation
from .credential import Credential
from .schema import Schema

_major, _minor, _patch = [
    int(x) for x in re.search(r"^(\d+)\.(\d+)\.(\d+)", __versionstr__).groups()
]
VERSION = __version__ = (_major, _minor, _patch)

__all__ = [
    "Attestation",
    "Credential",
    "Schema"
]
