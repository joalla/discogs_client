from discogs_client.fetchers import OAuth2Fetcher
import unittest
from discogs_client.tests import DiscogsClientTestCase
from discogs_client.exceptions import HTTPError


class FetcherTestCase(DiscogsClientTestCase):
    def test_memory_fetcher(self):
        """Client can fetch responses with MemoryFetcher"""
        self.m.artist(1)

        self.assertRaises(HTTPError, lambda: self.m._get('/500'))

        try:
            self.m._get('/500')
        except HTTPError as e:
            self.assertEqual(e.status_code, 500)

        self.assertRaises(HTTPError, lambda: self.m.release(1).title)
        self.assertTrue(self.m._get('/204') is None)

    def test_oauth2_fetcher(self):
        _fetcher = OAuth2Fetcher(
            'consumer_key', 'consumer_secret', token=None, secret=None)

        self.assertEqual(_fetcher.client.resource_owner_key, None)
        self.assertEqual(_fetcher.client.resource_owner_secret, None)

        query_string = b'oauth_token=token&oauth_token_secret=secret'
        token, secret = _fetcher.store_token_from_qs(query_string)
        self.assertEqual(token, 'token')
        self.assertEqual(secret, 'secret')

        _fetcher.forget_token()
        self.assertEqual(_fetcher.client.resource_owner_key, None)
        self.assertEqual(_fetcher.client.resource_owner_secret, None)

        _fetcher.store_token(token, secret)
        self.assertEqual(_fetcher.client.resource_owner_key, token)
        self.assertEqual(_fetcher.client.resource_owner_secret, secret)

        _fetcher.set_verifier('1234567890')
        self.assertEqual(_fetcher.client.verifier, '1234567890')

    def test_request_backoff(self):
        _fetcher = OAuth2Fetcher(
            'consumer_key', 'consumer_secret', token=None, secret=None)

        query_string = b'oauth_token=token&oauth_token_secret=secret'
        token, secret = _fetcher.store_token_from_qs(query_string)

        _fetcher.store_token(token, secret)

        _fetcher.set_verifier('1234567890')
        _fetcher.fetch(self.m, "GET", "asddsa")


def suite():
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(FetcherTestCase)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
