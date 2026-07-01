"""
Bilingual support (Arabic ↔ English).

Default language is Arabic. The ``t(key)`` helper reads
``st.session_state.lang`` and returns the matching string. Missing keys
fall back to the key name itself, which makes untranslated strings very
visible during development.
"""
from __future__ import annotations

import streamlit as st

LANG_DEFAULT = "ar"
SUPPORTED_LANGS = ("ar", "en")


# ----------------------------------------------------------------------------
# Translation dictionary
# ----------------------------------------------------------------------------
TRANSLATIONS: dict[str, dict[str, str]] = {
    # ----- App-wide -----
    "app.title":      {"en": "Digital Consulting Engineer",
                       "ar": "المستشار الهندسي الرقمي"},
    "app.subtitle":   {"en": "Your gatekeeper against contractor fraud",
                       "ar": "حارسك ضد التلاعب من المقاول"},
    "app.welcome.h":  {"en": "Welcome",
                       "ar": "مرحبًا بك"},
    "app.welcome.body": {
        "en": "Create your first project from the sidebar to get started.",
        "ar": "أنشئ أول مشروع لك من القائمة الجانبية لتبدأ."},

    # ----- Sidebar / Navigation -----
    "nav.lang":           {"en": "Language", "ar": "اللغة"},
    "nav.active_project": {"en": "Active project", "ar": "المشروع النشط"},
    "nav.no_projects":    {"en": "No projects yet. Create one below.",
                           "ar": "لا توجد مشاريع بعد. أنشئ مشروعاً أدناه."},
    "nav.new_project":    {"en": "➕ New project", "ar": "➕ مشروع جديد"},
    "nav.project_name":   {"en": "Project name", "ar": "اسم المشروع"},
    "nav.project_budget": {"en": "Total budget (SAR)",
                           "ar": "الميزانية الإجمالية (ر.س)"},
    "nav.project_loc":    {"en": "Location (city)", "ar": "الموقع (المدينة)"},
    "nav.create":         {"en": "Create", "ar": "إنشاء"},
    "nav.phases":         {"en": "Phases", "ar": "المراحل"},
    "nav.payment_ledger": {"en": "Payment ledger", "ar": "سجل الدفعات"},
    "nav.no_payments":    {"en": "No payments released yet.",
                           "ar": "لم تُصرف أي دفعات بعد."},
    "nav.certificates":   {"en": "Payment certificates",
                           "ar": "شهادات الدفع"},
    "nav.delete_project": {"en": "🗑️ Delete this project",
                           "ar": "🗑️ حذف هذا المشروع"},
    "nav.confirm_delete": {"en": "Type the project name to confirm:",
                           "ar": "اكتب اسم المشروع للتأكيد:"},
    "nav.confirm_delete_btn": {"en": "Confirm permanent deletion",
                               "ar": "تأكيد الحذف النهائي"},
    "nav.delete_warning": {"en": "⚠️ This permanently deletes the project and all its checklists, photos, and payment records.",
                           "ar": "⚠️ هذا يحذف المشروع نهائياً مع جميع البنود والصور وسجلات الدفع."},
    "nav.deleted":        {"en": "Project deleted.",
                           "ar": "تم حذف المشروع."},
    "nav.name_mismatch":  {"en": "The name you typed doesn't match. Deletion cancelled for safety.",
                           "ar": "الاسم المُدخل لا يطابق اسم المشروع. تم إلغاء الحذف للسلامة."},

    # ----- Header / progress -----
    "hdr.budget":      {"en": "Budget (SAR)", "ar": "الميزانية (ر.س)"},
    "hdr.last_phase":  {"en": "Last approved phase", "ar": "آخر مرحلة معتمدة"},
    "hdr.released":    {"en": "Released (% of budget)",
                        "ar": "المصروف (% من الميزانية)"},
    "hdr.progress":    {"en": "Project progress", "ar": "تقدم المشروع"},

    # ----- Phase short names (used in progress bar) -----
    "phase.0.short": {"en": "P0", "ar": "م٠"},
    "phase.1.short": {"en": "P1", "ar": "م١"},
    "phase.2.short": {"en": "P2", "ar": "م٢"},
    "phase.3.short": {"en": "P3", "ar": "م٣"},
    "phase.4.short": {"en": "P4", "ar": "م٤"},
    "phase.5.short": {"en": "P5", "ar": "م٥"},
    "phase.6.short": {"en": "P6", "ar": "م٦"},

    # ----- Phase titles -----
    "phase.0.title": {"en": "Phase 0 · Initiation & Planning",
                      "ar": "المرحلة ٠ · بدء وتخطيط المشروع"},
    "phase.0.desc":  {"en": "Blueprints, BOQ, contract review, and site preparation.",
                      "ar": "المخططات، جدول الكميات، مراجعة العقد، وتجهيز الموقع."},
    "phase.1.title": {"en": "Phase 1 · Surveying, Excavation & Backfill",
                      "ar": "المرحلة ١ · المساحة والحفر والردم"},
    "phase.1.desc":  {"en": "Establish elevation, inspect soil, treat against termites, compact backfill.",
                      "ar": "إثبات المنسوب، فحص التربة، العلاج ضد النمل الأبيض، ودك الردم."},
    "phase.2.title": {"en": "Phase 2 · Substructure & QA Testing",
                      "ar": "المرحلة ٢ · البنية التحتية واختبارات الجودة"},
    "phase.2.desc":  {"en": "Foundation steel, concrete pour, slump and cube tests, waterproofing.",
                      "ar": "حديد الأساسات، صب الخرسانة، اختبارات الهبوط والمكعبات، والعزل المائي."},
    "phase.3.title": {"en": "Phase 3 · Superstructure",
                      "ar": "المرحلة ٣ · الهيكل العلوي"},
    "phase.3.desc":  {"en": "Columns, slabs, blockwork, and lintel beams.",
                      "ar": "الأعمدة، الأسقف، البلوك، وكمرات اللينتل."},
    "phase.4.title": {"en": "Phase 4 · MEP Advanced Testing",
                      "ar": "المرحلة ٤ · اختبارات الكهروميكانيكية المتقدمة"},
    "phase.4.desc":  {"en": "Plumbing, electrical, and HVAC testing before plastering.",
                      "ar": "اختبارات السباكة والكهرباء والتكييف قبل اللياسة."},
    "phase.5.title": {"en": "Phase 5 · Finishes & Exteriors",
                      "ar": "المرحلة ٥ · التشطيبات والواجهات"},
    "phase.5.desc":  {"en": "Roof waterproofing, stone façades, plastering, flooring.",
                      "ar": "عزل الأسطح، حجر الواجهات، اللياسة، تركيب الأرضيات."},
    "phase.6.title": {"en": "Phase 6 · Closing & Handover",
                      "ar": "المرحلة ٦ · الإغلاق والتسليم"},
    "phase.6.desc":  {"en": "Snag list, warranties archive, and Balady occupancy certificate.",
                      "ar": "قائمة الملاحظات، حفظ الضمانات، وشهادة إشغال البلدي."},

    # ----- Status -----
    "status.pending": {"en": "Pending",   "ar": "قيد الانتظار"},
    "status.pass":    {"en": "Pass",      "ar": "ناجح"},
    "status.fail":    {"en": "Fail",      "ar": "فاشل"},
    "status.rework":  {"en": "In rework", "ar": "إعادة عمل"},

    # ----- Common buttons -----
    "btn.save":        {"en": "💾 Save",                "ar": "💾 حفظ"},
    "btn.upload":      {"en": "Upload",                 "ar": "رفع"},
    "btn.mark_pass":   {"en": "✅ Mark PASS",           "ar": "✅ تأكيد الإنجاز"},
    "btn.mark_fail":   {"en": "❌ Mark FAIL",           "ar": "❌ تسجيل فشل"},
    "btn.start_rework":{"en": "🔧 Start Rework / Re-submit",
                        "ar": "🔧 بدء إعادة العمل / إعادة الإرسال"},
    "btn.reset":       {"en": "Reset to Pending",       "ar": "إعادة إلى قيد الانتظار"},
    "btn.approve":     {"en": "✅ Approve phase & release payment",
                        "ar": "✅ اعتماد المرحلة وصرف الدفعة"},
    "btn.download_cert":{"en": "📄 Download certificate",
                         "ar": "📄 تنزيل الشهادة"},

    # ----- Common alerts -----
    "alert.locked": {"en": "Phase {phase} is locked. Approve Phase {prev} first.",
                     "ar": "المرحلة {phase} مغلقة. اعتمد المرحلة {prev} أولًا."},
    "alert.image_required":   {"en": "An image is required to PASS this item.",
                               "ar": "يلزم رفع صورة لاعتماد هذا البند."},
    "alert.material_required":{"en": "Material delivery must MATCH the BOQ before this item can PASS.",
                               "ar": "يجب أن تطابق فاتورة التوريد جدول الكميات قبل اعتماد هذا البند."},
    "alert.fail_explain":     {"en": "This item failed. After fixing on site, click Re-submit to start the rework cycle.",
                               "ar": "تم تسجيل فشل لهذا البند. بعد المعالجة في الموقع، اضغط إعادة الإرسال لبدء دورة إعادة العمل."},
    "alert.rework_in_progress":{"en": "Rework cycle #{n} in progress. Upload new proof, then mark PASS.",
                                "ar": "جارية دورة إعادة العمل رقم {n}. ارفع دليلًا جديدًا ثم اعتمد البند."},
    "alert.outstanding":      {"en": "Outstanding items before this phase can be approved:",
                               "ar": "البنود المتبقية قبل اعتماد المرحلة:"},
    "alert.all_passed":       {"en": "All checklist items passed and proofs uploaded.",
                               "ar": "جميع البنود اعتُمدت وتم رفع جميع الإثباتات."},
    "alert.cert_issued":      {"en": "Payment certificate {no} issued for {pct:.0f}% of the budget.",
                               "ar": "تم إصدار شهادة الدفع {no} بنسبة {pct:.0f}٪ من الميزانية."},

    # ----- Phase 0 -----
    "p0.tab.bp":        {"en": "📐 Blueprints & BOQ",
                         "ar": "📐 المخططات وجدول الكميات"},
    "p0.tab.contract":  {"en": "📜 Contract Review",
                         "ar": "📜 مراجعة العقد"},
    "p0.tab.siteprep":  {"en": "🏗️ Site Preparation",
                         "ar": "🏗️ تجهيز الموقع"},
    "p0.tab.signoff":   {"en": "✅ Sign-off",
                         "ar": "✅ الاعتماد"},
    "p0.bp.heading":    {"en": "Upload approved blueprints (PDF)",
                         "ar": "ارفع المخططات المعتمدة (PDF)"},
    "p0.bp.upload_label":{"en": "Blueprint PDF", "ar": "ملف المخطط (PDF)"},
    "p0.bp.save_btn":   {"en": "Save blueprint & generate BOQ",
                         "ar": "حفظ المخطط وتوليد جدول الكميات"},
    "p0.bp.generating": {"en": "Parsing blueprint and generating BOQ…",
                         "ar": "جارٍ قراءة المخطط وتوليد جدول الكميات…"},
    "p0.bp.saved":      {"en": "Blueprint saved and BOQ generated.",
                         "ar": "تم حفظ المخطط وتوليد جدول الكميات."},
    "p0.boq.heading":   {"en": "Estimated Bill of Quantities (BOQ)",
                         "ar": "جدول الكميات التقديري"},
    "p0.boq.disclaimer":{"en": "AI-generated estimate. A licensed engineer must validate it before signing the contract.",
                         "ar": "تقدير من الذكاء الاصطناعي. يجب أن يتحقق منه مهندس معتمد قبل توقيع العقد."},
    "p0.boq.empty":     {"en": "No BOQ yet. Upload a blueprint above to generate one.",
                         "ar": "لا يوجد جدول كميات بعد. ارفع مخططًا أعلاه لتوليده."},
    "p0.boq.col_item":  {"en": "Item", "ar": "البند"},
    "p0.boq.col_qty":   {"en": "Quantity", "ar": "الكمية"},
    "p0.boq.col_unit":  {"en": "Unit", "ar": "الوحدة"},

    # ----- BOQ category tabs -----
    "boq.cat.structural":  {"en": "🏗️ Structural",
                            "ar": "🏗️ الإنشائي"},
    "boq.cat.insulation":  {"en": "🛡️ Insulation",
                            "ar": "🛡️ العزل"},
    "boq.cat.mep":         {"en": "🔧 Plumbing & HVAC",
                            "ar": "🔧 السباكة والتكييف"},
    "boq.cat.electrical":  {"en": "⚡ Electrical",
                            "ar": "⚡ الكهرباء"},
    "boq.cat.sanitary":    {"en": "🚿 Sanitary",
                            "ar": "🚿 الأدوات الصحية"},
    "boq.cat.finishes":    {"en": "🎨 Finishes",
                            "ar": "🎨 التشطيبات"},

    # ----- BOQ controls (floors + finish level) -----
    "boq.floors":          {"en": "Floors",
                            "ar": "عدد الأدوار"},
    "boq.finish_level":    {"en": "Finish level",
                            "ar": "مستوى التشطيب"},
    "boq.finish.economic": {"en": "Economic (mid-market)",
                            "ar": "اقتصادي (سكن متوسط)"},
    "boq.finish.luxury":   {"en": "Luxury (marble, natural stone)",
                            "ar": "سوبر لوكس (رخام، حجر طبيعي)"},
    "boq.regenerate":      {"en": "🔄 Regenerate BOQ with these settings",
                            "ar": "🔄 إعادة توليد جدول الكميات بهذه الإعدادات"},
    "boq.summary":         {"en": "Total items: {n} across {c} categories.",
                            "ar": "إجمالي البنود: {n} موزعة على {c} فئات."},
    "boq.export_xlsx":     {"en": "📥 Download BOQ as Excel (single file)",
                            "ar": "📥 تنزيل جدول الكميات كملف Excel واحد"},

    # ----- Excel workbook sheet names + headings -----
    "xlsx.summary.title":     {"en": "Summary", "ar": "الملخص"},
    "xlsx.summary.heading":   {"en": "Bill of Quantities — Summary",
                               "ar": "جدول الكميات — ملخص"},
    "xlsx.summary.subtitle":  {"en": "Project: {name}",
                               "ar": "المشروع: {name}"},
    "xlsx.summary.generated": {"en": "Generated: {when}",
                               "ar": "تاريخ التوليد: {when}"},
    "xlsx.summary.col_label": {"en": "Field",   "ar": "البند"},
    "xlsx.summary.col_value": {"en": "Value",   "ar": "القيمة"},
    "xlsx.summary.breakdown": {"en": "Items per category",
                               "ar": "البنود حسب الفئة"},
    "xlsx.summary.col_category": {"en": "Category", "ar": "الفئة"},
    "xlsx.summary.col_count":    {"en": "Number of items",
                                  "ar": "عدد البنود"},
    "xlsx.summary.total":     {"en": "TOTAL",  "ar": "الإجمالي"},
    "xlsx.cat.subtitle":      {"en": "{n} items in this category",
                               "ar": "عدد البنود في هذه الفئة: {n}"},

    # ----- BOQ item names (Arabic translations of the canonical English keys) -----
    "boq.item.Ready-mix Concrete (SRC, sulfate-resistant)":
        {"en": "Ready-mix Concrete (SRC, sulfate-resistant)",
         "ar": "خرسانة جاهزة (SRC مقاومة للكبريتات)"},
    "boq.item.Reinforcement Steel — Ø12 mm":
        {"en": "Reinforcement Steel — Ø12 mm",
         "ar": "حديد تسليح — قطر ١٢ مم"},
    "boq.item.Reinforcement Steel — Ø16 mm":
        {"en": "Reinforcement Steel — Ø16 mm",
         "ar": "حديد تسليح — قطر ١٦ مم"},
    "boq.item.Reinforcement Steel — Ø8 mm (stirrups)":
        {"en": "Reinforcement Steel — Ø8 mm (stirrups)",
         "ar": "حديد تسليح — قطر ٨ مم (كانات)"},
    "boq.item.Tying Wire (steel)":
        {"en": "Tying Wire (steel)",
         "ar": "سلك ربط (فولاذي)"},
    "boq.item.Concrete Blocks — 20 cm":
        {"en": "Concrete Blocks — 20 cm",
         "ar": "بلوك خرساني — ٢٠ سم"},
    "boq.item.Concrete Blocks — 10 cm (interior partitions)":
        {"en": "Concrete Blocks — 10 cm (interior partitions)",
         "ar": "بلوك خرساني — ١٠ سم (قواطع داخلية)"},
    "boq.item.Cement (50 kg bags)":
        {"en": "Cement (50 kg bags)",
         "ar": "إسمنت (أكياس ٥٠ كجم)"},
    "boq.item.Washed Sand":
        {"en": "Washed Sand",
         "ar": "رمل مغسول"},
    "boq.item.Crushed Gravel (aggregates)":
        {"en": "Crushed Gravel (aggregates)",
         "ar": "حصى مكسر (ركام)"},
    "boq.item.Plywood Formwork":
        {"en": "Plywood Formwork",
         "ar": "خشب طبلية للصبّ"},
    "boq.item.Anti-termite Pesticide":
        {"en": "Anti-termite Pesticide",
         "ar": "مبيد النمل الأبيض"},

    "boq.item.Bitumen Waterproofing (foundations)":
        {"en": "Bitumen Waterproofing (foundations)",
         "ar": "عزل مائي بيتوميني (للقواعد)"},
    "boq.item.Roof Waterproofing Membrane (4 mm SBS)":
        {"en": "Roof Waterproofing Membrane (4 mm SBS)",
         "ar": "غشاء عزل سطح ٤ مم (SBS)"},
    "boq.item.Thermal Insulation — Polystyrene Boards (5 cm)":
        {"en": "Thermal Insulation — Polystyrene Boards (5 cm)",
         "ar": "عزل حراري — ألواح فلين (٥ سم)"},
    "boq.item.Vapor Barrier (PE sheet)":
        {"en": "Vapor Barrier (PE sheet)",
         "ar": "حاجز بخار (شرائح بولي إيثيلين)"},
    "boq.item.Galvanized Mesh (block/concrete joints)":
        {"en": "Galvanized Mesh (block/concrete joints)",
         "ar": "شبك جلفنة (لوصلات البلوك/الخرسانة)"},

    "boq.item.PEX Water Pipe — Ø½″ (cold/hot supply)":
        {"en": "PEX Water Pipe — Ø½″ (cold/hot supply)",
         "ar": "مواسير PEX — ½ بوصة (مياه باردة/حارة)"},
    "boq.item.PEX Water Pipe — Ø¾″ (mains)":
        {"en": "PEX Water Pipe — Ø¾″ (mains)",
         "ar": "مواسير PEX — ¾ بوصة (الخط الرئيسي)"},
    "boq.item.uPVC Drain Pipe — Ø4″":
        {"en": "uPVC Drain Pipe — Ø4″",
         "ar": "مواسير صرف uPVC — ٤ بوصة"},
    "boq.item.uPVC Drain Pipe — Ø2″":
        {"en": "uPVC Drain Pipe — Ø2″",
         "ar": "مواسير صرف uPVC — ٢ بوصة"},
    "boq.item.Copper Refrigerant Pipe (split AC lines)":
        {"en": "Copper Refrigerant Pipe (split AC lines)",
         "ar": "مواسير نحاس للتكييف (سبليت)"},
    "boq.item.Insulated AC Duct (flexible)":
        {"en": "Insulated AC Duct (flexible)",
         "ar": "دكت تكييف معزول (مرن)"},

    "boq.item.Electrical Cable — 2.5 mm² (lighting/sockets)":
        {"en": "Electrical Cable — 2.5 mm² (lighting/sockets)",
         "ar": "كابل كهرباء — ٢٫٥ مم² (إنارة وأفياش)"},
    "boq.item.Electrical Cable — 4 mm² (AC circuits)":
        {"en": "Electrical Cable — 4 mm² (AC circuits)",
         "ar": "كابل كهرباء — ٤ مم² (دوائر التكييف)"},
    "boq.item.Electrical Cable — 6 mm² (mains feeders)":
        {"en": "Electrical Cable — 6 mm² (mains feeders)",
         "ar": "كابل كهرباء — ٦ مم² (المغذيات الرئيسية)"},
    "boq.item.Conduit (PVC ¾″)":
        {"en": "Conduit (PVC ¾″)",
         "ar": "ماسورة كهرباء PVC ¾ بوصة"},
    "boq.item.Junction & Switch Boxes":
        {"en": "Junction & Switch Boxes",
         "ar": "علب توزيع ومفاتيح"},
    "boq.item.Main Distribution Panel":
        {"en": "Main Distribution Panel",
         "ar": "لوحة توزيع رئيسية"},
    "boq.item.Wall Sockets":
        {"en": "Wall Sockets",
         "ar": "أفياش جدارية"},
    "boq.item.Light Switches":
        {"en": "Light Switches",
         "ar": "مفاتيح إنارة"},
    "boq.item.LED Light Fittings":
        {"en": "LED Light Fittings",
         "ar": "تركيبات إنارة LED"},
    "boq.item.Earthing/Grounding Copper Rod (Ø16 mm × 2.4 m)":
        {"en": "Earthing/Grounding Copper Rod (Ø16 mm × 2.4 m)",
         "ar": "قضيب تأريض نحاسي (١٦ مم × ٢٫٤ م)"},

    "boq.item.Toilet (WC) Set":
        {"en": "Toilet (WC) Set",
         "ar": "كرسي حمام (طقم)"},
    "boq.item.Wash-basin with Pedestal":
        {"en": "Wash-basin with Pedestal",
         "ar": "مغسلة بقاعدة"},
    "boq.item.Shower / Bath Mixer":
        {"en": "Shower / Bath Mixer",
         "ar": "خلاط دش / حوض"},
    "boq.item.Basin Mixer":
        {"en": "Basin Mixer",
         "ar": "خلاط مغسلة"},
    "boq.item.Kitchen Sink (stainless steel)":
        {"en": "Kitchen Sink (stainless steel)",
         "ar": "حوض مطبخ (ستانلس ستيل)"},
    "boq.item.Polyethylene Water Tank (1000 L)":
        {"en": "Polyethylene Water Tank (1000 L)",
         "ar": "خزان مياه بولي إيثيلين (١٠٠٠ لتر)"},
    "boq.item.Submersible Water Pump":
        {"en": "Submersible Water Pump",
         "ar": "مضخة مياه غاطسة"},
    "boq.item.Electric Water Heater (50 L)":
        {"en": "Electric Water Heater (50 L)",
         "ar": "سخان كهربائي (٥٠ لتر)"},

    "boq.item.Floor Tiles — Ceramic":
        {"en": "Floor Tiles — Ceramic",
         "ar": "بلاط أرضيات — سيراميك"},
    "boq.item.Floor Tiles — Porcelain / Marble":
        {"en": "Floor Tiles — Porcelain / Marble",
         "ar": "بلاط أرضيات — بورسلين / رخام"},
    "boq.item.Wall Tiles (bathrooms & kitchen)":
        {"en": "Wall Tiles (bathrooms & kitchen)",
         "ar": "بلاط جدران (حمامات ومطابخ)"},
    "boq.item.Tile Adhesive":
        {"en": "Tile Adhesive",
         "ar": "لاصق بلاط"},
    "boq.item.Internal Plaster (cement/sand)":
        {"en": "Internal Plaster (cement/sand)",
         "ar": "ملاط داخلي (إسمنت/رمل)"},
    "boq.item.External Plaster (weather-resistant)":
        {"en": "External Plaster (weather-resistant)",
         "ar": "ملاط خارجي (مقاوم للعوامل الجوية)"},
    "boq.item.Interior Paint — Standard (2 coats)":
        {"en": "Interior Paint — Standard (2 coats)",
         "ar": "دهان داخلي — عادي (طبقتان)"},
    "boq.item.Interior Paint — Premium washable (3 coats)":
        {"en": "Interior Paint — Premium washable (3 coats)",
         "ar": "دهان داخلي — قابل للغسل ممتاز (٣ طبقات)"},
    "boq.item.Exterior Paint (weather-shield)":
        {"en": "Exterior Paint (weather-shield)",
         "ar": "دهان خارجي (مقاوم للجو)"},
    "boq.item.Gypsum False-Ceiling Panels":
        {"en": "Gypsum False-Ceiling Panels",
         "ar": "ألواح أسقف معلقة جبس"},
    "boq.item.Wooden Interior Door (with frame)":
        {"en": "Wooden Interior Door (with frame)",
         "ar": "باب داخلي خشبي (مع الإطار)"},
    "boq.item.Aluminum Window (incl. glass)":
        {"en": "Aluminum Window (incl. glass)",
         "ar": "شباك ألمنيوم (شامل الزجاج)"},
    "boq.item.Main Entrance Steel/Wood Door":
        {"en": "Main Entrance Steel/Wood Door",
         "ar": "باب مدخل رئيسي (حديد/خشب)"},
    "boq.item.Stone Cladding for Façade — natural":
        {"en": "Stone Cladding for Façade — natural",
         "ar": "حجر واجهات — طبيعي"},
    "boq.item.Stone Cladding for Façade — manufactured":
        {"en": "Stone Cladding for Façade — manufactured",
         "ar": "حجر واجهات — صناعي"},
    "boq.item.Mechanical Stone Anchors (stainless steel)":
        {"en": "Mechanical Stone Anchors (stainless steel)",
         "ar": "مثبتات حجر ميكانيكية (ستانلس ستيل)"},

    "p0.contract.heading": {"en": "Upload contractor agreement",
                            "ar": "ارفع عقد المقاول"},
    "p0.contract.skip":    {"en": "I don't have a formal contract yet — skip this step",
                            "ar": "لا يوجد لدي عقد رسمي بعد — تخطي هذه الخطوة"},
    "p0.contract.skip_warn":{"en": "⚠️ You skipped the contract review. This is risky — a written contract with clear penalty clauses is your strongest defense against fraud. Add one as soon as possible.",
                             "ar": "⚠️ لقد تخطيت مراجعة العقد. هذا مخاطرة كبيرة — العقد المكتوب بشروط جزائية واضحة هو أقوى حمايتك من التلاعب. أضف عقدًا في أقرب وقت ممكن."},
    "p0.contract.upload_label": {"en": "Contract PDF",
                                 "ar": "ملف العقد (PDF)"},
    "p0.contract.analyze_btn":  {"en": "Analyze contract",
                                 "ar": "تحليل العقد"},
    "p0.contract.analyzing":    {"en": "Reviewing contract against the Saudi Building Code…",
                                 "ar": "جارٍ مراجعة العقد وفق كود البناء السعودي…"},
    "p0.contract.high_risk":    {"en": "Risk level: HIGH. Missing clauses detected:",
                                 "ar": "مستوى المخاطرة: مرتفع. توجد بنود ناقصة:"},
    "p0.contract.no_risk":      {"en": "All standard clauses are present.",
                                 "ar": "جميع البنود الأساسية موجودة."},
    "p0.contract.accept":       {"en": "I have read the warnings above and accept the residual risk.",
                                 "ar": "قرأت التحذيرات أعلاه وأقبل المخاطر المتبقية."},
    "p0.contract.current":      {"en": "Current contract on file:",
                                 "ar": "العقد المحفوظ حاليًا:"},

    "p0.siteprep.heading":  {"en": "Site preparation gate",
                             "ar": "بوابة تجهيز الموقع"},
    "p0.siteprep.fencing":  {"en": "Site hoarding / fencing installed all around the plot",
                             "ar": "تم تركيب السور حول كامل الموقع"},
    "p0.siteprep.board":    {"en": "Municipality information board installed",
                             "ar": "تم تركيب لوحة معلومات البلدية"},
    "p0.siteprep.upload":   {"en": "Upload photo proof",
                             "ar": "ارفع صورة الإثبات"},

    "p0.signoff.heading":   {"en": "Phase 0 sign-off checklist",
                             "ar": "قائمة اعتماد المرحلة ٠"},
    "p0.signoff.bp_done":   {"en": "Blueprint uploaded & BOQ generated",
                             "ar": "تم رفع المخطط وتوليد جدول الكميات"},
    "p0.signoff.contract_done":{"en": "Contract uploaded, analyzed and risks accepted",
                                "ar": "تم رفع العقد وتحليله وقبول المخاطر"},
    "p0.signoff.siteprep_done":{"en": "Site fencing AND municipality board photos uploaded",
                                "ar": "تم رفع صورتَي السور ولوحة البلدية"},
    "p0.signoff.approve":   {"en": "✅ Approve Phase 0 and unlock Phase 1",
                             "ar": "✅ اعتماد المرحلة ٠ وفتح المرحلة ١"},
    "p0.signoff.approved":  {"en": "Phase 0 approved. Phase 1 is now unlocked.",
                             "ar": "تم اعتماد المرحلة ٠. أصبحت المرحلة ١ متاحة."},
    "p0.signoff.incomplete":{"en": "Complete the steps above to unlock Phase 1.",
                             "ar": "أكمل الخطوات أعلاه لفتح المرحلة ١."},

    # ----- Phase 1 checklist labels -----
    "p1.item.benchmark":   {"en": "Benchmark elevation established (foundation tied to street level)",
                            "ar": "تم إثبات منسوب الموقع (ربط الأساس بمنسوب الشارع)"},
    "p1.item.soil":        {"en": "Soil inspected — solid/virgin, no groundwater (or dewatering pumps in use)",
                            "ar": "تم فحص التربة — صلبة وغير ردمية، ولا توجد مياه جوفية (أو يتم استخدام مضخات السحب)"},
    "p1.item.soil.warn":   {"en": "🚨 Groundwater requires dewatering pumps before any concrete work. Stop and consult a structural engineer.",
                            "ar": "🚨 وجود مياه جوفية يستوجب استخدام مضخات السحب قبل أي خرسانة. توقف واستشر مهندساً إنشائياً."},
    "p1.item.termite":     {"en": "Anti-termite treatment applied (invoice already verified in Material Gate)",
                            "ar": "تم رش المبيد ضد النمل الأبيض (تم التحقق من الفاتورة في بوابة المواد)"},
    "p1.item.backfill":    {"en": "Backfill done in 30 cm layers AND compaction lab test > 95%",
                            "ar": "تم الردم على طبقات ٣٠ سم ودك مخبري > ٩٥٪"},
    "p1.item.backfill.imglabel":{"en": "Upload the lab compaction report",
                                 "ar": "ارفع تقرير الدك المخبري"},

    # ----- Phase 2 checklist labels -----
    "p2.item.earthing":     {"en": "Earthing/Grounding copper rods installed BEFORE pouring concrete",
                             "ar": "تم تركيب قضبان التأريض النحاسية قبل صب الخرسانة"},
    "p2.item.earthing.imglabel":{"en": "Photo of installed earthing rods",
                                 "ar": "صورة قضبان التأريض المركّبة"},
    "p2.item.cover":        {"en": "Concrete cover (biscuits/spacers) is 5–7 cm",
                             "ar": "غطاء الخرسانة (البسكوت) ٥–٧ سم"},
    "p2.item.slump":        {"en": "Slump test performed on site, and cubes taken for 7-day & 28-day strength tests",
                             "ar": "تم اختبار الهبوط في الموقع، وأخذ مكعبات لاختبار المقاومة بعد ٧ و ٢٨ يوماً"},
    "p2.item.slump.imglabel":{"en": "Photo of slump cone & cube samples",
                              "ar": "صورة مخروط الهبوط وعينات المكعبات"},
    "p2.item.concrete_type":{"en": "Concrete type matches BOQ specs (sulfate-resistant SRC) — invoice verified in Material Gate",
                             "ar": "نوع الخرسانة مطابق لمواصفات الجدول (SRC مقاومة للكبريتات) — الفاتورة مُتحقَّق منها في بوابة المواد"},
    "p2.item.bitumen":      {"en": "Bitumen waterproofing applied in two coats on foundations & retaining walls",
                             "ar": "تم دهان مادة البيتومين كعزل مائي على طبقتين للأساسات وجدران الدعم"},

    # ----- Phase 3 checklist labels -----
    "p3.item.squaring":     {"en": "Rooms squared at 90° using string lines (Pythagorean check 3-4-5)",
                             "ar": "تم التأكد من تعامد الغرف ٩٠° بالخيوط (قاعدة فيثاغورس ٣-٤-٥)"},
    "p3.item.column_plumb": {"en": "Column formwork checked for verticality with plumb bob",
                             "ar": "تم فحص شاكول الأعمدة للتأكد من العمودية"},
    "p3.item.mep_sleeves":  {"en": "MEP sleeves planted in slab BEFORE pouring concrete",
                             "ar": "تم تثبيت أكمام MEP في السقف قبل صب الخرسانة"},
    "p3.item.mesh_blocks":  {"en": "Steel mesh installed every 3 block layers (anti-cracking)",
                             "ar": "تم تركيب شبك حديد كل ٣ مدامك بلوك (لمنع التشققات)"},
    "p3.item.lintels":      {"en": "Lintel beams cast over every door and window opening",
                             "ar": "تم صب كمرات لينتل فوق كل فتحات الأبواب والشبابيك"},

    # ----- Phase 4 checklist labels -----
    "p4.item.no_horizontal_chipping":
        {"en": "No horizontal chipping/grooves cut in block walls (vertical only)",
         "ar": "لا يوجد كسر أفقي في جدران البلوك (التقطيع رأسي فقط)"},
    "p4.item.no_horizontal_chipping.warn":
        {"en": "🚨 Horizontal chipping severely weakens load-bearing walls and is FORBIDDEN by SBC. Reject any such grooves on site immediately.",
         "ar": "🚨 الكسر الأفقي يُضعف الجدران الحاملة بشدة وممنوع وفق كود البناء السعودي. ارفض أي تقطيع أفقي في الموقع فوراً."},
    "p4.item.megger":       {"en": "Electrical Megger Test (insulation resistance) passed (≥ 1 MΩ)",
                             "ar": "اجتاز اختبار الميجر الكهربائي (مقاومة العزل ≥ ١ ميجا أوم)"},
    "p4.item.megger.imglabel":{"en": "Megger test report",
                               "ar": "تقرير اختبار الميجر"},
    "p4.item.water_pressure":{"en": "Plumbing water-pressure test passed (15 bar held for 24 h)",
                              "ar": "اجتاز اختبار ضغط مياه السباكة (١٥ بار لمدة ٢٤ ساعة)"},
    "p4.item.water_pressure.imglabel":{"en": "Photo of pressure gauge after 24 h",
                                       "ar": "صورة عداد الضغط بعد ٢٤ ساعة"},
    "p4.item.drainage_slope":{"en": "Drainage pipes slope verified at 1 cm per 1 m (1%)",
                              "ar": "تم التحقق من ميل أنابيب الصرف بمعدل ١ سم لكل ١ متر (١٪)"},
    "p4.item.hvac_nitrogen":{"en": "HVAC copper pipes pressure-tested for leaks with nitrogen",
                             "ar": "تم اختبار ضغط أنابيب التكييف النحاسية بغاز النيتروجين للتأكد من عدم التسرب"},

    # ----- Phase 5 checklist labels -----
    "p5.item.ponding":      {"en": "Roof waterproofing 48-h ponding test passed (no leak)",
                             "ar": "اجتاز اختبار التغطية المائية للسطح ٤٨ ساعة (بدون تسرب)"},
    "p5.item.ponding.imglabel":{"en": "Before & after ponding test photos",
                                "ar": "صور قبل وبعد اختبار التغطية المائية"},
    "p5.item.stone_mechanical":{"en": "Stone façade fixed mechanically with stainless anchors (no glue-only)",
                                "ar": "تم تثبيت حجر الواجهة ميكانيكياً بمثبتات ستانلس (ليس بالغراء فقط)"},
    "p5.item.stone_mechanical.warn":
        {"en": "🚨 Glue-only stone façades fail catastrophically in Saudi heat cycles. Stainless mechanical anchors are mandatory.",
         "ar": "🚨 تثبيت حجر الواجهات بالغراء فقط يفشل بشكل كارثي في درجات حرارة المملكة. المثبتات الميكانيكية ستانلس إلزامية."},
    "p5.item.galv_mesh":    {"en": "Galvanized mesh installed at all block/concrete joints before plastering",
                             "ar": "تم تركيب شبك جلفنة على جميع وصلات البلوك/الخرسانة قبل اللياسة"},
    "p5.item.tile_clips":   {"en": "Tile leveling clips used during floor tile installation",
                             "ar": "تم استخدام كلبسات تسوية البلاط أثناء التركيب"},

    # ----- Phase 6 checklist labels -----
    "p6.item.balady":       {"en": "Balady (municipality) occupancy certificate obtained",
                             "ar": "تم الحصول على شهادة الإشغال من البلدية (بلدي)"},
    "p6.item.balady.imglabel":{"en": "Upload the Balady certificate (PDF or photo)",
                               "ar": "ارفع شهادة بلدي (PDF أو صورة)"},
    "p6.item.snags":        {"en": "All defects from snag list resolved (zero open snags)",
                             "ar": "تم حل جميع الملاحظات (لا توجد ملاحظات مفتوحة)"},
    "p6.item.warranties":   {"en": "All supplier warranties & MEP manuals archived in Document Vault",
                             "ar": "تم أرشفة جميع ضمانات الموردين وكتيبات MEP في خزانة المستندات"},

    # ----- Material names (for the per-phase Material Gate) -----
    "mat.concrete_name":    {"en": "Ready-mix Concrete (SRC)",
                             "ar": "خرسانة جاهزة (SRC)"},
    "mat.rebar_name":       {"en": "Reinforcement Steel — Ø12 mm",
                             "ar": "حديد تسليح — قطر ١٢ مم"},
    "mat.blocks_name":      {"en": "Concrete Blocks — 20 cm",
                             "ar": "بلوك خرساني — ٢٠ سم"},
    "mat.pex_name":         {"en": "PEX Water Pipes",
                             "ar": "مواسير PEX للمياه"},
    "mat.cable_name":       {"en": "Electrical Cable — 2.5 mm²",
                             "ar": "كابل كهرباء — ٢٫٥ مم²"},
    "mat.roof_membrane_name":{"en": "Roof Waterproofing Membrane (4 mm SBS)",
                              "ar": "غشاء عزل سطح ٤ مم (SBS)"},

    # ----- Materials Gate -----
    "mat.heading":      {"en": "Material Delivery Gate",
                         "ar": "بوابة توريد المواد"},
    "mat.subheading":   {"en": "Upload supplier invoices and verify they match the BOQ before each item is allowed to PASS.",
                         "ar": "ارفع فواتير الموردين وتأكد من مطابقتها لجدول الكميات قبل اعتماد البنود المرتبطة بها."},
    "mat.expected":     {"en": "Expected (BOQ)", "ar": "المتوقع (جدول الكميات)"},
    "mat.delivered":    {"en": "Delivered quantity",   "ar": "الكمية المسلَّمة"},
    "mat.invoice":      {"en": "Delivery invoice (image / PDF)",
                         "ar": "فاتورة التوريد (صورة / PDF)"},
    "mat.match_status": {"en": "Match status",   "ar": "حالة المطابقة"},
    "mat.match_pending":{"en": "Pending check",  "ar": "بانتظار التحقق"},
    "mat.match_ok":     {"en": "Match",    "ar": "مطابق"},
    "mat.match_bad":    {"en": "Mismatch", "ar": "غير مطابق"},
    "mat.run_check":    {"en": "Run match check",
                         "ar": "تشغيل التحقق"},
    "mat.antitermite_name":{"en": "Anti-termite Pesticide",
                            "ar": "مبيد النمل الأبيض"},
    "mat.weather_hot":  {"en": "🌡️ Hot/humid local weather. Consider sulfate-resistant (SRC) concrete and extended curing.",
                         "ar": "🌡️ المناخ المحلي حار/رطب. يُنصح باستخدام خرسانة مقاومة للكبريتات (SRC) وإطالة فترة المعالجة."},

    # ----- Certificate -----
    "cert.title":    {"en": "PAYMENT CERTIFICATE", "ar": "شهادة دفع"},
    "cert.no":       {"en": "Certificate No.", "ar": "رقم الشهادة"},
    "cert.project":  {"en": "Project",         "ar": "المشروع"},
    "cert.phase":    {"en": "Phase",           "ar": "المرحلة"},
    "cert.amount":   {"en": "Amount (SAR)",    "ar": "المبلغ (ر.س)"},
    "cert.percent":  {"en": "Percentage",      "ar": "النسبة"},
    "cert.issued":   {"en": "Issued",          "ar": "تاريخ الإصدار"},
    "cert.body":     {"en": "This certificate authorizes the release of the milestone payment to the contractor.",
                      "ar": "تعتمد هذه الشهادة صرف دفعة المرحلة للمقاول."},

    # ----- Misc -----
    "misc.disabled_locked": {"en": "🔒 Locked (previous phase not approved)",
                             "ar": "🔒 مغلق (المرحلة السابقة لم تُعتمد بعد)"},
    "misc.disabled_pass":   {"en": "Requirements not met (image or material pending)",
                             "ar": "المتطلبات غير مكتملة (الصورة أو المواد معلقة)"},
    "misc.disabled_rework": {"en": "Item must be marked FAIL before starting rework",
                             "ar": "يجب أن يفشل العنصر قبل بدء إعادة العمل"},
    "misc.rework_count":    {"en": "Rework attempts: {n}",
                             "ar": "عدد محاولات إعادة العمل: {n}"},
    "misc.image_uploaded":  {"en": "Image uploaded.",
                             "ar": "تم رفع الصورة."},
}


