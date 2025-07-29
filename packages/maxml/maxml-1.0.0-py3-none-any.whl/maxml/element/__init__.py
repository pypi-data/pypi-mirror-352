from __future__ import annotations

from maxml.namespace import Namespace
from maxml.logging import logger

from hybridmethod import hybridmethod


logger = logger.getChild(__name__)


class Element(object):
    """The Element class represents an XML element"""

    _name: str = None
    _prefix: str = None
    _namespaces: set[Namespace] = set()
    _attributes: dict[str, str] = None
    _text: str = None
    _parent: Element = None
    _children: list[Element] = None
    _mixed: bool = False

    @hybridmethod
    def register_namespace(self, prefix: str, uri: str):
        """Supports registering namespaces globally for the module or per instance
        depending on whether the method is called on the class directly or whether it is
        called on a specific instance of the class.

        If a namespace is registered globally for the module, the registered namespaces
        become available for use by any instance of the class created within the program
        after that point. This is especially useful for widely used XML namespaces which
        obviates the need to re-register these widely used namespaces for each instance.

        If there are namespaces which are specific to a document that is being created
        and that won't be used elsewhere in the program, then those namespaces can be
        registered on the specific class instance within which they will be used without
        affecting the global list of registered namespaces.

        Each namespace consists of a prefix which can be used to prefix element names
        and the URI associated with that namespace prefix.

        For example, the 'rdf' prefix is associated with the following canonical URI:
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

        This would be registered globally by calling:

            Element.register_namespace(
                prefix="rdf",
                uri="http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            )

        Or this would be registered on a specific instance of the class by calling:

            instance.register_namespace(
                prefix="rdf",
                uri="http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            )

        Where 'instance' was the variable referencing the desired instance of the class.
        """

        logger.debug("%s.register_namespace(prefix: %s, uri: %s)", self, prefix, uri)

        if not isinstance(prefix, str):
            raise TypeError("The 'prefix' argument must have a string value!")

        if not isinstance(uri, str):
            raise TypeError("The 'uri' argument must have a string value!")

        for namespace in self._namespaces:
            if namespace.prefix == prefix:
                if namespace.uri == uri:
                    logger.warning(
                        " >>> The '%s' namespace has already been registered..."
                        % (prefix)
                    )
                    break
                else:
                    raise ValueError(
                        "The '%s' namespace has already been registered with a different URI!"
                        % (prefix)
                    )
        else:
            if namespace := Namespace(prefix=prefix, uri=uri):
                self._namespaces.add(namespace)

    def __init__(
        self,
        name: str,
        text: str = None,
        namespace: Namespace | str = None,
        mixed: bool = True,
        parent: Element = None,
        **attributes,
    ):
        """Support initializing a new XML element with a required element name, optional
        text content, an optional parent element reference (which must be set for child
        nodes) and an optional namespace definition provided either as a Namespace class
        instance containing the matching prefix and associated namespace URI or as a URI
        given as a string which corresponds to the prefix used in the element's name."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")
        elif len(name := name.strip()) == 0:
            raise ValueError("The 'name' argument must have a non-empty string value!")

        if not ":" in name:
            raise ValueError(
                "The 'name' argument must contain a ':' separator character between the namespace and tag name!"
            )

        prefix: str = None

        if ":" in name:
            (prefix, basename) = name.split(":", maxsplit=1)

        self._prefix: str = prefix

        self._name: str = basename

        if parent is None:
            pass
        elif isinstance(parent, Element):
            self._parent: Element = parent
        else:
            raise TypeError(
                "The 'parent' argument must reference an Element class instance!"
            )

        if text is None:
            pass
        elif isinstance(text, str):
            self._text: str = text
        else:
            raise TypeError(
                "The 'text' argument, if specified, must have a string value!"
            )

        self._namespaces: set[Namespace] = set()

        if namespace is None:
            for namespace in self.__class__._namespaces:
                if namespace.prefix == prefix:
                    break
            else:
                raise ValueError(
                    f"No namespace has been registered for the '{prefix}' prefix associated with the '{name}' element!"
                )

            self._namespaces.add(namespace.copy().promote())
        elif isinstance(uri := namespace, str):
            for namespace in self.__class__._namespaces:
                if namespace.uri == uri:
                    break
            else:
                namespace = Namespace(prefix=prefix, uri=uri)

            self.__class__._namespaces.add(namespace)

            self._namespaces.add(namespace.copy().promote())
        elif isinstance(namespace, Namespace):
            self.__class__._namespaces.add(namespace)

            self._namespaces.add(namespace.copy().promote())
        else:
            raise TypeError(
                "The 'namespace' argument does not contain a valid namespace!"
            )

        self._attributes: dict[str, str] = attributes or {}

        self._children: list[Element] = []

        if isinstance(mixed, bool):
            self._mixed = mixed
        else:
            raise TypeError("The 'mixed' argument must have a boolean value!")

        logger.debug(
            "%s.__init__(name: %s, text: %s, parent: %s, namespace: %s, kwargs: %s) => depth %d",
            self.__class__.__name__,
            name,
            text,
            parent,
            namespace,
            attributes,
            self.depth,
        )

    @property
    def depth(self) -> int:
        """Return the depth of the current Element where the root Element has a depth of
        zero (0) and all nested Elements have a depth that increases by one (1) for each
        level of nesting between the root node and the current Element node."""

        depth: int = 0

        if self.parent:
            depth = 1 + self.parent.depth
        else:
            depth = 0

        return depth

    @property
    def prefix(self) -> str | None:
        """Return the current Element node's namespace prefix."""

        return self._prefix

    @property
    def name(self) -> str:
        """Return the current Element node's name without its namespace prefix."""

        return self._name

    @property
    def fullname(self) -> str:
        """Return the current Element node's full name, combining the elements namespace
        prefix and name."""

        if self._prefix:
            return f"{self._prefix}:{self._name}"
        else:
            return self._name

    @property
    def namespace(self) -> Namespace | None:
        """Return the current Element node's namespace, if the Element has a prefix and
        if a matching namespace has been registered prior to or at the time the Element
        was created. If no matching namespace can be found, None will be returned."""

        namespace: Namespace = None

        if self._prefix:
            for namespace in self.__class__._namespaces:
                if namespace.prefix == self._prefix:
                    break
            else:
                namespace = None

        logger.debug(
            "%s.namespace(%s) => %s",
            self.__class__.__name__,
            self.fullname,
            namespace.prefix if namespace else "?",
        )

        return namespace

    @property
    def namespaces(self) -> set[Namespace]:
        """Return the namespaces associated with the current Element and its parent"""

        namespaces: set[Namespace] = set(self._namespaces)

        logger.debug(
            "%s.namespaces(%s) => %s",
            self.__class__.__name__,
            self.fullname,
            [n.prefix for n in namespaces],
        )

        if self.parent:
            for namespace in self.parent.namespaces:
                namespaces.add(namespace)

        if namespace := self.namespace:
            namespaces.add(namespace)

        logger.debug(
            "%s.namespaces(%s) => %s",
            self.__class__.__name__,
            self.fullname,
            [n.prefix for n in namespaces],
        )

        return namespaces

    @property
    def namespaced(self) -> set[Namespace]:
        """Return the namespaces associated with the current Element and its children"""

        namespaces: list[Namespace] = set()

        inherited: set[Namespace] = self.parent.namespaces if self.parent else set()

        # logger.debug("%s.namespaced(%s) => inherited => %s", self.__class__.__name__, self.fullname, [n.prefix for n in inherited])

        if namespace := self.namespace:
            if self.parent is None:
                namespaces.add(namespace)
            elif not namespace in inherited:
                namespaces.add(namespace)

        if self.depth > 0:
            for child in self.children:
                if namespace := child.namespace:
                    if self.parent is None or not namespace in inherited:
                        namespaces.add(namespace)

        # logger.debug("%s.namespaced(%s) => current => %s", self.__class__.__name__, self.fullname, [n.prefix for n in namespaces])

        return namespaces

    @property
    def parent(self) -> Element | None:
        """Return current Element node's parent Element or None if its the root node."""

        return self._parent

    @property
    def root(self) -> Element:
        """Return the root Element of the tree, callable from any other Element node."""

        if self.parent is None:
            return self

        return self.parent.root

    @property
    def children(self) -> list[Element]:
        """Return a copy of the list of children associated with the current Element."""

        return list(self._children)

    @property
    def empty(self) -> bool:
        """Determine if the current Element is considered empty or not, as determined by
        the absence of any children, returning True for Elements without children."""

        return len(self._children) == 0

    @property
    def attributes(self) -> dict[str, str]:
        """Return a copy of the dictionary of attributes held by the current Element."""

        return dict(self._attributes)

    def set(self, name: str, value: object) -> Element:
        """Supports setting a named attribute value on the current Element; if the named
        attribute already exists, its value will be overwritten."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        if not (isinstance(value, object) and hasattr(value, "__str__")):
            raise TypeError(
                "The 'value' argument must have a value that can be cast to a string!"
            )

        self._attributes[name] = value

        return self

    def get(self, name: str, default: object = None) -> object | None:
        """Supports getting the value of a named attribute on the Element if the named
        attribute exists, returning the optional default value if the named attributes
        does not exist or returning None otherwise."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        if name in self._attributes:
            return self._attributes[name]

        return default

    def unset(self, name: str) -> Element:
        """Supports unsetting a named attribute on the Element."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        if name in self._attributes:
            del self._attributes[name]

        return self

    def subelement(self, name: str, **kwargs) -> Element:
        """Create a child Element under the current Element."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        element = Element(name=name, parent=self, **kwargs)

        self._children.append(element)

        if self.parent:
            if namespace := element.namespace:
                self._namespaces.add(namespace)

        return element

    @property
    def text(self) -> str | None:
        """Return the text value of the current Element if present or None otherwise."""

        return self._text

    @text.setter
    def text(self, text: str):
        """Supports setting the text property of the current Element by assigning a
        string value, or nullifying the text value if needed by assinging None."""

        if text is None:
            self._text = None
        elif isinstance(text, str):
            self._text = text
        else:
            raise TypeError(
                "The 'text' property must be assigned to a string value or None!"
            )

    @property
    def mixed(self) -> bool:
        """Return whether mixed content mode is enabled or not; by default it is."""

        return self._mixed

    def _parse_path(self, path: str) -> list[str]:
        """Supports parsing the search path into its consistuent parts"""

        if not isinstance(path, str):
            raise TypeError("The 'path' argument must have a string value!")

        # The root node can be referenced via '$', '.' or '//' and to allow removal of
        # a potentially trailing '/' we first need to replace '//' with '.'
        if path == "//":
            path = "."

        # Remove any potentially trailing '/' from the search path so that it doesn't
        # result in an additional empty search path component when splitting below
        path = path.rstrip("/")

        # The '//' prefix can also be used to indicate the root node
        if path.startswith("//"):
            path = "." + path[2:]

        # The '$' prefix can also be used to indicate the root node
        elif path.startswith("$"):
            path = "." + path[1:]

        return path.split("/")

    def find(self, path: str) -> Element | None:
        """Supports finding the matching element nested within the current Element as
        specified by the path which consists of one or more prefixed names and optional
        wildcard characters."""

        if not isinstance(path, str):
            raise TypeError("The 'path' argument must have a string value!")

        current: Element = self

        if (count := len(parts := self._parse_path(path))) > 0:
            root: Element = self.root

            found: bool = False

            for index, part in enumerate(parts, start=1):
                # print(index, part)

                if part == ".":
                    # print(f" >>> matched root ({part}) => {root.fullname}")
                    current = root

                    if count == index:
                        found = True
                        break
                else:
                    # print(f" >>> checking children for ({part})")

                    for child in current.children:
                        # print(f" >>> checking child ({child.fullname})")

                        if part == "*" or child.fullname == part:
                            # print(f" >>> matched child ({part})")

                            current = child

                            if count == index:
                                found = True
                                break

            if found is False:
                current = None

        return current

    def findall(self, path: str) -> list[Element]:
        """Supports finding the matching elements nested within the current Element as
        specified by the path which consists of one or more prefixed names and optional
        wildcard characters."""

        if not isinstance(path, str):
            raise TypeError("The 'path' argument must have a string value!")

        found: list[Element] = []

        current: Element = self

        if (count := len(parts := self._parse_path(path))) > 0:
            root: Element = self.root

            for index, part in enumerate(parts, start=1):
                # print(index, part)

                if part == ".":
                    current = root

                    if index == count:
                        found.append(child)
                else:
                    for child in current.children:
                        if part == "*" or child.fullname == part:
                            current = child

                            if index == count:
                                found.append(child)

        return found

    def tostring(
        self,
        pretty: bool = False,
        indent: str | int = None,
        encoding: str = None,
        **kwargs,
    ) -> str | bytes:
        """Supports serializing the current Element tree to a string or to a bytes array
        if a string encoding, such as 'UTF-8', is specified."""

        if not isinstance(pretty, bool):
            raise TypeError("The 'pretty' argument must have a boolean value!")

        if indent is None:
            indent = 2

        if isinstance(indent, (int, str)):
            if isinstance(indent, int) and indent > 0:
                indent = " " * indent
            elif isinstance(indent, str) and len(indent) > 0:
                pass
            else:
                indent = ""
        else:
            raise TypeError(
                "The 'indent' argument, if specified, must have an integer or string value!"
            )

        if encoding is None:
            pass
        elif not isinstance(encoding, str):
            raise TypeError("The 'encoding' argument must have a string value!")

        def stringify(
            element: Element,
            depth: int,
            pretty: bool = False,
            indent: str = None,
            **kwargs,
        ) -> str:
            """Convert the current XML element to a serialized XML string, recursively
            iterating downward through the tree and all of its children."""

            if indent is None:
                indent = ""

            newline: bool = False

            # Begin the element tag
            string: str = f"<{element.fullname}"

            # Add any promoted namespaces (those which should proceed any attributes)
            count = len(element.namespaced)
            for index, namespace in enumerate(element.namespaced, start=1):
                if not namespace.promoted:
                    continue

                if pretty and count > 1 and (newline or (index > 1 and index <= count)):
                    string += f"\n{indent * (depth + 2)}"

                string += f' xmlns:{namespace.prefix}="{namespace.uri}"'

            # Add any attributes
            count = len(element.attributes)
            for index, (key, value) in enumerate(element.attributes.items(), start=1):
                if pretty and count > 1 and index >= 1 and index <= count:
                    string += f"\n{indent * (depth + 2)}"
                    newline = True

                string += f' {key}="{value}"'

            # Add any non-promoted namespaces (those which can follow any attributes)
            count = len(element.namespaced)

            if count > 2:
                newline = True

            for index, namespace in enumerate(element.namespaced, start=1):
                if namespace.promoted:
                    continue

                if pretty and count > 1 and (newline or (index > 1 and index <= count)):
                    string += f"\n{indent * (depth + 2)}"

                string += f' xmlns:{namespace.prefix}="{namespace.uri}"'

            # Close an empty element tag if the element lacks text content and children
            if element.text is None and element.empty is True:
                string += f"/>"

            # Otherwise include the element's optional text and children
            else:
                string += f">"

                if not element.mixed and (element.text and element.children):
                    raise ValueError(
                        "The current XML element cannot be serialized as mixed content mode is not enabled, but both node text and children have been specified; please either enable mixed mode or adjust the element's node contents."
                    )

                # Include the element's text content, if any
                if element.text and (element.mixed or not element.children):
                    string += element.text

                # Include the element's children, if any
                if element.children and (element.mixed or not element.text):
                    for child in element.children:
                        if pretty:
                            string += f"\n{indent * (depth + 1)}"

                        string += stringify(
                            element=child,
                            depth=(depth + 1),
                            pretty=pretty,
                            indent=indent,
                            **kwargs,
                        )

                    if pretty:
                        string += f"\n{indent * (depth)}"

                string += f"</{element.fullname}>"

            return string

        string = stringify(
            element=self,
            depth=0,
            pretty=pretty,
            indent=indent,
            **kwargs,
        )

        string = string.strip()

        if encoding:
            string = string.encode(encoding)

        return string
