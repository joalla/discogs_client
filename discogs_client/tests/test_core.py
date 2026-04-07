import unittest
from discogs_client import Client
from discogs_client.fetchers import MemoryFetcher
from discogs_client.tests import DiscogsClientTestCase
from discogs_client.exceptions import ConfigurationError, HTTPError
from datetime import datetime


class CoreTestCase(DiscogsClientTestCase):
    def test_user_agent(self):
        """User-Agent should be properly set"""
        self.d.artist(1).name

        bad_client = Client('')

        self.assertRaises(ConfigurationError, lambda: bad_client.artist(1).name)

        try:
            bad_client.artist(1).name
        except ConfigurationError as e:
            self.assertTrue('User-Agent' in str(e))

    def test_caching(self):
        """Only perform a fetch when requesting missing data"""
        a = self.d.artist(1)

        self.assertEqual(a.id, 1)
        self.assertTrue(self.d._fetcher.last_request is None)

        self.assertEqual(a.name, 'Persuader, The')
        self.assertGot('/artists/1')

        self.assertEqual(a.real_name, 'Jesper Dahlb\u00e4ck')
        self.assertEqual(len(self.d._fetcher.requests), 1)

        # Get a key that's not in our cache
        a.fetch('blorf')
        # 6/2022: removed extra call to api in cases where last api point called is same as resource_url
        # self.assertEqual(len(self.d._fetcher.requests), 2)
        self.assertEqual(len(self.d._fetcher.requests), 1)
        self.assertTrue('blorf' in a._known_invalid_keys)

        # Now we know artists don't have blorves
        a.fetch('blorf')
        # 6/2022: removed extra call to api in cases where last api point called is same as resource_url
        # self.assertEqual(len(self.d._fetcher.requests), 2)
        self.assertEqual(len(self.d._fetcher.requests), 1)

    def test_equality(self):
        """APIObjects of the same class are equal if their IDs are"""
        a1 = self.d.artist(1)
        a1_ = self.d.artist(1)
        self.d.artist(2)

        r1 = self.d.release(1)

        self.assertEqual(a1, a1_)
        self.assertEqual(a1, r1.artists[0])
        self.assertNotEqual(a1, r1)
        self.assertNotEqual(r1, ':D')

    def test_transform_datetime(self):
        """String timestamps are converted to datetimes"""
        registered = self.d.user('example').registered
        self.assertTrue(isinstance(registered, datetime))

    def test_object_field(self):
        """APIObjects can have APIObjects as properties"""
        self.assertEqual(self.d.master(4242).main_release, self.d.release(79))

    def test_read_only_simple_field(self):
        """Can't write to a SimpleField when writable=False"""
        u = self.d.user('example')

        def fail():
            u.rank = 9001
        self.assertRaises(AttributeError, fail)

    def test_read_only_object_field(self):
        """Can't write to an ObjectField"""
        m = self.d.master(4242)

        def fail():
            m.main_release = 'lol!'
        self.assertRaises(AttributeError, fail)

    def test_pagination(self):
        """PaginatedLists are parsed correctly, indexable, and iterable"""
        results = self.d.artist(1).releases

        self.assertEqual(results.per_page, 50)
        self.assertEqual(results.pages, 2)
        self.assertEqual(results.count, 57)

        self.assertEqual(len(results), 57)
        self.assertEqual(len(results.page(1)), 50)

        self.assertRaises(HTTPError, lambda: results.page(42))

        try:
            results.page(42)
        except HTTPError as e:
            self.assertEqual(e.status_code, 404)

        self.assertRaises(IndexError, lambda: results[3141592])

        self.assertEqual(results[0].id, 20209)
        self.assertTrue(self.d.release(20209) in results)

        # Changing pagination settings invalidates the cache
        results.per_page = 10
        self.assertTrue(results._num_pages is None)

    def test_pagination_with_short_page(self):
        """Indexing walks actual page sizes when the API under-fills a page."""
        client = Client('ua')
        client._base_url = ''
        client._fetcher = MemoryFetcher({
            '/artists/1': (
                b'{"id": 1, "name": "Badger", "releases_url": "/artists/1/releases"}',
                200,
            ),
            '/artists/1/releases?page=1&per_page=50': (
                b'{"pagination": {"per_page": 50, "pages": 2, "items": 2}, '
                b'"releases": [{"id": 101, "type": "release", "title": "First"}]}',
                200,
            ),
            '/artists/1/releases?page=2&per_page=50': (
                b'{"pagination": {"per_page": 50, "pages": 2, "items": 2}, '
                b'"releases": [{"id": 102, "type": "release", "title": "Second"}]}',
                200,
            ),
        })

        results = client.artist(1).releases

        self.assertEqual(results.pages, 2)
        self.assertEqual(len(results.page(1)), 1)
        self.assertEqual(results[0].id, 101)
        self.assertEqual(results[1].id, 102)
        self.assertRaises(IndexError, lambda: results[2])

    def test_pagination_with_varying_page_sizes(self):
        """Indexing works correctly with pages of different actual sizes."""
        client = Client('ua')
        client._base_url = ''
        client._fetcher = MemoryFetcher({
            '/artists/1': (
                b'{"id": 1, "name": "Badger", "releases_url": "/artists/1/releases"}',
                200,
            ),
            '/artists/1/releases?page=1&per_page=50': (
                b'{"pagination": {"per_page": 50, "pages": 3, "items": 8}, '
                b'"releases": ['
                b'{"id": 101, "type": "release", "title": "First"},'
                b'{"id": 102, "type": "release", "title": "Second"},'
                b'{"id": 103, "type": "release", "title": "Third"}'
                b']}',
                200,
            ),
            '/artists/1/releases?page=2&per_page=50': (
                b'{"pagination": {"per_page": 50, "pages": 3, "items": 8}, '
                b'"releases": ['
                b'{"id": 104, "type": "release", "title": "Fourth"},'
                b'{"id": 105, "type": "release", "title": "Fifth"}'
                b']}',
                200,
            ),
            '/artists/1/releases?page=3&per_page=50': (
                b'{"pagination": {"per_page": 50, "pages": 3, "items": 8}, '
                b'"releases": ['
                b'{"id": 106, "type": "release", "title": "Sixth"},'
                b'{"id": 107, "type": "release", "title": "Seventh"},'
                b'{"id": 108, "type": "release", "title": "Eighth"}'
                b']}',
                200,
            ),
        })

        results = client.artist(1).releases

        # Verify we can access items across all pages
        self.assertEqual(results[0].id, 101)
        self.assertEqual(results[1].id, 102)
        self.assertEqual(results[2].id, 103)
        self.assertEqual(results[3].id, 104)  # First item on page 2
        self.assertEqual(results[4].id, 105)  # Last item on page 2
        self.assertEqual(results[5].id, 106)  # First item on page 3
        self.assertEqual(results[7].id, 108)  # Last item

        # Verify out-of-bounds access raises IndexError
        self.assertRaises(IndexError, lambda: results[8])

    def test_pagination_with_short_page_sequential_traversal(self):
        """Verify sequential page walking works when all pages are short."""
        client = Client('ua')
        client._base_url = ''
        client._fetcher = MemoryFetcher({
            '/artists/1': (
                b'{"id": 1, "name": "Badger", "releases_url": "/artists/1/releases"}',
                200,
            ),
            '/artists/1/releases?page=1&per_page=50': (
                b'{"pagination": {"per_page": 50, "pages": 4, "items": 4}, '
                b'"releases": [{"id": 201, "type": "release", "title": "A"}]}',
                200,
            ),
            '/artists/1/releases?page=2&per_page=50': (
                b'{"pagination": {"per_page": 50, "pages": 4, "items": 4}, '
                b'"releases": [{"id": 202, "type": "release", "title": "B"}]}',
                200,
            ),
            '/artists/1/releases?page=3&per_page=50': (
                b'{"pagination": {"per_page": 50, "pages": 4, "items": 4}, '
                b'"releases": [{"id": 203, "type": "release", "title": "C"}]}',
                200,
            ),
            '/artists/1/releases?page=4&per_page=50': (
                b'{"pagination": {"per_page": 50, "pages": 4, "items": 4}, '
                b'"releases": [{"id": 204, "type": "release", "title": "D"}]}',
                200,
            ),
        })

        results = client.artist(1).releases

        # With per_page=50 but only 1 item per actual page,
        # math-based indexing would fail. Sequential walking should work.
        self.assertEqual(results[0].id, 201)
        self.assertEqual(results[1].id, 202)
        self.assertEqual(results[2].id, 203)
        self.assertEqual(results[3].id, 204)
        self.assertRaises(IndexError, lambda: results[4])

    def test_pagination_404_exception_chaining(self):
        """Verify that HTTPError 404 is properly chained when index is out of bounds."""
        client = Client('ua')
        client._base_url = ''
        client._fetcher = MemoryFetcher({
            '/artists/1': (
                b'{"id": 1, "name": "Badger", "releases_url": "/artists/1/releases"}',
                200,
            ),
            '/artists/1/releases?page=1&per_page=50': (
                b'{"pagination": {"per_page": 50, "pages": 1, "items": 2}, '
                b'"releases": ['
                b'{"id": 301, "type": "release", "title": "Only"},'
                b'{"id": 302, "type": "release", "title": "Two"}'
                b']}',
                200,
            ),
        })

        results = client.artist(1).releases

        # Access valid items
        self.assertEqual(results[0].id, 301)
        self.assertEqual(results[1].id, 302)

        # Accessing beyond bounds should raise IndexError
        # (which is chained from HTTPError 404)
        with self.assertRaises(IndexError):
            results[100]

    def test_timeout_defaults_to_none(self):
        # Need to create client without LoggingDelegator here
        # self.d would throw AttributeError trying to access timeout properties on LoggingDelegator
        client = Client('')
        client._fetcher = MemoryFetcher({})
        self.assertEqual(None, client.connection_timeout)
        self.assertEqual(None, client.read_timeout)

    def test_set_timeout_in_float(self):
        self.d.set_timeout(connect=1.23, read=7.42)
        self.assertEqual(1.23, self.d.connection_timeout)
        self.assertEqual(7.42, self.d.read_timeout)

    def test_set_timeout_in_int(self):
        self.d.set_timeout(connect=3, read=6)        
        self.assertEqual(3, self.d.connection_timeout)
        self.assertEqual(6, self.d.read_timeout)

    def test_set_timeout_to_none(self):
        self.d.set_timeout(connect=5, read=None)
        self.assertEqual(5, self.d.connection_timeout)
        self.assertEqual(None, self.d.read_timeout)

        self.d.set_timeout(connect=None, read=10)
        self.assertEqual(None, self.d.connection_timeout)
        self.assertEqual(10, self.d.read_timeout)

        self.d.set_timeout(connect=None, read=None)
        self.assertEqual(None, self.d.connection_timeout)
        self.assertEqual(None, self.d.read_timeout)


def suite():
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(CoreTestCase)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
