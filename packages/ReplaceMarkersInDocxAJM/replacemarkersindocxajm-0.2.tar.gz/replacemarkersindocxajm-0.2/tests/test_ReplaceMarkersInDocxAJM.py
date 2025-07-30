import unittest

import mock
from ReplaceMarkersInDocxAJM.ReplaceMarkersInDocxAJM import ReplaceMarkersInDocx
from re import escape


class ReplaceMarkersInDocxTest(unittest.TestCase):
    info_dict = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3', 'test': 'replacement_text'}
    Document = mock.MagicMock()
    logger = mock.MagicMock()

    def setUp(self):
        self.replaceMarkersInDocx = ReplaceMarkersInDocx(self.Document, self.logger, self.info_dict)

    def test_init(self):
        self.assertTrue(isinstance(self.replaceMarkersInDocx, ReplaceMarkersInDocx))

    def test_standardize_paragraph_style(self):
        with self.assertRaises(NotImplementedError):
            self.replaceMarkersInDocx.standardize_paragraph_style(None)

    def test_info_dict(self):
        self.assertEqual(self.replaceMarkersInDocx.info_dict, self.info_dict)

    def test_get_header_footer_in_section(self):
        section = mock.MagicMock()
        result_headers, result_footers = self.replaceMarkersInDocx._get_header_footer_in_section(section)
        self.assertIsInstance(result_headers, set)
        self.assertIsInstance(result_footers, set)

    def test_fetch_mail_merge_markers(self):
        markers = self.replaceMarkersInDocx._fetch_mail_merge_markers()
        self.assertIsInstance(markers, set)

    def test_mail_merge_markers(self):
        self.assertIsInstance(self.replaceMarkersInDocx.mail_merge_markers, set)

    def test_mail_merge_keys(self):
        self.assertIsInstance(self.replaceMarkersInDocx.mail_merge_keys, set)

    def test_handle_marker_edge_case(self):
        marker = 'marker1'
        paragraph = 'paragraph1'
        replacement_text = 'replacement_text1'
        self.assertEqual(self.replaceMarkersInDocx._handle_marker_edge_case(marker, paragraph, replacement_text),
                         (replacement_text, paragraph))

    def test_replace_matched_marker(self):
        with mock.patch('re.sub') as patched_sub:
            replaced_text = "T replaced with text T"
            patched_sub.return_value = replaced_text
            paragraph = mock.MagicMock()
            paragraph.text = "This is a test"
            marker = "\u00ABtest\u00BB"
            marker_pattern = escape(marker)
            self.replaceMarkersInDocx._replace_matched_marker(paragraph, marker, marker_pattern)
            self.assertEqual(paragraph.text, replaced_text)

    def test_replace_markers_in_paragraph(self):
        paragraph = mock.MagicMock()
        replacement_counter = self.replaceMarkersInDocx._replace_markers_in_paragraph(paragraph)
        self.assertEqual(replacement_counter, 0)

    def test_replace_markers(self):
        paragraph = mock.MagicMock()
        paragraph_dict = {'paragraphs': [paragraph]}
        self.replaceMarkersInDocx.replace_markers(**paragraph_dict)
