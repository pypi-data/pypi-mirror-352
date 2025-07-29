import pytest
import maxml


@pytest.fixture(scope="module", name="namespace")
def test_maxml_namespace_fixture():
    """Create an instance of the maxml.Namespace class for use throughout the tests"""

    namespace = maxml.Namespace(prefix="my", uri="http://namespace.example.org/my")

    # Ensure that the namespace object's type is as expected
    assert isinstance(namespace, maxml.Namespace)

    return namespace


def test_maxml_namespace_prefix(namespace: maxml.Namespace):
    """Check the namespace's prefix property"""

    assert isinstance(namespace.prefix, str)
    assert namespace.prefix == "my"


def test_maxml_namespace_uri(namespace: maxml.Namespace):
    """Check the namespace's URI property"""

    assert isinstance(namespace.uri, str)
    assert namespace.uri == "http://namespace.example.org/my"


def test_maxml_namespace_promoted(namespace: maxml.Namespace):
    """Check the namespace's promoted property"""

    assert isinstance(namespace.promoted, bool)

    # By default a namespace's 'promoted' property is False
    assert namespace.promoted is False

    # Call the 'promote' helper method to mark the namespace as promoted
    promoted = namespace.promote()

    # The 'promote' helper method returns a reference to self, so ensure the value is as
    # expected in both the return type and identity
    assert isinstance(promoted, maxml.Namespace)
    assert namespace is promoted

    # After calling the 'promote' method we expect the 'promoted' property to be True
    assert namespace.promoted is True


def test_maxml_namespace_copy(namespace: maxml.Namespace):
    """Check the namespace's copy functionality which creates a new Namespace instance
    from the current namespace instance using the same prefix and URI."""

    # Copy the existing namespace
    namespace_copy = namespace.copy()

    # Ensure that the copy of the namespace has the expected type
    assert isinstance(namespace_copy, maxml.Namespace)

    # Ensure that the prefix and URI values were copied successfully
    assert namespace_copy.prefix == namespace.prefix
    assert namespace_copy.uri == namespace.uri

    # Ensure that the copy has a different identity to the original
    assert not namespace_copy is namespace
    assert not id(namespace_copy) == id(namespace)

    # However, the Namespace class overrides the __hash__ method so that a copy produces
    # the same hash as the original, which ensures that copies are seen as the same for
    # use in lists, tuples, sets, etc., where we do not want to duplicate the namespaces
    assert hash(namespace_copy) == hash(namespace)

    # Create a test set
    test_namespaces_set = set()

    # Ensure that the set is initial empty as we would expect it to be
    assert len(test_namespaces_set) == 0

    # Add the original namespace to the set
    test_namespaces_set.add(namespace)

    # Ensure that the set now reflects the addition of the original namespace
    assert len(test_namespaces_set) == 1

    # Now ensure that both the original and the copy report as being in the set, even
    # though only the original was added to the set; because __hash__ was overridden
    # both report as being in the set; this ensures namespaces cannot be duplicated
    assert namespace in test_namespaces_set
    assert namespace_copy in test_namespaces_set

    # Just to be sure, attempt to add the namespace copy to the set; this now relies on
    # the set class' internal checking of uniqueness, which again because __hash__ was
    # overridden should prevent the copy from being added to the set as __hash__ on both
    # the original and the copy reports the same value
    test_namespaces_set.add(namespace_copy)

    # Ensure that the set still contains just one value
    assert len(test_namespaces_set) == 1

    # Ensure that the set still only contains the original namespace via identity checks
    namespace_set_item = test_namespaces_set.pop()
    assert isinstance(namespace_set_item, maxml.Namespace)
    assert id(namespace_set_item) == id(namespace)
    assert not id(namespace_set_item) == id(namespace_copy)


def test_maxml_namespace_copy_and_promotion(namespace: maxml.Namespace):
    # Mark the original namespace as being un-promoted, removing its promoted status
    namespace.unpromote()

    # Ensure the original namespace instance now reflects the expected promoted status
    assert namespace.promoted is False

    # Create a copy of the namespace, this time to promote it while leaving the original
    # namespace instance unaffected by the change in promotion status
    namespace_copy = namespace.copy().promote()

    # Ensure that the copy of the namespace has the expected type
    assert isinstance(namespace_copy, maxml.Namespace)

    # Ensure that the copy of the namespace has been marked as promoted
    assert namespace_copy.promoted is True

    # Ensure that the original still reflects its non-promoted status demonstrating that
    # the copy and the original are independent objects unaffected by the other's state
    assert namespace.promoted is False
