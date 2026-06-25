"""
AI integration placeholders.

Each function returns realistic mock data so the UI is fully exercised.
Replace each implementation with a real model call when integrating
production AI.

Suggested production stack:

* parse_blueprint_pdf  → PyMuPDF / pdfplumber + Anthropic Claude vision
                         (or fine-tuned YOLO) for wall/column/dimension detection.
* estimate_boq         → coefficient engine validated against the
                         Saudi Building Code (SBC 304 / SBC 201).
* review_contract      → text extraction + RAG over MOMRAH templates
                         + LLM clause classifier.
* run_material_match   → OCR the invoice → compare quantities/specs
                         to the BOQ row.
* get_local_weather    → real call to a Saudi weather provider; the
                         hot/humid flag drives SBC curing advice and
                         the recommendation to use SRC concrete.
* query_saudi_building_code → Vector DB (Qdrant/Pinecone) of official SBC
                         PDFs answered with RAG.
"""
from __future__ import annotations

import random
from typing import Any


# ============================ Blueprint & BOQ ==============================
def parse_blueprint_pdf(file_path: str) -> dict[str, Any]:
    """Mock OCR/CV pipeline."""
    return {
        "total_built_area_m2": 320,
        "floors": 2,
        "rooms_detected": 8,
        "structural_elements": {"columns": 24, "beams": 36, "slabs": 2},
    }


# Categories used to group BOQ items in the UI tabs.
CAT_STRUCT  = "structural"   # Concrete, steel, blocks, sand, gravel
CAT_INSUL   = "insulation"   # Thermal, sound, waterproofing
CAT_MEP     = "mep"          # Plumbing, electrical, HVAC
CAT_FINISH  = "finishes"     # Tiles, paint, doors, windows, plaster
CAT_SANI    = "sanitary"     # Toilets, sinks, mixers, water tanks
CAT_ELEC    = "electrical"   # Panels, switches, sockets, lights

# Finish-level multipliers applied to "Finishes" category items.
FINISH_LEVELS = {
    "economic":  {"tile_grade": "Ceramic", "paint_grade": "Standard"},
    "luxury":    {"tile_grade": "Porcelain / Marble",
                  "paint_grade": "Premium washable"},
}


