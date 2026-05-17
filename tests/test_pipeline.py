"""
Unit tests for the Beam pipeline logic.
"""

import unittest
from streaming.pipeline import ParseLogFn

class TestParseLogFn(unittest.TestCase):
    def test_parse_valid_json(self):
        """Tests if the DoFn correctly parses valid JSON bytes."""
        parser = ParseLogFn()
        test_payload = b'{"level": "ERROR", "service": "web"}'
        
        # process() yields results, so we convert to a list
        result = list(parser.process(test_payload))
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['level'], 'ERROR')
        self.assertEqual(result[0]['service'], 'web')

    def test_parse_invalid_json(self):
        """Tests if the DoFn safely ignores malformed JSON without crashing."""
        parser = ParseLogFn()
        test_payload = b'{malformed_json: true}'
        
        result = list(parser.process(test_payload))
        
        # Should yield nothing if parsing fails
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()
