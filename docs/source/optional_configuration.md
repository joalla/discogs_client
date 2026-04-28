# Optional Configuration

## Requests rate limiting

The Discogs API has rate limitations as documented on the [discogs.com API
documentation pages](
https://www.discogs.com/developers#page:home,header:home-rate-limiting).
python3-discogs-client respects and handles these limitations automatically.

_Backing off and auto retry when API rate limit is hit_ is enabled by default and can be disabled as follows:

```python
>>> import discogs_client
>>> d = discogs_client.Client('ExampleApplication/0.1')
>>> d.backoff_enabled = False
```

## Request timeouts

By default the {class}`.Client` does not timeout requests.

For example, to enable a request timeout of 5 seconds:

```python
timeout_in_seconds = 5
client.set_timeout(
    connect=timeout_in_seconds,
    read=timeout_in_seconds
)
```

_Timeouts support integer and float values, you can also set either value to `None` to disable timeout for connect or read separately_

## Trust Discogs per page value

When accessing paginated results by index (e.g. `results[42]`),
python3-discogs-client uses the `per_page` value from the API response to
calculate which page contains the item directly. This is fast, but assumes the
API always returns exactly `per_page` items per page.

If the API returns fewer items per page than the reported `per_page` value,
this calculation can be off. In such cases, disable this behaviour to fall
back to a sequential page walk:

```python
>>> import discogs_client
>>> d = discogs_client.Client('ExampleApplication/0.1')
>>> d.trust_per_page = False
```

:::{attention}
The sequential fallback is slower for large result sets, as it must fetch pages
one by one until it reaches the requested index.
:::