def estimate_boq(
    blueprint_data: dict[str, Any],
    floors: int | None = None,
    finish_level: str = "economic",
) -> list[dict[str, Any]]:
    """Comprehensive BOQ estimator for Saudi residential villas.

    Coefficients are derived from typical 1–3 storey villa builds and the
    Saudi Building Code (SBC). They are intentionally conservative — a real
    licensed engineer must validate them before contract signature.

    Parameters
    ----------
    blueprint_data : dict from ``parse_blueprint_pdf``.
    floors         : override the floor count detected in the blueprint.
                     Use 1 by default if neither blueprint nor caller supplied.
    finish_level   : ``"economic"`` (default) or ``"luxury"``.

    Returns
    -------
    list of {item_name, quantity, unit, category} dicts.
    """
    area = float(blueprint_data.get("total_built_area_m2", 300))
    if floors is None:
        floors = int(blueprint_data.get("floors", 1) or 1)

    # ``ext_area`` (external wall area) is roughly the perimeter * floor
    # height. For a square-ish footprint we approximate perimeter as
    # 4 * sqrt(area-per-floor) and assume 3.2 m per storey.
    per_floor = max(area / max(floors, 1), 1.0)
    ext_area = 4.0 * (per_floor ** 0.5) * 3.2 * floors
    roof_area = per_floor                           # roof = top floor footprint
    floor_finish_area = area * 0.85                 # 85% net finished floor

    luxury = finish_level == "luxury"
    paint_grade = FINISH_LEVELS[finish_level]["paint_grade"]
    tile_grade  = FINISH_LEVELS[finish_level]["tile_grade"]

    # Sanitary fixtures scale with floors (one bathroom per floor + a guest WC).
    bathrooms = max(2, floors + 1)

    # Helper to build a row.
    def row(name: str, qty: float, unit: str, category: str) -> dict:
        return {"item_name": name, "quantity": round(qty, 2),
                "unit": unit, "category": category}

    items: list[dict] = [
        # ================== STRUCTURAL ==================
        row("Ready-mix Concrete (SRC, sulfate-resistant)",
            area * 0.14, "m³", CAT_STRUCT),
        row("Reinforcement Steel — Ø12 mm",
            area * 0.009, "Tons", CAT_STRUCT),
        row("Reinforcement Steel — Ø16 mm",
            area * 0.005, "Tons", CAT_STRUCT),
        row("Reinforcement Steel — Ø8 mm (stirrups)",
            area * 0.003, "Tons", CAT_STRUCT),
        row("Tying Wire (steel)",
            area * 0.0006, "Tons", CAT_STRUCT),
        row("Concrete Blocks — 20 cm",
            area * 12 * floors, "pcs", CAT_STRUCT),
        row("Concrete Blocks — 10 cm (interior partitions)",
            area * 4 * floors, "pcs", CAT_STRUCT),
        row("Cement (50 kg bags)",
            area * 1.4 * floors, "bags", CAT_STRUCT),
        row("Washed Sand",
            area * 0.35, "m³", CAT_STRUCT),
        row("Crushed Gravel (aggregates)",
            area * 0.45, "m³", CAT_STRUCT),
        row("Plywood Formwork",
            area * 1.2, "m²", CAT_STRUCT),
        row("Anti-termite Pesticide",
            area * 1.0, "L", CAT_STRUCT),

        # ================== INSULATION ==================
        row("Bitumen Waterproofing (foundations)",
            area * 0.6, "m²", CAT_INSUL),
        row("Roof Waterproofing Membrane (4 mm SBS)",
            roof_area * 1.10, "m²", CAT_INSUL),
        row("Thermal Insulation — Polystyrene Boards (5 cm)",
            roof_area + ext_area * 0.6, "m²", CAT_INSUL),
        row("Vapor Barrier (PE sheet)",
            roof_area * 1.05, "m²", CAT_INSUL),
        row("Galvanized Mesh (block/concrete joints)",
            ext_area * 0.15, "m²", CAT_INSUL),

        # ================== MEP ==================
        # Plumbing — water supply
        row("PEX Water Pipe — Ø½″ (cold/hot supply)",
            area * 1.8, "m", CAT_MEP),
        row("PEX Water Pipe — Ø¾″ (mains)",
            area * 0.8, "m", CAT_MEP),
        # Plumbing — drainage
        row("uPVC Drain Pipe — Ø4″",
            area * 0.5, "m", CAT_MEP),
        row("uPVC Drain Pipe — Ø2″",
            area * 0.7, "m", CAT_MEP),
        # HVAC
        row("Copper Refrigerant Pipe (split AC lines)",
            bathrooms * 12 + area * 0.05, "m", CAT_MEP),
        row("Insulated AC Duct (flexible)",
            area * 0.25, "m", CAT_MEP),
        # ================== ELECTRICAL ==================
        row("Electrical Cable — 2.5 mm² (lighting/sockets)",
            area * 4.5, "m", CAT_ELEC),
        row("Electrical Cable — 4 mm² (AC circuits)",
            area * 1.8, "m", CAT_ELEC),
        row("Electrical Cable — 6 mm² (mains feeders)",
            area * 0.4, "m", CAT_ELEC),
        row("Conduit (PVC ¾″)",
            area * 6.0, "m", CAT_ELEC),
        row("Junction & Switch Boxes",
            int(area * 0.4), "pcs", CAT_ELEC),
        row("Main Distribution Panel",
            floors, "pcs", CAT_ELEC),
        row("Wall Sockets",
            int(area * 0.2), "pcs", CAT_ELEC),
        row("Light Switches",
            int(area * 0.15), "pcs", CAT_ELEC),
        row("LED Light Fittings",
            int(area * 0.18), "pcs", CAT_ELEC),
        row("Earthing/Grounding Copper Rod (Ø16 mm × 2.4 m)",
            max(2, floors + 1), "pcs", CAT_ELEC),

        # ================== SANITARY ==================
        row("Toilet (WC) Set",
            bathrooms, "pcs", CAT_SANI),
        row("Wash-basin with Pedestal",
            bathrooms, "pcs", CAT_SANI),
        row("Shower / Bath Mixer",
            bathrooms, "pcs", CAT_SANI),
        row("Basin Mixer",
            bathrooms + 1, "pcs", CAT_SANI),
        row("Kitchen Sink (stainless steel)",
            1, "pcs", CAT_SANI),
        row("Polyethylene Water Tank (1000 L)",
            max(1, floors), "pcs", CAT_SANI),
        row("Submersible Water Pump",
            1, "pcs", CAT_SANI),
        row("Electric Water Heater (50 L)",
            bathrooms, "pcs", CAT_SANI),

        # ================== FINISHES ==================
        row(f"Floor Tiles — {tile_grade}",
            floor_finish_area * 1.10, "m²", CAT_FINISH),
        row("Wall Tiles (bathrooms & kitchen)",
            bathrooms * 25 + 20, "m²", CAT_FINISH),
        row("Tile Adhesive",
            (floor_finish_area + bathrooms * 25 + 20) * 5, "kg", CAT_FINISH),
        row("Internal Plaster (cement/sand)",
            ext_area * 0.4 + area * 2.5, "m²", CAT_FINISH),
        row("External Plaster (weather-resistant)",
            ext_area * 0.95, "m²", CAT_FINISH),
        row(f"Interior Paint — {paint_grade} ({'3' if luxury else '2'} coats)",
            area * 3.2, "m²", CAT_FINISH),
        row("Exterior Paint (weather-shield)",
            ext_area * 0.95, "m²", CAT_FINISH),
        row("Gypsum False-Ceiling Panels",
            area * 0.5, "m²", CAT_FINISH),
        row("Wooden Interior Door (with frame)",
            int(area * 0.025) + bathrooms, "pcs", CAT_FINISH),
        row("Aluminum Window (incl. glass)",
            int(area * 0.10), "m²", CAT_FINISH),
        row("Main Entrance Steel/Wood Door",
            1, "pcs", CAT_FINISH),
        row("Stone Cladding for Façade"
            + (" — natural" if luxury else " — manufactured"),
            ext_area * 0.45, "m²", CAT_FINISH),
        row("Mechanical Stone Anchors (stainless steel)",
            ext_area * 0.45 * 4, "pcs", CAT_FINISH),
    ]
    return items


