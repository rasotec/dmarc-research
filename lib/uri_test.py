from unittest import TestCase, main
from uri import UriParseErrorType, parse_uri, parse_domain

class Test(TestCase):
    def test_parse_uri(self):
        # Test invalid scheme
        result = parse_uri('a+b@beispiel.de')
        self.assertEqual(result.error_type, UriParseErrorType.INVALID_SCHEME)
        self.assertIsNone(result.email)
        self.assertIsNone(result.payload)

        # Test valid email with no payload
        result = parse_uri('mailto:a+b@beispiel.de')
        self.assertIsNone(result.error_type)
        self.assertEqual(result.email, 'a+b@beispiel.de')
        self.assertIsNone(result.payload)

        # Test whitespace handling
        result = parse_uri('mailto:  a+b@beispiel.de ')
        self.assertIsNone(result.error_type)
        self.assertEqual(result.email, 'a+b@beispiel.de')
        self.assertIsNone(result.payload)

        # Test valid payload with 'g' unit
        result = parse_uri('mailto:a+b@beispiel.de!1g')
        self.assertIsNone(result.error_type)
        self.assertEqual(result.email, 'a+b@beispiel.de')
        self.assertEqual(result.payload, '1g')

        # Test whitespace in payload
        result = parse_uri('mailto: a+b@beispiel.de ! 1g')
        self.assertIsNone(result.error_type)
        self.assertEqual(result.email, 'a+b@beispiel.de')
        self.assertEqual(result.payload, '1g')

        # Test valid payload with 'm' unit
        result = parse_uri('mailto:a+b@beispiel.de!10m')
        self.assertIsNone(result.error_type)
        self.assertEqual(result.email, 'a+b@beispiel.de')
        self.assertEqual(result.payload, '10m')

        # Test invalid payload format
        result = parse_uri('mailto:a+b@beispiel.de!!10m')
        self.assertIsNone(result.email)
        self.assertIsNone(result.payload)
        self.assertEqual(result.error_type, UriParseErrorType.INVALID_PAYLOAD)

        # Test valid payload with 'k' unit
        result = parse_uri('mailto:a+b@beispiel.de!500k')
        self.assertIsNone(result.error_type)
        self.assertEqual(result.email, 'a+b@beispiel.de')
        self.assertEqual(result.payload, '500k')

        # Test valid payload with 't' unit
        result = parse_uri('mailto:a+b@beispiel.de!2t')
        self.assertIsNone(result.error_type)
        self.assertEqual(result.email, 'a+b@beispiel.de')
        self.assertEqual(result.payload, '2t')

        # Test invalid payload unit
        result = parse_uri('mailto:a+b@beispiel.de!10x')
        self.assertEqual(result.error_type, UriParseErrorType.INVALID_PAYLOAD_UNIT)
        self.assertIsNone(result.email)
        self.assertIsNone(result.payload)

        # Test non-numeric payload
        result = parse_uri('mailto:a+b@beispiel.de!abcm')
        self.assertEqual(result.error_type, UriParseErrorType.INVALID_PAYLOAD_SIZE)
        self.assertIsNone(result.email)
        self.assertIsNone(result.payload)

        # Test empty email with exclamation mark
        result = parse_uri('mailto:!')
        self.assertEqual(result.error_type, UriParseErrorType.EMPTY_EMAIL)
        self.assertIsNone(result.email)
        self.assertIsNone(result.payload)

        # Test empty email with a valid payload format
        result = parse_uri('mailto:!10m')
        self.assertEqual(result.error_type, UriParseErrorType.EMPTY_EMAIL)
        self.assertIsNone(result.email)
        self.assertIsNone(result.payload)

        # Test with only whitespace in email
        result = parse_uri('mailto:  ')
        self.assertEqual(result.error_type, UriParseErrorType.EMPTY_EMAIL)
        self.assertIsNone(result.email)
        self.assertIsNone(result.payload)

    def test_parse_domain(self):
        self.assertEqual('beispiel.de', parse_domain('a+b@beispiel.de'))
        self.assertEqual(None, parse_domain('abc.de'))

if __name__ == '__main__':
    main()
