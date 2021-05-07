# Quickstart

## Instantiating the client object

```python
import discogs_client
d = discogs_client.Client('ExampleApplication/0.1')
```

The string passed into the `Client` class is your User-Agent. A User-Agent is
required for Discogs API requests, as it identifies your application to the
Discogs servers.

There are more parameters the `Client` class accepts on instantiation; please
refer to the [authentication chapter](authentication.md) for more details.

Once instantiated, you can either start making requests to endpoints that do not
require authentication, or you can authenticate and make requests to a wider
range of endpoints.

```python
release = d.release(1293022)
print(release.title)
artists = release.artists
```

As you can see, once you fetch data from an endpoint, you can call various
properties and methods on those objects.


## Searching

Note that for searching Discogs via the API [you need to be an authenticated
user](authentication.md) already.

Simple example:

```python
results = d.search('Can I borrow a feeling?')
```

The search method allows for all of the parameters that the raw Discogs API
allows. A full list of available parameters [is found
here.](http://www.discogs.com/developers/#page:database,header:database-search)

Examples using parameters:

```python
results = d.search('Can I borrow a feeling?', type='release')
results = d.search('Can I borrow a feeling?', type='release,master')
results = d.search('Can I borrow a feeling?', artist='Kirk', type='release')
results = d.search('Can I borrow a feeling?', genre='Hip Hop')
```

The `results` object is a paginated list, so you need to specify which page of
results to view, like so:

```python
print(results.page(1))
```


## Most other objects

Objects contain many callable properties. Some examples are shown in the
[fetching data section](fetching_data.md). For a full list of properties, call
the Python `dir()` function with the object as a parameter.

Also look into the documentation of the models module at
{mod}`discogs_client.models`, to find out what properties are available.

Not all information available in the API response is mapped out, so if you need
more information, you can look in the `data` property of the Release object:

```python
release = d.release(1)
release.data.keys()
```

