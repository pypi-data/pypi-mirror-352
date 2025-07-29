# MaXML: A Pure Python XML Serializer

The MaXML library provides a streamlined pure Python XML serializer.

### Requirements

The MaXML library has been tested with Python 3.10, 3.11, 3.12 and 3.13. The library is
not compatible with Python 3.9 or earlier.

### Installation

The MaXML library is available from PyPI, so may be added to a project's dependencies
via its `requirements.txt` file or similar by referencing the MaXML library's name,
`maxml`, or the library may be installed directly into your local runtime environment
using `pip` via the `pip install` command by entering the following into your shell:

	$ pip install maxml

### Example Usage

To use the MaXML library, import the library's and begin creating your XML document:

```python
import maxml

root = maxml.Element(name="my:node", namespace="http://namespace.example.org/my")

child = root.subelement(name="my:child-node")

child.set("my-attribute", "my-attribute-value")

child.text = "testing"

root.tostring(pretty=True)
```

The above example will result in the following XML:

```xml
<my:node xmlns:my="http://namespace.example.org/my">
  <my:child-node my-attribute="my-attribute-value">testing</my:child-node>
</my:node>
```

### Methods & Properties

The MaXML library provides two main classes for use in creating and serializing XML, the
`Elements` class that is used to represent nodes in the XML document tree along with any
attributes those nodes have, their associated namespaces, any text content and children,
and the `Namespace` class for holding information about namespaces.

The classes and their methods and properties are listed below:

#### Element Class

The `Element` class constructor `Element(...)` takes the following arguments:

 * `name` (`str`) – The required `name` argument sets the prefixed name of the element.

 * `text` (`str`) – The optional `text` argument can be used to specify the text content
	of the element; alternatively it can be set later via the `text` property.

 * `namespace` (`Namespace` | `str`) – The optional `namespace` argument can be used to
	specify the namespace for the element while it is being created; the namespace can
	either be specified as the URI that corresponds with the prefix specified as part of
	the element's name, or can be a reference to a `Namespace` class instance that holds
	the corresponding `prefix` and matching `URI`. If the matching namespace has already
	been registered before the element is created via the class' `register_element()`
	method, then it is not necessary to specify a `namespace` argument when an element
	that references that namespace (via its `name` prefix) is created.

 * `mixed` (`bool`) – The optional `mixed` argument can be used to override the default
	mixed-content mode of the element; by default each element allows mixed-content
	which means that the element can contain both text content and children; if an
	element should only be allowed to contain text content or children, then
	`mixed` can be set to `False` during the construction of the element, which will
	then prevent both content types from being serialized and will instead result in an
	error being raised.

 * `parent` (`Element`) – The optional `parent` property is used internally by the
	library when sub-elements are created to set the appropriate parent reference; this
	property should not be set manually unless one is conformable with the possible
	side-effects that may occur.

The `Element` class provides the following methods:

 * `register_namespace(prefix: str, uri: str)` – The `register_namespace()`  method
	supports registering namespaces globally for the module or per instance depending
	on whether the method is called on the class directly or whether it is called on a
	specific instance of the class.

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

	```python
	from maxml import Element
	
	Element.register_namespace(
	  prefix="rdf",
	  uri="http://www.w3.org/1999/02/22-rdf-syntax-ns#",
	)
	```

	Or this would be registered locally on an instance of the class before its use by a
	sub-element by calling:

	```python
	from maxml import Element
	
	element = Element(name="my:test", namespace="http://namespace.example.org/my")
	
	element.register_namespace(
	  prefix="rdf",
	  uri="http://www.w3.org/1999/02/22-rdf-syntax-ns#",
	)
	```

	Where `instance` was the variable referencing the desired instance of the class.

 * `set(name: str, value: object)` (`Element`) – The `set()` supports setting a named
	attribute value on the current element; if the named attribute already exists, its
	value is overwritten. The `set()` method returns a reference to `self` so it may be
	chained with other calls on the element.

 * `get(name: str, default: object = None)` (`object` | `None`) – The `get()` supports
	getting the value of a named attribute on the Element if the named attribute exists,
	returning the optional `default` value if the named attributes does not exist or if
	the `default` value has not been specified, returning `None` otherwise.

 * `unset(name: str)` (`Element`) – The `set()` supports unsetting a named attribute on
	the element. The `unset()` method returns a reference to `self` so it may be chained
	with other calls on the element.

 * `subelement(name: str, **kwargs)` (`Element`) – The `subelement()` method creates a
	child element nested under the current element. It requires a `name` and optionally
	accepts all of the other arguments that the `Element` class constructor accepts as
	documented above. When a child element is created, its parent is automatically set
	to the element it is nested under. The `subelement()` method returns a reference to
	the newly created element, thus other calls on that element may be chained.

 * `find(path: str)` (`Element` | `None`) – The `find()` method can be used to find the
	matching element nested within the current element as specified by the element path
	which consists of one or more prefixed names and optional wildcard characters.
	
	The path to the element we wish to find can be specified from the root node of the
	tree by starting the path with the "//" marker which indicates the root node, or the
	path can be specified as a relative path by omitting this, which will result in the
	search starting at the current element node. The path should be specified with the
	name of the element at each level of the nesting that should be matched against to
	reach the desired node; each element node name should be separated by a single "/"
	character, and if any node name could be matched as part of the search the wildcard
	character "*" can be used in place of an element node name.

 * `findall(path: str)` (`list[Element]`) – The `findall()` method can be used to find
	the matching elements nested within the current element as specified by the element
	path which consists of one or more prefixed names and optional wildcard characters.
	
	The `findall()` method uses the same search path format as the `find()` method
	described above, the only difference being that if multiple elements are found at
	the end of the search, all matching elements will be returned instead of the first
	match found as is the case with the `find` method.

 * `tostring(pretty: bool = False, indent: str | int = None, encoding: str = None)` –
	The `tostring()` method supports serializing the current element tree to a string,
	or to a bytes array if a string encoding, such as 'UTF-8' is specified.
	
	To create a 'pretty' printed string, set the `pretty` argument to `True` and set an
	optional indent, which by default is set to two spaces per level of indentation. To
	set the indent level to 1 or more spaces, set `indent` to a positive integer value
	of the number of spaces that should be used for the indentation per level of nesting
	or to use a different whitespace character, such as a tab, set the `indent` value to
	a tab character using the escape sequence for a tab, `"\t"`.
	
	To have the method return an encoded `bytes` sequence instead of a unicode string,
	set the optional `encoding` argument to a valid string encoding, such as `"UTF-8"`.

