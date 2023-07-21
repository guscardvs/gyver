# URL

The URL module offers a convenient way of interacting with the different parts of a URL.


## Initialization

You can create a new instance of the URL class by passing a string to the constructor.

```python

from gyver.url import URL
url = URL("https://www.example.com/path?key=value#fragment")
```

## Properties

The URL class has the following properties:

* **`scheme`**: The scheme of the URL (e.g. "http", "https").
* **`netloc`**: The network location of the URL. It includes the hostname and port, as well as the username and password if present.
* **`path`**: The path of the URL.
* **`query`**: The query string of the URL, as a Query object.
* **`fragment`**: The fragment of the URL, as a Fragment object.
* **`port`**: The port of the URL, if present.

## Methods

The URL class has the following methods:

* **`load(val: str)`**

You can use this method to update the URL with a new string. It will update all the properties accordingly.

* **`encode(self, omit_empty_equal: bool = True):`**

This method returns the resolved string representation of the URL. By default, it will append an equal sign to null query parameters. If omit_empty_equal is set to False, null query parameters will be represented by only their name.


* **`add(...)`**

This method allows you to add new elements to the URL. You can add new values to the query, path, fragment or netloc by passing the corresponding arguments.


* **set(...)**

This method allows you to set elements of the URL. You can set new values to the query, path, fragment or netloc by passing the corresponding arguments.


## Sub-classes


The URL class uses the following sub-classes to handle the different parts of the URL:

* **`Query`**: handles the query string of the URL.
* **`Path`**: handles the path of the URL.
* **`Fragment`**: handles the fragment of the URL
* **`Netloc`**: handles the netloc of the URL

## Examples

Here are some examples of how you can use the URL class:

```python

# Create a new URL
url = URL("https://www.example.com/path?key=value#fragment")

# Add a new query parameter
url.add(query={"new_key": "new_value"})

# Set a new path
url.set(path="/new_path")

# Get the encoded string representation of the URL
print(url.encode()) # "https://www.example.com/new_path?key=value&new_key=new_value#fragment"

# Create a new URL
url = URL("https://www.example.com/path?key=value#fragment")

# Add a new netloc
url.add(netloc_obj=Netloc(username="user", host="host", port=8080))

# Change the fragment
url.set(fragment='another')

# Get the resolved string representation
print(url.encode()) # "https://user@host:8080/path?key=value#another"
```