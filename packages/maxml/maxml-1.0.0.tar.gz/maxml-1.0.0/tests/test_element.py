import pytest
import maxml


@pytest.fixture(scope="module", name="element")
def test_maxml_element_fixture():
    """Create an instance of the maxml.Element class for use throughout the tests"""

    element = maxml.Element(name="my:test", namespace="http://namespace.example.org/my")

    # Ensure that the element object's type is as expected
    assert isinstance(element, maxml.Element)

    return element


def test_maxml_element_class_instantiation(element: maxml.Element):
    """Check that the element class was initialized as expected"""

    # Ensure that the element's name prefix was parsed correctly
    assert element.prefix == "my"

    # Ensure that the element's name was parsed correctly
    assert element.name == "test"

    # Ensure that the element's full name was parsed correctly
    assert element.fullname == "my:test"

    # Ensure that the element's namespace prefix was registered correctly
    assert element.namespace.prefix == "my"

    # Ensure that the element's namespace URI was registered correctly
    assert element.namespace.uri == "http://namespace.example.org/my"

    # Ensure that the root node has no parent
    assert element.parent is None

    # Ensure that the root node has the expected depth
    assert element.root.depth == 0


def test_maxml_check_root(element: maxml.Element):
    """Check that the root property on the root element resolves to itself"""

    assert element.root is element


def test_maxml_check_root_parent(element: maxml.Element):
    """Check that the root note has no parent"""

    assert element.root.parent is None


def test_maxml_add_subelement(element: maxml.Element):
    """Create a sub element and ensure it is created as expected"""

    sub = element.subelement("my:sub")

    # Ensure that the subelement's type is as expected
    assert isinstance(sub, maxml.Element)

    # Ensure that the subelement's name prefix was parsed correctly
    assert sub.prefix == "my"

    # Ensure that the subelement's name was parsed correctly
    assert sub.name == "sub"

    # Ensure that the element's fullname was parsed correctly
    assert sub.fullname == "my:sub"

    # Ensure that the element's namespace prefix was registered correctly
    assert sub.namespace.prefix == "my"

    # Ensure that the element's namespace URI was registered correctly
    assert sub.namespace.uri == "http://namespace.example.org/my"

    # Ensure that the root has the expected depth
    assert sub.depth == 1


def test_maxml_add_subelement_list(element: maxml.Element):
    """Create a sub element and ensure it is created as expected"""

    sub = element.find("my:sub")

    # Ensure that the subelement's type is as expected
    assert isinstance(sub, maxml.Element)

    values: list[str] = [
        "ABC",
        "DEF",
        "XYZ",
    ]

    sequence = sub.subelement("my:seq")

    for index, value in enumerate(values, start=1):
        item = sequence.subelement("my:li")
        item.set("my:index", str(index))
        item.text = value


def test_maxml_children_property_type(element: maxml.Element):
    """Check that the element's children property has the expected type"""

    assert isinstance(element.children, list)


def test_maxml_children_property_count(element: maxml.Element):
    """Check that the element's children list has the expected count"""

    assert len(element.children) == 1


def test_maxml_check_child_parent(element: maxml.Element):
    """Check that the parent of each child is as expected"""

    for child in element.children:
        assert child.parent is element


def test_maxml_set_text(element: maxml.Element):
    """Set text content on the element"""

    # Before any text content is set on the element, the property will have a None value
    assert element.text is None

    # Set text content on the element
    element.text = "text content"


def test_maxml_get_text(element: maxml.Element):
    """Get text content from the element"""

    # Ensure that the property now has the expected value type
    assert isinstance(element.text, str)

    # Ensure that the property now has the expected value
    element.text == "text content"


def test_maxml_clear_text(element: maxml.Element):
    """Set text content on the element"""

    # Clear text content on the element by assigning it to None
    element.text = None

    # Ensure that the property now has the expected value
    assert element.text is None


def test_maxml_set_attributes(element: maxml.Element):
    """Set attributes on the element"""

    # For a newly created element we expect the attributes dictionary to be empty
    assert isinstance(element.attributes, dict)
    assert len(element.attributes) == 0

    # Add two attributes
    element.set("my:about", "information about this element")
    element.set("another", "another attribute")

    # Ensure that the added attributes are reflected in the attributes dictionary count
    assert len(element.attributes) == 2


def test_maxml_get_attributes(element: maxml.Element):
    """Ensure the added attributes can be accessed and have the expected values"""

    # Ensure that the attribute getter returns the expected value
    assert element.get("my:about") == "information about this element"

    # Ensure that the attribute getter returns the expected value
    assert element.get("another") == "another attribute"

    # Ensure that the attributes property returns the expected value
    assert element.attributes == {
        "my:about": "information about this element",
        "another": "another attribute",
    }


def test_maxml_get_attribute_with_default_value(element: maxml.Element):
    """Ensure the added attributes can be accessed and have the expected values"""

    # Ensure that the attribute getter returns the expected value
    assert element.get("my:about") == "information about this element"

    # Ensure that the attribute getter returns the expected value
    assert element.get("another") == "another attribute"

    # Ensure that the attributes property returns the expected value
    assert element.attributes == {
        "my:about": "information about this element",
        "another": "another attribute",
    }