The `Element` class provides the following properties:

 * `prefix` (`str`) – The `prefix` property returns the prefix portion of the element's
	tag full name, for example `my` from `my:test`.

 * `name` (`str`) – The `name` property getter returns the name portion of the element's
	tag full name, for example `test` from `my:test`.

 * `fullname` (`str`) – The `fullname` property returns the full name of the element's
	tag, for example `my:test`.

 * `namespace` (`Namespace`) – The `namespace` property returns the namespace associated
	with the element, as either registered before the element was created, or created by
	the process of creating the element if the optional `namespace` property was used.

 * `depth` (`int`) – The `depth` property returns depth of the element in the tree.

 * `parent` (`Element` | `None`) – The `parent` property returns the parent, if any, of
	the element; the root node of the tree will not have a parent, while all other
	elements will have an assigned parent, set automatically when a sub-element is made.

 * `children` (`list[Element]`) – The `children` property returns the list of children
	elements associated with the element, if any have been assigned.

 * `attributes` (`dict[str, str]`) – The `attributes` property returns a dictionary of
	the attributes associated with the element, if any have been assigned, where the key
	of each entry is the name of the attribute and the value is its value.

 * `text` (`str` | `None`) – The `text` property returns the text of the element if any
	has been assigned or `None` otherwise.

 * `mixed` (`bool`) – The `mixed` property returns the mixed-content status of the
	element which determines whether the element can have both text content and children
	or if at most it can only have one or the other. By default each element allows both
	content types, but by setting the `mixed` argument on the `Element` constructor to
	`False`, mixed-content mode will be turned-off.

 * `root` (`Element`) – The `root` property returns the root element of the tree from
	anywhere else within the tree.

 * `namespaces` (`set[Namespace]`) – The `namespaces` property returns the full `set` of
	namespaces associated with the element including any inherited from its parents; the
	set can be used to inspect the associated namespaces, but its primary use is to help
	facilitate the serialization of the document.

 * `namespaced` (`set[Namespace]`) – The `namespaced` property returns the unique `set`
	of namespaces associated with the element that have not already been referenced by
	a parent node, thus ensuring only the newly referenced namespaces are introduced in
	the serialized document rather than potentially repeated references to namespaces
	which have already been referenced previously; the set can be used to inspect the
	associated namespaces, but its primary use is to help facilitate the serialization.

#### Namespace Class

The `Namespace` class constructor `Namespace(...)` takes the following arguments:

 * `prefix` (`str`) – The required `prefix` argument sets the namespace prefix.
 * `uri` (`str`) – The required `uri` argument sets the namespace URI.

The `Namespace` class provides the following methods:

 * `copy()` (`Namespace`) – The `copy()` method creates an independent copy of the
	current Namespace instance and returns it.

 * `promote()` (`Namespace`) – The `promote()` marks the current Namespace instance as
	having been 'promoted' which allows it to be listed before any attributes on the
	Element it is associated with; as this method returns a reference to `self` it may
	be chained with other calls.

 * `unpromote()` (`Namespace`) – The `unpromote()` marks the current Namespace instance
	as having been 'un-promoted' preventing it from being listed before any attributes
	on the Element it is associated with; as this method returns a reference to `self`
	it may be chained with other calls.

The `Namespace` class provides the following properties:

 * `prefix` (`str`) – The `prefix` property returns the prefix held by the namespace.
 * `uri` (`str`) – The `uri` property returns the URI held by the namespace.
 * `promoted` (`bool`) – The `promoted` property getter returns the promoted state of the
	Namespace instance as set or unset through the `promote()` and `unpromote()` helper
	methods or via the `promoted` property setter.
 * `promoted` (`bool`) – The `promoted` property setter supports setting the `promoted`
	property value via the property accessor.


### Unit Tests

The MaXML library includes a suite of comprehensive unit tests which ensure that the
library functionality operates as expected. The unit tests were developed with and are
run via `pytest`.

To ensure that the unit tests are run within a predictable runtime environment where all of the necessary dependencies are available, a [Docker](https://www.docker.com) image is created within which the tests are run. To run the unit tests, ensure Docker and Docker Compose is [installed](https://docs.docker.com/engine/install/), and perform the following commands, which will build the Docker image via `docker compose build` and then run the tests via `docker compose run` – the output of running the tests will be displayed:

```shell
$ docker compose build
$ docker compose run tests
```

To run the unit tests with optional command line arguments being passed to `pytest`, append the relevant arguments to the `docker compose run tests` command, as follows, for example passing `-vv` to enable verbose output:

```shell
$ docker compose run tests -vv
```

See the documentation for [PyTest](https://docs.pytest.org/en/latest/) regarding available optional command line arguments.

### Copyright & License Information

Copyright © 2025 Daniel Sissman; licensed under the MIT License.