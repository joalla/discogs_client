import unittest
from discogs_client.models import Artist, Release, ListItem, CollectionValue
from discogs_client.tests import DiscogsClientTestCase
from discogs_client.exceptions import HTTPError


class ModelsTestCase(DiscogsClientTestCase):
    def test_artist(self):
        """Artists can be fetched and parsed"""
        a = self.d.artist(1)
        self.assertEqual(a.name, 'Persuader, The')

    def test_release(self):
        """Releases can be fetched and parsed"""
        r = self.d.release(1)
        self.assertEqual(r.title, 'Stockholm')

    def test_master(self):
        """Masters can be fetched and parsed"""
        m = self.d.master(4242)
        self.assertEqual(len(m.tracklist), 4)

    def test_user(self):
        """Users can be fetched and parsed"""
        u = self.d.user('example')
        self.assertEqual(u.username, 'example')
        self.assertEqual(u.name, 'Example Sampleman')

    def test_list(self):
        """Lists can be fetched and parsed"""
        l = self.d.list(1)
        i = l.items
        self.assertEqual(l.name, 'Example List')
        self.assertEqual(l.description, 'description')
        self.assertEqual(l.public, True)
        self.assertTrue(isinstance(i[0], ListItem))

    def test_search(self):
        results = self.d.search('trash80')
        self.assertEqual(len(results), 13)
        self.assertTrue(isinstance(results[0], Artist))
        self.assertTrue(isinstance(results[1], Release))

    def test_bytes_search(self):
        results = self.d.search(b'trash80')
        self.assertEqual(len(results), 13)
        self.assertTrue(isinstance(results[0], Artist))
        self.assertTrue(isinstance(results[1], Release))

    def test_utf8_search(self):
        uni_string = 'caf\xe9'
        try:
            results = self.d.search(uni_string)
        except Exception as e:
            self.fail('exception {} was raised'.format(e))

    def test_fee(self):
        fee = self.d.fee_for(20.5, currency='EUR')
        self.assertEqual(fee.currency, 'USD')
        self.assertAlmostEqual(fee.value, 1.57)

    def test_invalid_artist(self):
        """Invalid artist raises HTTPError"""
        self.assertRaises(HTTPError, lambda: self.d.artist(0).name)

    def test_invalid_release(self):
        """Invalid release raises HTTPError"""
        self.assertRaises(HTTPError, lambda: self.d.release(0).title)

    def test_http_error(self):
        """HTTPError provides useful information"""
        self.assertRaises(HTTPError, lambda: self.d.artist(0).name)

        try:
            self.d.artist(0).name
        except HTTPError as e:
            self.assertEqual(e.status_code, 404)
            self.assertEqual('404: Resource not found.', str(e))

    def test_parent_label(self):
        """Test parent_label / sublabels relationship"""
        l = self.d.label(1)
        l2 = self.d.label(31405)

        self.assertTrue(l.parent_label is None)
        self.assertTrue(l2 in l.sublabels)
        self.assertEqual(l2.parent_label, l)

    def test_master_versions(self):
        """Test main_release / versions relationship"""
        m = self.d.master(4242)
        r = self.d.release(79)
        v = m.versions

        self.assertEqual(len(v), 2)
        self.assertTrue(r in v)
        self.assertEqual(r.master, m)

        r2 = self.d.release(3329867)
        self.assertTrue(r2.master is None)

    def test_user_writable(self):
        """User profile can be updated"""
        u = self.d.user('example')
        u.name  # Trigger a fetch

        method, url, data, headers = self.d._fetcher.requests[0]
        self.assertEqual(method, 'GET')
        self.assertEqual(url, '/users/example')

        new_home_page = 'http://www.discogs.com'
        u.home_page = new_home_page
        self.assertTrue('home_page' in u.changes)
        self.assertFalse('profile' in u.changes)

        u.save()

        # Save
        method, url, data, headers = self.d._fetcher.requests[1]
        self.assertEqual(method, 'POST')
        self.assertEqual(url, '/users/example')
        self.assertEqual(data, {'home_page': new_home_page})

        # Refresh
        method, url, data, headers = self.d._fetcher.requests[2]
        self.assertEqual(method, 'GET')
        self.assertEqual(url, '/users/example')

    def test_wantlist(self):
        """Wantlists can be manipulated"""
        # Fetch the user/wantlist from the filesystem
        u = self.d.user('example')
        self.assertEqual(len(u.wantlist), 3)

        # Stub out expected responses
        self.m._fetcher.fetcher.responses = {
            '/users/example/wants/5': (b'{"id": 5}', 201),
            '/users/example/wants/1': (b'', 204),
        }

        # Now bind the user to the memory client
        u.client = self.m

        u.wantlist.add(5)
        method, url, data, headers = self.m._fetcher.last_request
        self.assertEqual(method, 'PUT')
        self.assertEqual(url, '/users/example/wants/5')

        u.wantlist.remove(1)
        method, url, data, headers = self.m._fetcher.last_request
        self.assertEqual(method, 'DELETE')
        self.assertEqual(url, '/users/example/wants/1')

    def test_inventory(self):
        """Inventory can be manipulated"""
        # Fetch users inventory from the filesystem
        u = self.d.user('example')
        self.assertEqual(len(u.inventory), 1)

        # Stub out expected responses
        self.m._fetcher.fetcher.responses = {
            '/marketplace/listings': (b'{"listing_id": 321}', 201),
        }

        # Now bind the user to the memory client
        u.client = self.m

        # Test adding by release id
        u.inventory.add_listing(release=123, condition='Mint (M)', price=15.99, status='Draft')
        method, url, data, headers = self.m._fetcher.last_request
        self.assertEqual(method, 'POST')
        self.assertEqual(url, '/marketplace/listings')
        self.assertEqual(data['release_id'], '123')

        # test adding by release object
        r = self.d.release(1)
        self.assertEqual(r.title, 'Stockholm')
        u.inventory.add_listing(release=r, condition='Mint (M)', price=15.99, status='Draft')
        method, url, data, headers = self.m._fetcher.last_request
        self.assertEqual(method, 'POST')
        self.assertEqual(url, '/marketplace/listings')
        self.assertEqual(data['release_id'], '1')

    def test_listing(self):
        """Listing can be manipulated"""
        # Fetch users inventory from the filesystem
        u = self.d.user('example')

        # Fetch listing
        listing = u.inventory[0]
        method, url, data, headers = self.d._fetcher.requests[1]
        self.assertEqual(method, 'GET')
        self.assertEqual(url, '/users/example/inventory?page=1&per_page=50')

        # Test fetching listing information
        self.assertEqual(listing.status, 'For Sale')
        self.assertEqual(listing.price.value, 149.99)
        self.assertEqual(listing.allow_offers, True)
        self.assertEqual(listing.id, 150899904)
        self.assertEqual(listing.seller.username, 'example')
        self.assertEqual(listing.release.id, 2992668)

        # Test manipulating listing
        listing.status = 'Draft'
        listing.price = 1.99
        # Test unsaved price
        self.assertEqual(listing.price.value, 1.99)
        listing.allow_offers = False
        expected = {
            'status': 'Draft',
            'price': 1.99,
            'allow_offers': False,
        }
        self.assertEqual(listing.changes, expected)

        # Test saving
        listing.save()
        method, url, data, headers = self.d._fetcher.requests[2]
        self.assertEqual(method, 'POST')
        self.assertEqual(url, '/marketplace/listings/150899904')
        self.assertEqual(data, expected)

        # Refresh
        method, url, data, headers = self.d._fetcher.requests[3]
        self.assertEqual(method, 'GET')
        self.assertEqual(url, '/marketplace/listings/150899904')


    def test_collection(self):
        """Collection folders can be manipulated"""
        # Fetch the users collection folders from the filesystem
        u = self.d.user('example')
        self.assertEqual(len(u.collection_folders), 3)
        # Fetch basic information from folders endpoint
        self.assertEqual(u.collection_folders[0].id, 0)
        self.assertEqual(u.collection_folders[0].name, "All")
        self.assertEqual(u.collection_folders[1].id, 1)
        self.assertEqual(u.collection_folders[1].name, "Uncategorized folder")
        # Fetch details from folders/<id>/releases endpoint
        self.assertEqual(u.collection_folders[0].releases[2].id, 656052)
        self.assertEqual(u.collection_folders[0].releases[2].release.title, "Control / Command & Conquer")

        # Mock expected responses for add_release test - FileSystemFetcher disabled now
        self.m._fetcher.fetcher.responses = {
            '/users/example/collection/folders': (b'''
                {"folders": [{"resource_url": "/users/example/collection/folders/0",
                              "id": 0,
                              "name": "All"
                             },
                             {"resource_url": "/users/example/collection/folders/1",
                              "id": 1,
                              "name": "Uncategorized folder"
                             }]
                 }''', 200),
            '/users/example/collection/folders/1': (b'{}', 200),
            '/users/example/collection/folders/1/releases/123456': (b'{"instance_id": 123}', 201),
            '/users/example/collection/folders/1/releases/1': (b'{"instance_id": 124}', 201),
        }

        # Now bind the user to the memory client
        u.client = self.m

        # test adding a release by id
        u.collection_folders[1].add_release(123456)
        method, url, data, headers = self.m._fetcher.last_request
        self.assertEqual(method, 'POST')
        self.assertEqual(url, '/users/example/collection/folders/1/releases/123456')

        # test adding a release object
        r = self.d.release(1)
        self.assertEqual(r.title, 'Stockholm')
        u.collection_folders[1].add_release(r)
        method, url, data, headers = self.m._fetcher.last_request
        self.assertEqual(method, 'POST')
        self.assertEqual(url, '/users/example/collection/folders/1/releases/1')

    def test_delete_object(self):
        """Can request DELETE on an APIObject"""
        u = self.d.user('example')
        u.delete()

        method, url, data, headers = self.d._fetcher.last_request
        self.assertEqual(method, 'DELETE')
        self.assertEqual(url, '/users/example')

    def test_identity(self):
        """OAuth identity returns a User"""
        me = self.d.identity()
        self.assertEqual(me.data['consumer_name'], 'Test Client')
        self.assertEqual(me, self.d.user('example'))

    def test_marketplace_stats(self):
        """Release stats can be fetched and parsed"""
        stats = self.d.release(1).marketplace_stats

        # Assert that returned stats are correct.
        self.assertEqual(stats.num_for_sale, 10)
        self.assertEqual(stats.lowest_price.value, 100)
        self.assertEqual(stats.lowest_price.currency, 'EUR')

        # Assert that request URL and method is correct.
        method, url, data, headers = self.d._fetcher.requests[0]
        self.assertEqual(method, 'GET')
        self.assertEqual(url, '/marketplace/stats/1')

    def test_collection_value(self):
        """Collection Value can be fetched and parsed"""
        u = self.d.user("example")

        self.assertEqual(isinstance(u.collection_value, CollectionValue), True)
        self.assertEqual(u.collection_value.minimum, "£1.05")
        self.assertEqual(u.collection_value.maximum, "£5")
        self.assertEqual(u.collection_value.median, "£2.50")

        # Assert that request URL and method is correct.
        method, url, data, headers = self.d._fetcher.requests[0]
        self.assertEqual(method, "GET")
        self.assertEqual(url, "/users/example/collection/value")


def suite():
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(ModelsTestCase)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