def test_maxml_remove_attribute(element: maxml.Element):
    assert len(element.attributes) == 2

    assert element.attributes == {
        "my:about": "information about this element",
        "another": "another attribute",
    }

    element.unset("my:about")

    assert len(element.attributes) == 1

    assert element.attributes == {
        "another": "another attribute",
    }

    element.get("my:about") is None


def test_maxml_remove_attribute(element: maxml.Element):
    assert len(element.attributes) == 2

    assert element.attributes == {
        "my:about": "information about this element",
        "another": "another attribute",
    }

    element.unset("my:about")

    assert len(element.attributes) == 1

    assert element.attributes == {
        "another": "another attribute",
    }

    element.get("my:about") is None


def test_maxml_check_mixed_content_flag(element: maxml.Element):
    """Check that the mixed content flag is enabled, which is the default status"""

    assert element.mixed is True


def test_maxml_find_functionality(element: maxml.Element):
    """Check that the find functionality works as expected"""

    # Find an element that we know exists specifying a path to the element from the root
    # to the element we wish to find, where the root is marked by "//" and then elements
    # are specified by their names, separated by forward strokes:
    found: maxml.Element = element.find("//my:test/my:sub")

    # Ensure that the element was found; the 'find' method returns None otherwise
    assert isinstance(found, maxml.Element)

    # Ensure that the found element is the one we expect
    assert found.fullname == "my:sub"


def test_maxml_find_functionality_for_non_existing_element(element: maxml.Element):
    """Check that the find functionality works as expected"""

    # Find an element that we know exists specifying a path to the element from the root
    # to the element we wish to find, where the root is marked by "//" and then elements
    # are specified by their names, separated by forward strokes:
    found: maxml.Element = element.find("//my:test/my:does-not-exist")

    # Ensure that the 'find' method returns None when the element cannot be found
    assert found is None


def test_maxml_find_functionality_nested(element: maxml.Element):
    """Check that the find functionality works as expected"""

    # Find an element that we know exists specifying a path to the element from the root
    # to the element we wish to find, where the root is marked by "//" and then elements
    # are specified by their names, separated by forward strokes:
    found: maxml.Element = element.find("//")

    # Ensure that the element was found; the 'find' method returns None otherwise
    assert isinstance(found, maxml.Element)

    # Ensure that the found element is the one we expect
    assert found.fullname == "my:test"

    # Now find an element within the element; in this case we look for my:sub in my:test
    # and the path is specified as a relative path as we do not reference the root "//"
    # at the start of the path, instead we specify the name of the node held under the
    # current node that we wish to find and retrieve
    found: maxml.Element = found.find("my:sub")

    # Ensure that the element was found; the 'find' method returns None otherwise
    assert isinstance(found, maxml.Element)

    # Ensure that the found element is the one we expect
    assert found.fullname == "my:sub"


def test_maxml_namespaces(element: maxml.Element):
    """Check that the namespacing functionality works as expected"""

    # Retrieve the namespaces associated with the root element
    namespaced: set[maxml.Namespace] = element.namespaced

    # Ensure that the returned value is of the expected set type
    assert isinstance(namespaced, set)

    # Ensure that the returned set contains the expected number of values
    assert len(namespaced) == 1

    # Create a Namespace instance referencing the same namespace as the root element
    compare = maxml.Namespace(prefix="my", uri="http://namespace.example.org/my")

    # Ensure various comparison methods to compare namespace equality work as expected
    assert compare in namespaced  # Facilitated by Namespace.__eq__()

    for namespace in namespaced:
        assert namespace == compare  # Facilitated by Namespace.__eq__()]
        assert not id(namespace) == id(compare)  # They are still different objects

    assert namespaced == set([compare])  # Facilitated by Namespace.__hash__()


def test_maxml_tostring(element: maxml.Element, data: callable):
    """Check that the string serialization functionality works as expected"""

    string: str = element.tostring()

    assert isinstance(string, str)

    compare: str = data("examples/example01.xml")

    assert isinstance(compare, str)

    assert string == compare


def test_maxml_tostring_bytes(element: maxml.Element, data: callable):
    """Check that the string serialization functionality works as expected"""

    string: bytes = element.tostring(encoding="UTF-8")

    assert isinstance(string, bytes)

    compare: bytes = data("examples/example01.xml", binary=True)

    assert isinstance(compare, bytes)

    assert string == compare


def test_maxml_tostring_pretty_default(element: maxml.Element, data: callable):
    """Check that the string serialization functionality works as expected"""

    string: str = element.tostring(pretty=True)

    assert isinstance(string, str)

    compare: str = data("examples/example01pretty.xml")

    assert isinstance(compare, str)

    assert string == compare


def test_maxml_tostring_pretty_tab(element: maxml.Element, data: callable):
    """Check that the string serialization functionality works as expected"""

    string: str = element.tostring(pretty=True, indent="\t")  # Use tabs for indents

    assert isinstance(string, str)

    compare: str = data("examples/example01prettytab.xml")

    assert isinstance(compare, str)

    assert string == compare


def test_maxml_fragment_tostring(element: maxml.Element, data: callable):
    """Check that the string serialization functionality works as expected"""

    fragment: maxml.Element = element.find("my:sub")

    assert isinstance(fragment, maxml.Element)

    string: str = fragment.tostring(pretty=True)

    assert isinstance(string, str)

    compare: str = data("examples/example02fragment.xml")

    assert isinstance(compare, str)

    assert string == compare
