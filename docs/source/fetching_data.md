# Fetching Release and Collection data

Note that the examples in this chapter are shown using example Python code with `print` statements to show the results and require an existing [Client object](quickstart.md).

Using the [Python REPL is another way to test and review data](fetching_data_repl.md) and information available using the Discogs API.

Most data about releases can be queried without having to authenticate using your [Client object](quickstart.md).  Other data including search, querying the records in your collection, or fetching album art requires authentication.  See the [Authentication section](https://github.com/joalla/discogs_client/blob/master/docs/source/authentication.md) for more information.

## Release Data

Almost all data available on a Release page on the Discogs website is available using the `python3-discogs-client` library. If you were to run `dir()` on the `release` object, you would see the following list of all objects available to query, where 20017387 is the release ID.   Some common examples are shown below.

```
# Authenticate using your Client object
d = discogs_client.Client(config.agent, user_token=config.my_token)

print(dir(d.release(20017387)))

['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_known_invalid_keys', 'artists', 'changes', 'client', 'companies', 'country', 'credits', 'data', 'data_quality', 'delete', 'fetch', 'formats', 'genres', 'id', 'images', 'labels', 'marketplace_stats', 'master', 'notes', 'refresh', 'save', 'status', 'styles', 'thumb', 'title', 'tracklist', 'url', 'videos', 'year']
```

### Artists

```
print(d.release(20017387).artists[0].name, type(d.release(1443762).artists))
```
returns a list of Artists associated with the release:

```
Chvrches <class 'list'>
```

This returns a list as some releases have multiple artists:

```
[<Artist 2672269 'Poliça'>, <Artist 4771951 'Stargaze (4)'>] Music For The Long Emergency
```

Data returns a dictionary including the URL to the page for the given release:

```
print(d.release(20017387).data)
```

```
{'id': 20017387, 'resource_url': 'https://api.discogs.com/releases/20017387'}
```

### Formats

Formats returns a list of dictionaries that includes the kind of release, such as CD, Vinyl, and any other special properties of the release:

```
print(d.release(20017387).formats)
```

```
[{'name': 'Vinyl', 'qty': '1', 'text': 'Red Transparent', 'descriptions': ['LP', 'Album']}]
```

### Genres 

Genres returns a list of genres associated with the release:

```
print(d.release(20017387).genres)
```

```
['Electronic', 'Pop']
```

### Images

Images returns a list of all images and its URL associated with the release.  You must be authenticated to get the image URL.  The first image is is the primary image found on the Release page:

```
print(d.release(20017387).images[0])
```

```
{'type': 'primary', 'uri': 'https://img.discogs.com/XbUkIoS6p-yb9U36xSKethiXs0U=/fit-in/600x600/filters:strip_icc():format(jpeg):mode_rgb():quality(90)/discogs-images/R-20017387-1631064590-2485.jpeg.jpg', 'resource_url': 'https://img.discogs.com/XbUkIoS6p-yb9U36xSKethiXs0U=/fit-in/600x600/filters:strip_icc():format(jpeg):mode_rgb():quality(90)/discogs-images/R-20017387-1631064590-2485.jpeg.jpg', 'uri150': 'https://img.discogs.com/tbjnf4pVYhNvxNRDqZWrXtkKZcc=/fit-in/150x150/filters:strip_icc():format(jpeg):mode_rgb():quality(40)/discogs-images/R-20017387-1631064590-2485.jpeg.jpg', 'width': 600, 'height': 600}
```

### Tracklist

Tracklist returns a list of tracks and track position on the album associated with the release:

```
print(d.release(20017387).tracklist)
```

```
[<Track 'A1' 'Asking For A Friend'>, <Track 'A2' 'He Said She Said'>, <Track 'A3' 'California'>, <Track 'A4' 'Violent Delights'>, <Track 'A5' 'How Not To Drown '>, <Track 'B1' 'Final Girl'>, <Track 'B2' 'Good Girls'>, <Track 'B3' 'Lullabies'>, <Track 'B4' 'Nightmares'>, <Track 'B5' "Better If You Don't">]
```

```
print(d.release(20017387).tracklist[0].title)
```

```
Asking For A Friend
```

## Collection Data

TBA
