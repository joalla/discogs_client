# Managing Release and Collection data

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
### Community Details

```python
release = d.release(15343679)
community_details = release.community

print(community_details)
print(community_details.rating)
print(community_details.want)
print(community_details.have)
print(community_details.contributors)
```

```
<CommunityDetails want/have: 34/74>
<Rating avg: 4.5>
34
74
[<User 1053297 'ManikRecs'>, <User 1241908 'neurosis76'>, <User 8867757 'silyn1'>, <User 3410038 'evasstra'>]
```

Additional attributes are also available. Learn more about them in the reference docs of the {class}`~discogs_client.models.CommunityDetails` class.

## Collection Data

To access the collection an [authenticated Client object](authentication.md) is required.

Assuming the {class}`.Client` object is called `d`:

```
me=d.identity()
print(me)
```

will return:

```
<User 123456 'discogs_username'>
```

Loop through _all_ the items in the collection:

```
for item in me.collection_folders[0].releases:
    print(item)
```

```
<CollectionItemInstance 731053 'DJ-Kicks'>
<CollectionItemInstance 2230329 'Drumlesson Zwei'>
<CollectionItemInstance 6794957 'The K&D Sessions™'>
...
...
```

The items in the collection always are {class}`.CollectionItemInstance` objects.


### Collection Items by Folder

- Folder 0 is a special folder containing all the release in the user's collection
- Folder 1 is the "Uncategorized" folder.
- Folders 2 to n are any other collection folders manually created by the user.

To loop through the "Uncategorized" folder:

```
for item in me.collection_folders[1].releases:
    print(item)
```

Find out more about the available attributes of a {class}`.CollectionItemInstance`:

```
print(dir(me.collection_folders[1].releases[123]:
```

```
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_known_invalid_keys', 'changes', 'client', 'data', 'date_added', 'delete', 'fetch', 'folder_id', 'id', 'notes', 'rating', 'refresh', 'release', 'save']
```

Get a full {class}`.Release` object of a collection item:

```
print(me.collection_folders[1].releases[123].release)
```

```
<Release 1692728 'Phylyps Trak II'>
```

Get the {attr}`~.Release.title` of the {class}`.Release`:

```
print(me.collection_folders[1].releases[123].release.title)
```

```
Phylyps Trak II
```


### Collection Items by Release

As seen in the [Collection Items by Folder chapter](fetching_data.md#collection-items-by-folder), collection items can be accessed by iterating through a specific folder or the whole collection.

An alternative approach is using the {meth}`.collection_items` method which can be faster than iterating through the collection. After passing this method a `release_id` or {class}`.Release` object, it will return a list of {class}`.CollectionItemInstance` objects.

As it is possible that you have (or physically own) multiple copies of the same release inside one or more collection folders, using this method will return all copies of the release no matter which folder it is located in.

The example code below will print all {class}`.CollectionItemInstance`s of release 22155985. The attributes of the {class}`.CollectionItemInstance`s will show additional information, such as the folder it is located in or the details of the {class}`.Release`.

```python
release_instances = me.collection_items(22155985)
for instance in release_instances:
    print(instance)
    print(instance.folder_id)
    print(instance.release)
```


### Adding a Release to a Collection Folder

```python
me.collection_folders[2].add_release(17392219)
```

_{meth}`.add_release` also accepts {class}`.Release` objects_


### Removing a Release from the Collection

Removing a single release instance identified by its index:

```python
folder = me.collection_folders[2]
releases = folder.releases
# Delete the first instance in releases
folder.remove_release(releases[0])
```

:::{caution}
The {meth}`.remove_release` method deletes from the collection entirely. To remove an instance from a folder only, use the {meth}`.uncategorize_release` method.
:::

To filter out which instance to remove we could also use the attributes of the {class}`.Release` object attached to the {class}`.CollectionItemInstance`:

```python
folder = me.collection_folders[2]
for instance in folder.releases:
    if instance.release.title == "Internet Protocol":
        folder.remove_release(instance)
```

### Removing a Release from a Folder

To remove a release from a collection folder, we need to know the release ID already and  make use of the {meth}`.collection_items` method. This way we could remove all the instances from all its containing folders (uncategorize them):

```python
release_instances = me.collection_items(22155985)
for instance in release_instances:
    folder = me.collection_folders[instance.folder_id]
    folder.uncategorize_release(instance)
```

### Moving a Release to a Different Folder

To move a release from a collection folder to another one, again we need to know the release ID already and make use of the {meth}`.collection_items` method. We also need to know the ID of the target folder we want to move to (use {attr}`.collection_folders`). We move all the instances from all its containing folders to a specified target folder:

```python
release_instances = me.collection_items(22155985)
target_folder = 1
for folder in me.collection_folders:
    if folder.name == "My Target Folder":
        target_folder = folder.id

for instance in release_instances:
    folder = me.collection_folders[instance.folder_id]
    folder.move_release(instance, target_folder)
```

_{meth}`.remove_release`, {meth}`.move_release` and {meth}`.uncategorize_release` only accept {class}`.CollectionItemInstance` objects_


## Using {meth}`~discogs_client.models.PrimaryAPIObject.fetch` to get other data

You can use the {meth}`~discogs_client.models.PrimaryAPIObject.fetch` method to get any data from an object, including data that may not be accessible via the objects properties.

An [authenticated Client object](authentication.md) is required. To understand the Discogs API, see the [Discogs API documentation](https://www.discogs.com/developers/) or use the community [Postman collection](https://github.com/leopuleo/discogs-postman) to test the API.

Examples of using the {meth}`~discogs_client.models.PrimaryAPIObject.fetch` method:

```python
release = d.release(1026691)

print(release.id)
print(release.fetch('id'))
print(release.fetch('community')['rating'])
```

```python
1026691
1026691
{'count': 274, 'average': 4.38}
```
