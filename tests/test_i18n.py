import unittest
from unittest.mock import MagicMock, patch

from i18n import init_lang, LANG_DEFAULT

class TestInitLang(unittest.TestCase):
    @patch('i18n.st.session_state')
    def test_init_lang_not_set(self, mock_session_state):
        # Configure mock to act like a dictionary missing "lang"
        mock_session_state.__contains__.side_effect = lambda k: False if k == "lang" else True

        init_lang()

        self.assertEqual(mock_session_state.lang, LANG_DEFAULT)

    @patch('i18n.st.session_state')
    def test_init_lang_already_set(self, mock_session_state):
        # Configure mock to act like a dictionary that has "lang"
        mock_session_state.__contains__.side_effect = lambda k: True if k == "lang" else False
        mock_session_state.lang = "en"

        init_lang()

        self.assertEqual(mock_session_state.lang, "en")
