import pytest
from unittest.mock import patch

from i18n import t

# Sample translation data to use for testing if we need to patch, but
# we can just use the existing translations, or add a fake one to i18n.TRANSLATIONS.
import i18n

def setup_module():
    i18n.TRANSLATIONS["test.greeting"] = {"en": "Hello {name}", "ar": "مرحباً {name}"}
    i18n.TRANSLATIONS["test.fallback"] = {"en": "Only in English"}
    i18n.TRANSLATIONS["test.static"] = {"en": "English Static", "ar": "Arabic Static"}

def teardown_module():
    i18n.TRANSLATIONS.pop("test.greeting", None)
    i18n.TRANSLATIONS.pop("test.fallback", None)
    i18n.TRANSLATIONS.pop("test.static", None)

@patch("i18n.current_lang")
def test_t_known_keys(mock_current_lang):
    mock_current_lang.return_value = "en"
    assert t("test.static") == "English Static"

    mock_current_lang.return_value = "ar"
    assert t("test.static") == "Arabic Static"

@patch("i18n.current_lang")
def test_t_unknown_keys(mock_current_lang):
    mock_current_lang.return_value = "en"
    assert t("this.key.does.not.exist") == "this.key.does.not.exist"

    mock_current_lang.return_value = "ar"
    assert t("this.key.does.not.exist") == "this.key.does.not.exist"

@patch("i18n.current_lang")
def test_t_string_formatting(mock_current_lang):
    mock_current_lang.return_value = "en"
    assert t("test.greeting", name="Jules") == "Hello Jules"

    mock_current_lang.return_value = "ar"
    assert t("test.greeting", name="Jules") == "مرحباً Jules"

@patch("i18n.current_lang")
def test_t_string_formatting_keyerror(mock_current_lang):
    # Pass incorrect kwargs, it should catch KeyError and return the raw string
    mock_current_lang.return_value = "en"
    assert t("test.greeting", wrong_arg="Jules") == "Hello {name}"

    mock_current_lang.return_value = "ar"
    assert t("test.greeting", wrong_arg="Jules") == "مرحباً {name}"

@patch("i18n.current_lang")
def test_t_fallback_to_english(mock_current_lang):
    # Test fallback: language is set to 'ar' but translation only exists in 'en'
    mock_current_lang.return_value = "ar"
    assert t("test.fallback") == "Only in English"