# ============================ Contract review ==============================
REQUIRED_CONTRACT_CLAUSES: dict[str, str] = {
    "penalty_clause":
        "Late-delivery penalty (per Saudi construction practice)",
    "warranty_clause":
        "10-year structural warranty (الضمان العشري)",
    "payment_schedule":
        "Milestone-based payment schedule tied to progress",
    "scope_of_work":
        "Detailed scope of work referencing the BOQ",
    "dispute_resolution":
        "Dispute resolution mechanism (Saudi Center for Commercial Arbitration)",
    "material_specs":
        "Material specifications matching the Saudi Building Code",
    "termination_clause":
        "Termination conditions for both parties",
}


def review_contract(file_path: str) -> dict[str, Any]:
    """Mock contract reviewer. Pretends to find 4 of 7 standard clauses."""
    found = random.sample(list(REQUIRED_CONTRACT_CLAUSES.keys()), 4)
    missing = {k: v for k, v in REQUIRED_CONTRACT_CLAUSES.items() if k not in found}
    risk_level = "HIGH" if len(missing) >= 3 else ("MEDIUM" if missing else "LOW")
    return {
        "found_clauses": found,
        "missing_clauses": missing,
        "risk_level": risk_level,
    }


# ============================ Material delivery ============================
def run_material_match(
    expected_qty: float,
    expected_unit: str,
    delivered_qty: float | None,
    invoice_path: str | None,
    tolerance: float = 0.10,
) -> dict[str, Any]:
    """Mock match check between an uploaded invoice and the BOQ row.

    A real impl would OCR the invoice, normalise units, and run a sanity
    check on the supplier name and product spec. Here we just compare
    quantities within ±10% by default.
    """
    if not invoice_path or delivered_qty is None or delivered_qty <= 0:
        return {"status": "PENDING", "delta_pct": None, "reason": "No invoice / qty supplied."}

    diff = (delivered_qty - expected_qty) / expected_qty
    if abs(diff) <= tolerance:
        return {"status": "MATCH", "delta_pct": diff * 100,
                "reason": f"Within ±{int(tolerance*100)}% of BOQ."}
    return {"status": "MISMATCH", "delta_pct": diff * 100,
            "reason": f"Delivered qty deviates {diff*100:+.1f}% from BOQ."}


# ============================ Vision AI ====================================
def detect_image_defects(image_path: str) -> list[str]:
    return []  # MVP: never reports defects unless wired to a real model


# ============================ Weather ======================================
# Crude lookup table — Saudi cities default to hot/humid coastal in summer.
_HOT_HUMID_CITIES = {
    "jeddah", "yanbu", "jubail", "dammam", "khobar", "jizan",
    "dhahran", "qatif", "rabigh", "duba",
}


def get_local_weather(location: str | None) -> dict[str, Any]:
    """Mock weather lookup. ``hot_humid=True`` triggers the SBC curing advice
    and the SRC concrete recommendation in the UI."""
    if not location:
        return {"hot_humid": False, "temp_c": 28, "humidity": 35,
                "advice_key": None}
    loc = (location or "").strip().lower()
    hot = any(city in loc for city in _HOT_HUMID_CITIES)
    return {
        "hot_humid": hot,
        "temp_c": 42 if hot else 30,
        "humidity": 75 if hot else 40,
        "advice_key": "mat.weather_hot" if hot else None,
    }


# ============================ RAG over SBC =================================
def query_saudi_building_code(question: str) -> str:
    return ("[Placeholder] In production this returns a cited answer "
            "from the Saudi Building Code knowledge base.")
