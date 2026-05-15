import pytest
import i18n
from i18n import translate_boq_item

def test_translate_boq_item_english(monkeypatch):
    monkeypatch.setattr(i18n, "current_lang", lambda: "en")

    # Should return original english name
    assert translate_boq_item("Cement (50 kg bags)") == "Cement (50 kg bags)"
    assert translate_boq_item("Some Unknown Item") == "Some Unknown Item"

def test_translate_boq_item_arabic_translation_exists(monkeypatch):
    monkeypatch.setattr(i18n, "current_lang", lambda: "ar")

    # Exists in TRANSLATIONS ("boq.item.Cement (50 kg bags)")
    assert translate_boq_item("Cement (50 kg bags)") == "إسمنت (أكياس ٥٠ كجم)"

def test_translate_boq_item_arabic_fallback(monkeypatch):
    monkeypatch.setattr(i18n, "current_lang", lambda: "ar")

    # Does not exist in TRANSLATIONS
    assert translate_boq_item("Unknown Special Concrete") == "Unknown Special Concrete"
