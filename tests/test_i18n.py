import pytest
from unittest.mock import patch
import i18n

def test_t_known_key():
    """Test retrieving a known key for the current language."""
    with patch("i18n.current_lang", return_value="en"):
        with patch.dict("i18n.TRANSLATIONS", {"test.key": {"en": "English text", "ar": "Arabic text"}}):
            assert i18n.t("test.key") == "English text"

    with patch("i18n.current_lang", return_value="ar"):
        with patch.dict("i18n.TRANSLATIONS", {"test.key": {"en": "English text", "ar": "Arabic text"}}):
            assert i18n.t("test.key") == "Arabic text"

def test_t_fallback_to_en():
    """Test falling back to English if the translation for the current language is missing."""
    with patch("i18n.current_lang", return_value="ar"):
        with patch.dict("i18n.TRANSLATIONS", {"test.key": {"en": "English text"}}):
            # Missing "ar" should fall back to "en"
            assert i18n.t("test.key") == "English text"

def test_t_missing_key():
    """Test that a completely missing key returns the key itself."""
    with patch("i18n.current_lang", return_value="en"):
        assert i18n.t("unknown.key") == "unknown.key"

def test_t_formatting():
    """Test string formatting with **kwargs."""
    with patch("i18n.current_lang", return_value="en"):
        with patch.dict("i18n.TRANSLATIONS", {"test.format": {"en": "Hello {name}!"}}):
            assert i18n.t("test.format", name="World") == "Hello World!"

def test_t_formatting_missing_kwargs():
    """Test that missing formatting kwargs return the raw string instead of raising an error."""
    with patch("i18n.current_lang", return_value="en"):
        with patch.dict("i18n.TRANSLATIONS", {"test.format": {"en": "Hello {name}!"}}):
            # Passing a random kwarg just so kwargs is true to trigger format, but missing 'name'
            assert i18n.t("test.format", random="kwarg") == "Hello {name}!"

def test_t_formatting_index_error():
    """Test that positional format placeholders handle missing args gracefully (IndexError)."""
    with patch("i18n.current_lang", return_value="en"):
        with patch.dict("i18n.TRANSLATIONS", {"test.format": {"en": "Hello {0}!"}}):
            # Using positional placeholder {0} but only providing kwargs will raise IndexError
            assert i18n.t("test.format", name="World") == "Hello {0}!"
