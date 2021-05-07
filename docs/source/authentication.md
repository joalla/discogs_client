# Authentication

There are two forms of authentication the Discogs API allows: OAuth and
User-token Authentication.

User-token Authentication is great as a simple solution for scripts that just
want to use endpoint that require authentication, or for users who are writing
apps that only represent a single user (e.g., writing a store-front for your
Discogs seller account).

OAuth is useful if you want to create an application where a user uses your app
as a proxy to make requests and change information about their Discogs account.
This includes profile information, collection and wantlist information, and
marketplace changes.

We will cover both forms of authentication below.

## User-token Authentication

This is the simpler one of the two authentication methods. You need to generate
a token in the developer's section of your Discogs user account settings:

["Click user avatar on top right of screen" - "Settings" - "Developers"](
https://www.discogs.com/settings/developers) - "Generate new token ".

Supply the token to the `Client` class:

```python
import discogs_client
d = discogs_client.Client('my_user_agent/1.0', user_token='my_user_token')
```

That's it! You are now free to make authenticated requests. The downside is
that you'll be limited to the information only your user account can see
(i.e., no requests on behalf of other users).



## OAuth Authentication

OAuth is an open protocol commonly used for authorization (and in this case,
authentication as well). For more information on the OAuth specification,
please visit the OAuth website: http://oauth.net/

A Discogs consumer key and consumer secret are required for OAuth, to get
those go to the developer's section of your Discogs user account settings:

["Click user avatar on top right of screen" - "Settings" - "Developers"](
https://www.discogs.com/settings/developers) - "Create
an appplication". Fill out the form, copy consumer key and secret and optionally
add a custom callback url.

1. Importing the client library:
    ```python
    import discogs_client
    ```

2. Instantiating the `Client` class with the consumer key and secret:

    ```python
    d = discogs_client.Client(
        'my_user_agent/1.0',
        consumer_key='my_consumer_key',
        consumer_secret='my_consumer_secret'
    )
    ```

    You can also supply your OAuth token and token secret if you already have
    them saved, as so:

    ```python
    d = discogs_client.Client(
        'my_user_agent/1.0',
        consumer_key='my_consumer_key',
        consumer_secret='my_consumer_secret',
        token=u'my_token',
        secret=u'my_token_secret'
    )
    ```

    Alternativaly the `set_consumer_key()` method can be used on an already
    existing Client object to supply consumer key and secret.

    ```python
    d = discogs_client.Client('my_user_agent/1.0')
    d.set_consumer_key('my_consumer_key', 'my_consumer_secret')
    ```

4. Get authorization URL

    ```python
    d.get_authorize_url()
    ```

    This will return a tuple with the request token, request secret, and **the
    authorization URL that your user needs to visit** to accept your app's
    request to sign in on their behalf.

    If you are writing a web application, you can specify a string argument
    to this method that will be used as the `callback_url`:

    ```
    d.get_authorize_url('https://your.callback.url')
    ```

    If the user clicks on the returned discogs.com oauth url, the request token
    and request secret will be transmitted as the URL parameters to the provided
    callback URL:

    https://your.callback.url?oauth_token=secret_1&oauth_verifier=secret_2

5. Get OAuth access token

    Pass the OAuth verifier that you received after the user authorizes your app
    into this method. This will return a tuple with the access token and access
    token secret that finalizes the OAuth process.

    ```python
    d.get_access_token('verifier-here')
    ```

6. Verify

    We are free to make OAuth-based requests now. A smoke-test to verify
    everything is working is to call the `identity()` method:

    ```python
    me = d.identity()
    ```

    This will return a `User` object if everything is okay.

## More information

Find out more details about the authentication methods in the module
documentation: {class}`discogs_client.client.Client`
