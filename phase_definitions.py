"""
Data-driven definitions of construction phases.

Each phase entry uses *translation keys* (not raw strings) so the renderer
can switch language at runtime via ``i18n.t()``.

For the v2 MVP we fully define Phase 1-6. Phase 0
is bespoke (multiple tabs) so it lives entirely inside ``phase_views.py``.
"""
from __future__ import annotations

PHASE_ORDER: list[int] = [0, 1, 2, 3, 4, 5, 6]


PHASE_DEFINITIONS: dict[int, dict] = {
    1: {
        "title_key": "phase.1.title",
        "desc_key":  "phase.1.desc",
        "items": [
            {
                "key": "benchmark",
                "label_key": "p1.item.benchmark",
                "requires_image": False,
            },
            {
                "key": "soil_groundwater",
                "label_key": "p1.item.soil",
                "requires_image": False,
                # Red banner shown when the item is FAIL or REWORK.
                "warn_on_fail_key": "p1.item.soil.warn",
            },
            {
                "key": "anti_termite",
                "label_key": "p1.item.termite",
                "requires_image": False,
                # Linkage to the Material Delivery Gate: this item
                # cannot PASS until material 'anti_termite_pesticide'
                # has match_status='MATCH'.
                "material_required": "anti_termite_pesticide",
            },
            {
                "key": "backfill_compaction",
                "label_key": "p1.item.backfill",
                "requires_image": True,
                "image_label_key": "p1.item.backfill.imglabel",
            },
        ],
        "materials": [
            {
                "key": "anti_termite_pesticide",
                "name_key": "mat.antitermite_name",
                "boq_match_name": "Anti-termite Pesticide",
            },
        ],
        "payment_pct": 5.0,
        "payment_label": "Excavation milestone",
    },
    2: {
        "title_key": "phase.2.title",
        "desc_key":  "phase.2.desc",
        "items": [
            {
                "key": "earthing_rods",
                "label_key": "p2.item.earthing",
                "requires_image": True,
                "image_label_key": "p2.item.earthing.imglabel",
            },
            {
                "key": "concrete_cover",
                "label_key": "p2.item.cover",
                "requires_image": False,
            },
            {
                "key": "slump_test",
                "label_key": "p2.item.slump",
                "requires_image": True,
                "image_label_key": "p2.item.slump.imglabel",
            },
            {
                "key": "concrete_type",
                "label_key": "p2.item.concrete_type",
                "requires_image": False,
                "material_required": "ready_mix_concrete",
            },
            {
                "key": "bitumen_double",
                "label_key": "p2.item.bitumen",
                "requires_image": True,
            },
        ],
        "materials": [
            {
                "key": "ready_mix_concrete",
                "name_key": "mat.concrete_name",
                "boq_match_name": "Ready-mix Concrete (SRC, sulfate-resistant)",
            },
            {
                "key": "rebar",
                "name_key": "mat.rebar_name",
                "boq_match_name": "Reinforcement Steel — Ø12 mm",
            },
        ],
        "payment_pct": 15.0,
        "payment_label": "Substructure milestone",
    },
    3: {
        "title_key": "phase.3.title",
        "desc_key":  "phase.3.desc",
        "items": [
            {
                "key": "squaring_alignment",
                "label_key": "p3.item.squaring",
                "requires_image": False,
            },
            {
                "key": "column_plumb",
                "label_key": "p3.item.column_plumb",
                "requires_image": False,
            },
            {
                "key": "mep_sleeves",
                "label_key": "p3.item.mep_sleeves",
                "requires_image": True,
            },
            {
                "key": "steel_mesh_blocks",
                "label_key": "p3.item.mesh_blocks",
                "requires_image": False,
            },
            {
                "key": "lintel_beams",
                "label_key": "p3.item.lintels",
                "requires_image": False,
            },
        ],
        "materials": [
            {
                "key": "blocks_20",
                "name_key": "mat.blocks_name",
                "boq_match_name": "Concrete Blocks — 20 cm",
            },
        ],
        "payment_pct": 15.0,
        "payment_label": "Superstructure milestone",
    },
    4: {
        "title_key": "phase.4.title",
        "desc_key":  "phase.4.desc",
        "items": [
            {
                "key": "no_horizontal_chipping",
                "label_key": "p4.item.no_horizontal_chipping",
                "requires_image": False,
                "warn_on_fail_key": "p4.item.no_horizontal_chipping.warn",
            },
            {
                "key": "megger_test",
                "label_key": "p4.item.megger",
                "requires_image": True,
                "image_label_key": "p4.item.megger.imglabel",
            },
            {
                "key": "water_pressure_test",
                "label_key": "p4.item.water_pressure",
                "requires_image": True,
                "image_label_key": "p4.item.water_pressure.imglabel",
            },
            {
                "key": "drainage_slope",
                "label_key": "p4.item.drainage_slope",
                "requires_image": False,
            },
            {
                "key": "hvac_nitrogen_test",
                "label_key": "p4.item.hvac_nitrogen",
                "requires_image": True,
            },
        ],
        "materials": [
            {
                "key": "pex_pipes",
                "name_key": "mat.pex_name",
                "boq_match_name": "PEX Water Pipe — Ø½″ (cold/hot supply)",
            },
            {
                "key": "elec_cable_2_5",
                "name_key": "mat.cable_name",
                "boq_match_name": "Electrical Cable — 2.5 mm² (lighting/sockets)",
            },
        ],
        "payment_pct": 10.0,
        "payment_label": "MEP rough-in milestone",
    },
    5: {
        "title_key": "phase.5.title",
        "desc_key":  "phase.5.desc",
        "items": [
            {
                "key": "ponding_test",
                "label_key": "p5.item.ponding",
                "requires_image": True,
                "image_label_key": "p5.item.ponding.imglabel",
            },
            {
                "key": "stone_mechanical",
                "label_key": "p5.item.stone_mechanical",
                "requires_image": False,
                "warn_on_fail_key": "p5.item.stone_mechanical.warn",
            },
            {
                "key": "galvanized_mesh_joints",
                "label_key": "p5.item.galv_mesh",
                "requires_image": True,
            },
            {
                "key": "tile_leveling_clips",
                "label_key": "p5.item.tile_clips",
                "requires_image": True,
            },
        ],
        "materials": [
            {
                "key": "roof_membrane",
                "name_key": "mat.roof_membrane_name",
                "boq_match_name": "Roof Waterproofing Membrane (4 mm SBS)",
            },
        ],
        "payment_pct": 25.0,
        "payment_label": "Finishes milestone",
    },
    6: {
        "title_key": "phase.6.title",
        "desc_key":  "phase.6.desc",
        "items": [
            {
                "key": "balady_certificate",
                "label_key": "p6.item.balady",
                "requires_image": True,
                "image_label_key": "p6.item.balady.imglabel",
            },
            {
                "key": "snag_list_cleared",
                "label_key": "p6.item.snags",
                "requires_image": False,
            },
            {
                "key": "warranties_archived",
                "label_key": "p6.item.warranties",
                "requires_image": False,
            },
        ],
        "materials": [],
        "payment_pct": 5.0,
        "payment_label": "Final handover milestone",
    },
}


def previous_phase(phase: int) -> int | None:
    if phase not in PHASE_ORDER:
        return None
    idx = PHASE_ORDER.index(phase)
    return PHASE_ORDER[idx - 1] if idx > 0 else None


def next_phase(phase: int) -> int | None:
    if phase not in PHASE_ORDER:
        return None
    idx = PHASE_ORDER.index(phase)
    return PHASE_ORDER[idx + 1] if idx < len(PHASE_ORDER) - 1 else None
