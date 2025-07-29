from __future__ import annotations

import zlib

from maxml.logging import logger

logger = logger.getChild(__name__)


class Namespace(object):
    """The Namespace class represents an XML namespace"""

    _prefix: str = None
    _uri: str = None
    _promoted: bool = False

    def __init__(self, prefix: str, uri: str):
        """Initialize the Namespace class"""

        if not isinstance(prefix, str):
            raise TypeError("The 'prefix' argument must have a string value!")

        self._prefix = prefix

        if not isinstance(uri, str):
            raise TypeError("The 'uri' argument must have a string value!")

        self._uri = uri

    def __str__(self) -> str:
        """Return a string representation of the class for debugging purposes."""

        return f"<{self.__class__.__name__}({self._prefix}:{self._uri})>"

    def __repr__(self) -> str:
        """Return a more detailed representation of the class for debugging purposes."""

        return f"<{__name__}.{self.__class__.__name__}({self._prefix}:{self._uri}) object at 0x{hex(id(self))}>"

    @staticmethod
    def stableid(value: str):
        """Generate a stable id for a given string value; this is used with __hash__."""

        if not isinstance(value, str):
            raise TypeError("The 'value' argument must have a string value!")

        return zlib.crc32(value.encode()) & 0xFFFFFFFF

    def __hash__(self) -> int:
        """Generate a stable hash value for a Namespace with a given prefix and URI."""

        return self.stableid(self._prefix) + self.stableid(self._uri)

    def __eq__(self, other: Namespace) -> bool:
        """Support comparing Namespace instances by determining if the prefix and URI
        match, allowing copies of Namespace instances to compare as equal even if they
        are distinctly different copies in memory."""

        logger.debug(
            "%s.__eq__(self: %s, other: %s)",
            self.__class__.__name__,
            self,
            other,
        )

        if not isinstance(other, Namespace):
            return False

        if self.prefix != other.prefix:
            return False

        if self.uri != other.uri:
            return False

        return True

    @property
    def prefix(self) -> str:
        """Return the prefix held by the Namespace."""

        return self._prefix

    @property
    def uri(self) -> str:
        """Return the URI held by the Namespace."""

        return self._uri

    def copy(self) -> Namespace:
        """Create an independent copy of the current Namespace instance."""

        return Namespace(prefix=self.prefix, uri=self.uri)

    @property
    def promoted(self) -> bool:
        """Return the promoted status of the Namespace instance as set or unset through
        the 'promote' and 'unpromote' helper methods."""

        return self._promoted

    @promoted.setter
    def promoted(self, promoted: bool):
        """Support setting the promoted value via the property accessor."""

        if not isinstance(promoted, bool):
            raise TypeError("The 'promoted' argument must have a boolean value!")

        self._promoted = promoted

    def promote(self) -> Namespace:
        """Mark the current Namespace instance as having been 'promoted' which allows
        it to be listed before any attributes on the Element it is associated with; as
        this method returns a reference to 'self' it may be chained with other calls."""

        self._promoted = True

        return self

    def unpromote(self) -> Namespace:
        """Mark the current Namespace instance as having been 'unpromoted' preventing it
        from being listed before any attributes on the Element it is associated with; as
        this method returns a reference to 'self' it may be chained with other calls."""

        self._promoted = False

        return self
