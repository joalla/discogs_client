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