# ----------------------------------------------------------------------------
# Public helpers
# ----------------------------------------------------------------------------
def init_lang() -> None:
    """Initialize the language session-state slot exactly once."""
    if "lang" not in st.session_state:
        st.session_state.lang = LANG_DEFAULT


def current_lang() -> str:
    return st.session_state.get("lang", LANG_DEFAULT)


def is_rtl() -> bool:
    return current_lang() == "ar"


def t(key: str, **kwargs) -> str:
    """Translate ``key`` into the active language. Unknown keys return the
    key itself (highly visible during dev). Supports ``str.format`` kwargs."""
    lang = current_lang()
    raw = TRANSLATIONS.get(key, {}).get(lang)
    if raw is None:
        # Fall back to English if available, else echo the key.
        raw = TRANSLATIONS.get(key, {}).get("en", key)
    if kwargs:
        try:
            return raw.format(**kwargs)
        except (KeyError, IndexError):
            return raw
    return raw


def translate_boq_item(english_name: str) -> str:
    """Return the Arabic name of a BOQ row when the active language is Arabic,
    otherwise return the original English name. New items (not yet
    translated) silently fall back to the English name."""
    if current_lang() != "ar":
        return english_name
    entry = TRANSLATIONS.get(f"boq.item.{english_name}")
    return entry["ar"] if entry else english_name
