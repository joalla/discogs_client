import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from discogs_client.tests import DiscogsClientTestCase
from discogs_client import utils
from discogs_client.exceptions import TooManyAttemptsError
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
        self.assertEqual(utils.Condition.MINT.value, 'Mint (M)')
        self.assertEqual(utils.Condition.NEAR_MINT.value, 'Near Mint (NM or M-)')

    def test_status(self):
        self.assertRaises(TypeError, lambda: utils.Status())
        self.assertEqual(utils.Status.DRAFT.value, 'Draft')
        self.assertEqual(utils.Status.FOR_SALE.value, 'For Sale')

    def test_sort(self):
        self.assertRaises(TypeError, lambda: utils.Sort())
        self.assertEqual(utils.Sort.By.ARTIST, 'artist')
        self.assertEqual(utils.Sort.Order.ASCENDING, 'asc')
        self.assertEqual(utils.Sort.Order.DESCENDING, 'desc')


    @patch('discogs_client.utils.get_backoff_duration')
    def test_backed_off_when_rate_limit_reached(self, patched_duration):
        # Mock sleep duration returned so it doesn't effect tests speed
        patched_duration.return_value = 0

        backoff = utils.backoff

        mock_ratelimited_response = MagicMock()
        mock_ratelimited_response.status_code = 429

        mock_ok_response = MagicMock()
        mock_ok_response.status_code = 200

        call_count = 0

        class BackoffTestClass:
            def __init__(self):
                self.backoff_enabled = True

            @backoff
            def always_fails(self):
                return mock_ratelimited_response

            @backoff
            def returns_non_ratelimit_status_code(self):
                return mock_ok_response

            @backoff
            def succeeds_after_x_calls(self):
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    return mock_ratelimited_response
                else:
                    return mock_ok_response

            @backoff
            def function_not_decorated_when_disabled(self):
                return mock_ratelimited_response

        test_class = BackoffTestClass()

        with self.assertRaises(TooManyAttemptsError):
            test_class.always_fails()

        self.assertEqual(mock_ok_response, test_class.returns_non_ratelimit_status_code())
        self.assertEqual(mock_ok_response, test_class.succeeds_after_x_calls())

        with patch('discogs_client.utils.get_backoff_duration') as patched_duration:
            test_class.backoff_enabled = False
            test_class.function_not_decorated_when_disabled()
            self.assertEqual(0, patched_duration.call_count)


def suite():
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(UtilsTestCase)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
