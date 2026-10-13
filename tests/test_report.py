"""Protect completed human review and demo links during report regeneration."""
import unittest

from report import preserve_manual_sections


class ReportPreservationTests(unittest.TestCase):
    def test_manual_review_and_demo_survive_without_freezing_other_sections(self):
        existing = ('## Retrieval\nOld results\n\n'
                    '## AI Usage Transparency\nMy completed review.\n\n'
                    '## Demo\n[Video](https://example.com/demo)\n\n'
                    '## Validation\nOld checks\n')
        rendered = ('## Retrieval\nNew results\n\n'
                    '## AI Usage Transparency\nOld TODO\n\n'
                    '## Demo\nURL placeholder\n\n'
                    '## Validation\nNew checks\n')
        result = preserve_manual_sections(rendered, existing)
        self.assertIn('My completed review.', result)
        self.assertIn('[Video](https://example.com/demo)', result)
        self.assertIn('New results', result)
        self.assertIn('New checks', result)
        self.assertNotIn('Old TODO', result)
        self.assertNotIn('Old results', result)

    def test_first_render_keeps_default_sections(self):
        rendered = '## AI Usage Transparency\nRecorded assistance\n\n## Demo\nPending video\n'
        self.assertEqual(preserve_manual_sections(rendered, ''), rendered)


if __name__ == '__main__':
    unittest.main()
