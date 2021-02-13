import unittest
from datetime import datetime, timezone, timedelta
from discogs_client.tests import DiscogsClientTestCase
from discogs_client import utils
from dateutil.tz import tzutc, tzoffset


class UtilsTestCase(DiscogsClientTestCase):
    def test_update_qs(self):
        """update_qs helper works as intended"""
        u = utils.update_qs
        self.assertEqual(u('http://example.com', {'foo': 'bar'}), 'http://example.com?foo=bar')
        self.assertEqual(u('http://example.com?foo=bar', {'foo': 'baz'}), 'http://example.com?foo=bar&foo=baz')
        # be careful for dict iteration order is not deterministic
        result = u('http://example.com?c=3&a=yep', {'a': 1, 'b': '1'})
        try:
            self.assertEqual(result, 'http://example.com?c=3&a=yep&a=1&b=1')
        except AssertionError:
            self.assertEqual(result, 'http://example.com?c=3&a=yep&b=1&a=1')

        self.assertEqual(u('http://example.com', {'a': 't\xe9st'}),
                         'http://example.com?a=t%C3%A9st')

    def test_omit_none(self):
        o = utils.omit_none
        self.assertEqual(o({
            'foo': None,
            'baz': 'bat',
            'qux': None,
            'flan': 0,
        }), {
            'baz': 'bat',
            'flan': 0,
        })

        self.assertEqual(o({k: None for k in ('qux', 'quux', 'quuux')}), {})
        self.assertEqual(o({'nope': 'yep'}), {'nope': 'yep'})
        self.assertEqual(o({}), {})

    def test_parse_timestamp(self):
        p = utils.parse_timestamp
        self.assertEqual(
            p('2016-07-27T08:11:29-07:00'),
            datetime(2016, 7, 27, 8, 11, 29, tzinfo=tzoffset(None, -25200))
        )
        self.assertEqual(
            p('2055-07-27T08:11:29-07:00'),
            datetime(2055, 7, 27, 8, 11, 29, tzinfo=timezone(timedelta(hours=-7)))
        )
        self.assertEqual(
            p('1930-07-27T08:11:29-00:00'),
            datetime(1930, 7, 27, 8, 11, 29, tzinfo=timezone.utc)
        )
        self.assertEqual(
            p('1930-07-27T08:11:29-00:00'),
            datetime(1930, 7, 27, 8, 11, 29, tzinfo=tzutc())
        )

    def test_condition(self):
        self.assertRaises(TypeError, lambda: utils.Condition())
        self.assertEqual(utils.Condition.MINT, 'Mint (M)')
        self.assertEqual(utils.Condition.NEAR_MINT, 'Near Mint (NM or M-)')

    def test_status(self):
        self.assertRaises(TypeError, lambda: utils.Status())
        self.assertEqual(utils.Status.DRAFT, 'Draft')
        self.assertEqual(utils.Status.FOR_SALE, 'For Sale')

    def test_sort(self):
        self.assertRaises(TypeError, lambda: utils.Sort())
        self.assertEqual(utils.Sort.By.ARTIST, 'artist')
        self.assertEqual(utils.Sort.Order.ASCENDING, 'asc')
        self.assertEqual(utils.Sort.Order.DESCENDING, 'desc')


def suite():
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(UtilsTestCase)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
