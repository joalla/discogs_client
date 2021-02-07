import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from discogs_client.tests import DiscogsClientTestCase
from discogs_client import utils
from discogs_client.exceptions import HTTPError, TooManyAttemptsError


call_count = 0


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
        self.assertEqual(p('2012-01-01T00:00:00'), datetime(2012, 1, 1, 0, 0, 0))
        self.assertEqual(p('2001-05-25T00:00:42'), datetime(2001, 5, 25, 0, 0, 42))


    @patch('discogs_client.utils.get_backoff_duration')
    def test_backed_off_when_rate_limit_reached(self, patched_duration):

        # Mock sleep duration returned so it doesn't effect tests speed
        patched_duration.return_value = 0.00001
        backoff = utils.backoff
        mock_ratelimited_response = MagicMock()
        mock_ratelimited_response.status_code = 429

        mock_ok_response = MagicMock()
        mock_ok_response.status_code = 200

        @backoff(enabled=True)
        def always_fails():
            return mock_ratelimited_response

        @backoff(enabled=True)
        def returns_non_ratelimit_status_code():
            return mock_ok_response

        @backoff(enabled=True)
        def succeeds_after_x_calls():
            global call_count
            call_count += 1
            if call_count < 3:
                return mock_ratelimited_response
            else:
                return mock_ok_response

        @backoff(enabled=False)
        def function_not_decorated_when_disabled():
            return mock_ok_response


        with self.assertRaises(TooManyAttemptsError):
            always_fails()

        self.assertEqual(mock_ok_response, returns_non_ratelimit_status_code())

        self.assertEqual(mock_ok_response, succeeds_after_x_calls())

        with patch('discogs_client.utils.get_backoff_duration') as patched_duration:
            function_not_decorated_when_disabled()
            self.assertEqual(0, patched_duration.call_count)


def suite():
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(UtilsTestCase)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
