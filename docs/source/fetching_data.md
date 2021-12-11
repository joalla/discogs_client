# Fetching data

Note that the examples in this chapter are shown using a Python REPL and require
an existing [Client object](quickstart.md) already.

## Artist

Query for an artist using the artist's name:

```python
>>> artist = d.artist(956139)
>>> print(artist)
<Artist "...">
>>> 'name' in artist.data.keys()
True
```

### Special properties

Get a list of `Artist`s representing this artists' aliases:

```python
>>> artist.aliases
[...]
```

Get a list of `Release`s by this artist by page number:

```python
>>> artist.releases.page(1)
[...]
```

## Release

Query for a release using its Discogs ID:

```python
>>> release = d.release(221824)
```

### Special properties

Get the title of this `Release`:

```python
>>> release.title
'...'
```

Get a list of all `Artist`s associated with this `Release`:

```python
>>> release.artists
[<Artist "...">]
```

Get the tracklist for this `Release`:

```python
>>> release.tracklist
[...]
```

Get details of the first track on this `Release`

```python
>>> release.tracklist[0].title
[...]
>>> release.tracklist[0].duration
[...]
```

Find the available properties of a `Track` object in the module docs:
{class}`discogs_client.models.Track`

Get the `MasterRelease` for this `Release`:

```python
>>> release.master
<MasterRelease "...">
```

Get a list of all `Label`s for this `Release`:

```python
>>> release.labels
[...]
```

## MasterRelease

Query for a master release using its Discogs ID:

```python
>>> master_release = d.master(120735)
```

### Special properties

Get the key `Release` for this `MasterRelease`:

```python
>>> master_release.main_release
<Release "...">
```

Get the title of this `MasterRelease`:

```python
>>> master_release.title
'...'
>>> master_release.title == master_release.main_release.title
True
```

Get a list of `Release`s representing other versions of this `MasterRelease` by
page number:

```python
>>> master_release.versions.page(1)
[...]
```

Get the tracklist for this `MasterRelease`:

```python
>>> master_release.tracklist
[...]
```

## Label

Query for a label using the label's ID:

```python
>>> label = d.label(6170)
```

### Special properties

Get a list of `Release`s from this `Label` by page number:

```python
>>> label.releases.page(1)
[...]
```

Get a list of `Label`s representing sublabels associated with this `Label`:

```python
>>> label.sublabels
[...]
```

Get the `Label`'s parent label, if it exists:

```python
>>> label.parent_label
<Label "Warp Records Limited">
```
