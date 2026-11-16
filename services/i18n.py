"""Minimal VI/JA switch for UI chrome text (headers, captions, column labels).

Phase 0 scope (user-approved 2026-11-04, position moved to page top
2026-11-06): the language selector is wired into the top of every page's
main content (not the sidebar, so it's the first thing visible on load),
but only the new "Giải thích thuật ngữ" page is fully bilingual right now
-- the existing Tìm kiếm/Thống kê/... pages stay Vietnamese-only and get
translated incrementally later (CLAUDE.md mục 4 "Do not over-engineer").

This module only ever translates the tool's OWN interface strings. It never
translates dictionary/database CONTENT (D1-D4 Japanese terms, Master Doc
prose, disease/drug names) -- CLAUDE.md mục 3 "Never invent missing medical
terms" -- that content is always shown verbatim in its source language.
"""
from __future__ import annotations

import streamlit as st

LANGS = {"vi": "Tiếng Việt", "ja": "日本語"}
DEFAULT_LANG = "vi"


def get_lang() -> str:
    return st.session_state.get("lang", DEFAULT_LANG)


def language_selector() -> str:
    """Renders the VI/JA selectbox at the very top of the main page content
    (right-aligned, above the title -- not the sidebar), so it's the first
    thing visible on every page regardless of which one loads.

    ROOT CAUSE found 2026-11-08 by reading Streamlit's own installed source
    (elements/widgets/selectbox.py): a keyed widget's `persist_state`
    defaults to None, under which Streamlit's own docstring says the value
    "is lost when the widget stops being rendered or the user switches
    pages" (runtime/state/session_state.py::PersistedWidgetTracker enforces
    this per-widget "page" vs "session" scope). Since this selectbox is
    instantiated fresh inside each of the 7 different page scripts (not
    once in the entrypoint), every page switch counted as "the widget
    stopped rendering" under the default scope, and Streamlit intentionally
    reset it to "vi" -- this was never a session reset, a caching bug, nor
    the on_change experiment from earlier today (removed, see git history).
    `persist_state="session"` is Streamlit's own documented switch to keep
    a keyed widget's value "for the entire session, including across page
    switches" -- exactly what's needed here, and it requires `key` to be
    set (already is: key="lang")."""
    _spacer, col = st.columns([4, 1])
    with col:
        return st.selectbox(
            "🌐 Ngôn ngữ / 言語",
            options=list(LANGS.keys()),
            format_func=lambda k: LANGS[k],
            index=list(LANGS.keys()).index(get_lang()),
            key="lang",
            persist_state="session",
        )


def t(key: str, **kwargs) -> str:
    """Looks up `key` in _STRINGS for the current language, falling back to
    DEFAULT_LANG, then to the raw key itself (so a missing translation is
    visibly obvious instead of crashing the page)."""
    entry = _STRINGS.get(key, {})
    text = entry.get(get_lang()) or entry.get(DEFAULT_LANG) or key
    return text.format(**kwargs) if kwargs else text


_STRINGS: dict[str, dict[str, str]] = {
    # ---- Trang "Giải thích thuật ngữ" (D1-D4) -----------------------------
    "glossary.title": {
        "vi": "Giải thích thuật ngữ & từ điển (D1–D4)",
        "ja": "用語・辞書解説（D1〜D4）",
    },
    "glossary.caption": {
        "vi": "Tra cứu nhanh các mã, nhóm, trạng thái dùng trong công cụ tìm kiếm. "
              "Nội dung tiếng Nhật giữ nguyên bản gốc từ dictionaries/*.csv (Master Doc v1.0) "
              "— không dịch lại để tránh sai lệch thuật ngữ y khoa (CLAUDE.md mục 3).",
        "ja": "検索ツールで使用するコード・グループ・ステータスのクイックリファレンスです。"
              "日本語の内容は dictionaries/*.csv（マスタードキュメント v1.0）の原文のまま表示しており、"
              "医学用語のずれを避けるため翻訳はしていません。",
    },
    "glossary.model_status_banner": {
        "vi": "✅ Cập nhật 2026-11-12: các tab dưới đây (Tổng quan pipeline, Cách hoạt động) đã viết lại theo "
              "model v1.3.1 — 1 điều kiện lọc duy nhất (`D4_注射区分`) + group theo tháng liên tục; con người "
              "(reviewer) xác định episode/Day0/case_status/転帰, tool không tự quyết. Thay cho banner cảnh báo "
              "\"lỗi thời\" trước đây. Danh sách đầy đủ, có đánh dấu rõ **đã giải quyết** / **còn tồn đọng** "
              "(cần chủ dự án quyết định) cho từng hạng mục của đợt migrate này nằm ở mục **D** trong tab "
              "\"Nghi vấn & Xác nhận\" bên dưới — nguồn: `deliverables/session00/15_addendum_v1.3.1_migration_"
              "plan_2026-11-11.md`.",
        "ja": "✅ 2026-11-12更新：以下のタブ（パイプライン概要、仕組み）はv1.3.1モデルに合わせて書き直しました — "
              "候補を選ぶ条件は`D4_注射区分`のフィルタ1つだけ＋連続月のグルーピング。エピソード／Day0／"
              "case_status／転帰は人（レビュー担当者）が判断し、ツールは自動判定しません。以前の「旧モデルの"
              "まま」という警告バナーを置き換えています。今回の移行で**解決済み**／**未解決**（チーム責任者の"
              "決定待ち）の項目の全リストは、下の「未確認・確認済み事項」タブのD項にあります — 出典："
              "`deliverables/session00/15_addendum_v1.3.1_migration_plan_2026-11-11.md`。",
    },
    "glossary.tab_intro": {"vi": "Giới thiệu", "ja": "はじめに"},
    "intro.quick_answer_title": {
        "vi": "Công cụ này có dùng được cho nghiên cứu hồi cứu không?",
        "ja": "このツールは後ろ向き研究に使えますか？",
    },
    "intro.quick_answer_body": {
        "vi": "Có — đây chính là công cụ được xây cho Phase 0 Retrospective Analysis. Nhưng chỉ ở vai trò "
              "trích xuất ứng viên + giữ lại bằng chứng tìm kiếm + hỗ trợ rà soát thủ công — KHÔNG tự chẩn "
              "đoán, KHÔNG tự xác nhận đợt điều trị. Mọi ứng viên đều phải được người đọc bệnh án xác nhận "
              "lại bằng tay trước khi tính vào kết quả nghiên cứu chính thức.",
        "ja": "はい — これはPhase 0後ろ向き分析のために作られたツールです。ただし役割は限定的です："
              "候補の抽出＋検索根拠の保存＋手動レビューの支援のみで、自動診断や治療エピソードの自動確認は"
              "行いません。すべての候補は、正式な研究結果として扱う前に診療録を読む人が手動で確認する必要が"
              "あります。",
    },
    "intro.caveat_no_signoff": {
        "vi": "⚠ Chưa có phê duyệt chính thức từ chủ dự án cho một lượt chạy \"sản xuất\" — phạm vi MVP mới "
              "chỉ được \"đóng băng\" ở mức tài liệu nội bộ (xem mục dưới cùng).",
        "ja": "⚠ 本番運用としてのプロジェクトオーナーによる正式な承認はまだありません — MVPの範囲は社内文書"
              "レベルで「凍結」されているのみです（ページ下部参照）。",
    },
    "intro.orphan_title": {
        "vi": "⚠ Phát hiện (kiểm tra trực tiếp trên DB thật, mỗi lần tải trang): clinic_master gốc thiếu dòng "
              "cho các cơ sở sau — đã vá bằng placeholder, vẫn cần tên thật",
        "ja": "⚠ 検出事項（ページ読み込みごとに実データベースを直接確認）：以下の施設は clinic_master に未登録"
              "— プレースホルダーで応急処置済み、正式名称は未確認のまま",
    },
    "intro.orphan_body": {
        "vi": "Các `clinic_id` dưới đây có dữ liệu thật trong database nhưng KHÔNG có dòng trong "
              "`clinic_master` gốc. Đã xác nhận với chủ dự án (2026-11-08) thêm placeholder "
              "`[UNVERIFIED] clinic_<id>` vào filter/pipeline tìm kiếm (`rules/clinic_master_overrides.csv`, "
              "INT-00-04) nên **không còn bị bỏ sót khỏi kết quả tìm kiếm nữa** — nhưng tên cơ sở thật vẫn "
              "chưa xác nhận, và bảng `clinic_master` trong DB gốc vẫn thiếu dòng này (cần tra tên thật từ hệ "
              "thống ORCA gốc rồi backfill để đóng hẳn).",
        "ja": "以下の `clinic_id` は実データを持っていますが、元の `clinic_master` に登録がありません。"
              "チーム責任者の確認（2026-11-08）を得て、検索フィルター・パイプラインに `[UNVERIFIED] "
              "clinic_<id>` のプレースホルダーを追加しました（`rules/clinic_master_overrides.csv`、"
              "INT-00-04）— これで**検索結果から見落とされることはなくなりました**が、正式名称はまだ未確認で"
              "あり、元DBの `clinic_master` にはまだ登録されていません（元のORCAシステムで正式名称を確認の"
              "上、登録する必要があります）。",
    },
    "intro.orphan_col_disease": {"vi": "Dòng bệnh danh", "ja": "傷病名の行数"},
    "intro.orphan_col_medical": {"vi": "Dòng thuốc", "ja": "医薬品の行数"},
    "intro.orphan_col_points": {"vi": "Dòng thủ thuật", "ja": "手技の行数"},
    "intro.orphan_total": {
        "vi": "Tổng cộng bị bỏ sót: {disease} dòng bệnh danh · {medical} dòng thuốc · {points} dòng thủ thuật.",
        "ja": "見落としの合計：傷病名 {disease} 行・医薬品 {medical} 行・手技 {points} 行。",
    },
    "intro.orphan_resolved": {
        "vi": "✓ Không có cơ sở nào bị bỏ sót — mọi clinic_id có dữ liệu thật đều đã có trong clinic_master.",
        "ja": "✓ 見落とされている施設はありません — 実データを持つすべての clinic_id が clinic_master に"
              "登録されています。",
    },
    "intro.can_title": {"vi": "✓ Công cụ làm được", "ja": "✓ できること"},
    "intro.can_body": {
        "vi": "- Đọc database gốc ở chế độ **chỉ đọc**, không bao giờ ghi/sửa dữ liệu nguồn.\n"
              "- Áp đúng 4 từ điển y khoa đã phê duyệt (D1–D4) và bộ điều kiện tìm kiếm Q, không tự thêm/bớt.\n"
              "- Lọc ra danh sách **ứng viên** khả nghi theo bệnh danh hô hấp + kháng sinh tiêm.\n"
              "- Giữ lại toàn bộ bằng chứng dẫn tới mỗi ứng viên, để người rà soát kiểm tra lại.\n"
              "- Xuất 2 mẫu trống (Rà soát thủ công, Kết cục) để con người tự điền tay ở ngoài công cụ.",
        "ja": "- 元データベースを**読み取り専用**で読み込み、ソースデータを書き換えることは一切ありません。\n"
              "- 承認済みの4つの医学辞書（D1〜D4）と検索条件Qをそのまま適用し、独自に追加・削除しません。\n"
              "- 呼吸器系の傷病名＋注射用抗菌薬から疑わしい**候補**の一覧を絞り込みます。\n"
              "- 各候補に至った根拠をすべて保持し、レビュー担当者が確認できるようにします。\n"
              "- 空のテンプレート（手動レビュー、転帰）を2種類出力し、ツールの外で人が手入力します。",
    },
    "intro.cannot_title": {"vi": "✗ Công cụ không làm", "ja": "✗ できないこと"},
    "intro.cannot_body": {
        "vi": "- Không tự chẩn đoán bệnh nhân có thực sự nhiễm trùng hô hấp hay không.\n"
              "- Không tự xác nhận một đợt điều trị, không tự suy ra \"Ngày 0\".\n"
              "- Không tự tính kết cục 30 ngày — trường này luôn trống cho tới khi điền tay.\n"
              "- Không bao giờ xuất tên bệnh nhân ra bất kỳ file nào.\n"
              "- Không suy diễn rằng thuốc \"chắc chắn đã được dùng\" chỉ từ bản ghi hóa đơn/thủ thuật.",
        "ja": "- 患者が実際に呼吸器感染症であるかどうかを自動診断しません。\n"
              "- 治療エピソードを自動確定せず、「Day 0」も自動推定しません。\n"
              "- 30日転帰を自動計算しません — 手入力されるまで常に空欄です。\n"
              "- 患者名をいかなるファイルにも出力しません。\n"
              "- 請求・手技の記録だけから「薬剤が確実に投与された」とは推定しません。",
    },
    "intro.db_header": {"vi": "Cấu trúc database (số liệu trực tiếp từ DB thật)", "ja": "データベース構造（実データベースから直接取得）"},
    "intro.db_clinic_master": {"vi": "Danh sách cơ sở y tế", "ja": "医療機関の一覧"},
    "intro.db_disease_records": {"vi": "Mỗi dòng là 1 bệnh danh ghi nhận cho 1 bệnh nhân trong 1 tháng", "ja": "1行＝1患者・1か月分の傷病名"},
    "intro.db_medical_records": {"vi": "Mỗi dòng là 1 loại thuốc/thủ thuật được tính phí trong 1 tháng", "ja": "1行＝1か月分の請求対象の医薬品・手技"},
    "intro.db_medical_points": {"vi": "Mỗi dòng là 1 lượt tính điểm thủ thuật/truyền dịch, có ngày cụ thể", "ja": "1行＝日付付きの手技・点滴の算定"},
    "intro.db_caption": {
        "vi": "Không có ngày dùng thuốc cụ thể trong \"dòng thuốc\" (chỉ có tháng); mã bệnh nhân không duy "
              "nhất toàn hệ thống — một bệnh nhân luôn được nhận diện bằng cặp (cơ sở, mã bệnh nhân), không "
              "dùng mã bệnh nhân một mình.",
        "ja": "「医薬品の行」には投与日はなく月単位のみです。患者IDはシステム全体で一意ではないため、患者は"
              "常に（施設, 患者ID）の組み合わせで識別され、患者IDだけでは識別しません。",
    },
    "intro.diagram_header": {"vi": "Sơ đồ quan hệ giữa các bảng", "ja": "テーブル関連図"},
    "intro.diagram_caption": {
        "vi": "Mỗi cơ sở có thể có nhiều dòng trong 3 bảng bên dưới — đây là quan hệ trên thực tế dữ liệu, "
              "database không khai báo khóa ngoại chính thức nào.",
        "ja": "各施設は以下の3つのテーブルに複数の行を持つことがあります — これはデータ上の実際の関係であり、"
              "データベースに正式な外部キーは宣言されていません。",
    },
    "intro.diagram_note": {
        "vi": "Công cụ dùng cặp (mã cơ sở, mã bệnh nhân) — không phải 1 cột nào ở trên — để biết các dòng ở "
              "3 bảng dưới cùng thuộc về 1 bệnh nhân, vì 1 mã bệnh nhân có thể lặp lại ở nhiều cơ sở khác nhau.",
        "ja": "ツールは（施設ID, 患者ID）の組み合わせ — 上記のどの列でもなく — を使って、下の3テーブルのどの行が"
              "同じ患者のものかを判断します。患者IDだけでは複数の施設で重複することがあるためです。",
    },
    "intro.run_header": {"vi": "Cách sử dụng", "ja": "使い方"},
    "intro.run_1": {"vi": "Khởi động công cụ (`streamlit run app/Home.py`) và mở đường dẫn hiện ra.", "ja": "ツールを起動し（`streamlit run app/Home.py`）、表示されたURLを開きます。"},
    "intro.run_2": {"vi": "Xem tổng quan dữ liệu ở trang **Home**.", "ja": "**Home** ページでデータの概要を確認します。"},
    "intro.run_3": {"vi": "Sang trang **Tìm kiếm**: chọn cơ sở + khoảng tháng, bấm \"▶ Chạy tìm kiếm\".", "ja": "**検索** ページで施設と期間を選び「▶ 検索実行」を押します。"},
    "intro.run_4": {"vi": "Xem **Thống kê**, rồi vào **Danh sách ứng viên** để duyệt từng ứng viên.", "ja": "**統計** を見てから **候補一覧** で1件ずつ確認します。"},
    "intro.run_5": {"vi": "Xem chi tiết từng ứng viên kèm bằng chứng ở trang **Chi tiết ứng viên**.", "ja": "**候補詳細** ページで根拠付きの詳細を確認します。"},
    "intro.run_6": {"vi": "Xuất kết quả ở trang **Xuất dữ liệu**.", "ja": "**データ出力** ページで結果を出力します。"},
    "intro.approval_status": {
        "vi": "**Trạng thái phê duyệt tổng thể:** phạm vi MVP đã \"đóng băng\" ở mức tài liệu nội bộ, nhưng "
              "chưa có chữ ký/phê duyệt chính thức từ chủ dự án cho một lượt chạy sản xuất "
              "(`deliverables/session00/09_implementation_approval_document.md`).",
        "ja": "**全体の承認状況：** MVPの範囲は社内文書レベルで「凍結」されていますが、本番運用に対する"
              "プロジェクトオーナーの正式な承認・署名はまだありません"
              "（`deliverables/session00/09_implementation_approval_document.md`）。",
    },
    "intro.pointer": {
        "vi": "Xem giải thích chi tiết từng mã D1–D4 ở các tab bên cạnh, và danh sách đầy đủ 34 nghi vấn/"
              "quyết định ở tab \"Nghi vấn & Xác nhận\".",
        "ja": "D1〜D4各コードの詳細は隣のタブを、34件の未確認・決定事項の全リストは「未確認・確認済み事項」"
              "タブをご覧ください。",
    },
    "glossary.overview_header": {
        "vi": "Tổng quan: D4 → Group tháng → D1 → Review (mô hình v1.3.1, 1 trục)",
        "ja": "概要：D4→月単位グルーピング→D1→レビュー（v1.3.1モデル、単一軸）",
    },
    "glossary.overview_flow_d1": {
        "vi": "Lọc bản ghi tính tiền kháng sinh tiêm/truyền (静注・点滴静注)",
        "ja": "注射用抗菌薬の静注・点滴静注の算定記録を抽出",
    },
    "glossary.overview_flow_d2": {
        "vi": "Gộp theo (clinic_id, patient_id) + tháng liên tục → 1 candidate",
        "ja": "(clinic_id, patient_id) ＋ 連続月でグループ化 → 候補1件",
    },
    "glossary.overview_flow_q30": {
        "vi": "Gắn病名 làm metadata (A14–A16) — không dùng để chọn candidate",
        "ja": "病名をメタデータとして付加（A14〜A16）— 候補選定には使わない",
    },
    "glossary.overview_flow_d3": {
        "vi": "Con người xác định episode/Day0/case_status/転帰",
        "ja": "人がエピソード／Day0／case_status／転帰を判定",
    },
    "glossary.overview_flow_d4_note": {
        "vi": "V1-ROUTE (`D4_注射区分`, mã `.310`–`.350`) là điều kiện LỌC duy nhất chọn candidate — không còn "
              "kết hợp AND giữa nhiều trục (病名×薬剤×点滴手技) như model v1.0.",
        "ja": "V1-ROUTE（`D4_注射区分`、コード`.310`〜`.350`）が候補を選ぶ唯一のフィルタ条件です — v1.0モデルの"
              "ような複数軸（病名×薬剤×点滴手技）のAND結合はもうありません。",
    },
    "glossary.overview_d1": {
        "vi": "**Bước 1 — D4_注射区分 (lọc candidate)**: quét `medical_records`, giữ lại dòng có mã tính tiền "
              "khớp `D4_注射区分` (`.310`–`.350`, tương ứng 皮下筋肉注射/静脈注射/点滴注射) VÀ là kháng sinh tiêm "
              "(theo D2_成分/D2_検索語, nội dung giữ nguyên từ v1.0). Cột `候補にするか` cho biết medical_class "
              "nào được tính; cột `A13投与経路` ghi lại 静注/点滴静注.",
        "ja": "**ステップ1 — D4_注射区分（候補フィルタ）**：`medical_records` を走査し、`D4_注射区分`（`.310`〜"
              "`.350`、皮下筋肉注射／静脈注射／点滴注射に対応）に一致する算定コード **かつ** 注射用抗菌薬（D2_成"
              "分／D2_検索語、内容はv1.0から変更なし）の行のみ残す。`候補にするか`列がどのmedical_classを候補と"
              "して数えるかを示し、`A13投与経路`列が静注／点滴静注を記録する。",
    },
    "glossary.overview_d2": {
        "vi": "**Bước 2 — Group theo tháng liên tục**: vì ORCA chỉ có `perform_month` (không có ngày tính tiền), "
              "1 candidate = 1 chuỗi tháng liên tục có tính tiền kháng sinh tiêm/truyền, theo từng `(clinic_id, "
              "patient_id)`. `candidate_id` = `施設ID:患者番号:最初の算定月` (vd `clinic_001:00000004:2025-11`) "
              "— cùng điều kiện tìm sẽ luôn ra cùng ID.",
        "ja": "**ステップ2 — 連続月のグルーピング**：ORCAには`perform_month`（月単位）しかなく算定日が無いため、"
              "候補1件＝`(clinic_id, patient_id)` ごとに注射用抗菌薬の算定がある連続した月の並び。`candidate_id`"
              "＝「施設ID:患者番号:最初の算定月」（例：clinic_001:00000004:2025-11）— 同じ検索条件なら常に同じ"
              "IDになる。",
    },
    "glossary.overview_merge": {
        "vi": "**Bước 3 — D1 gắn病名 làm metadata**: với mỗi candidate, đọc `disease_records` hiệu lực trong "
              "khoảng thời gian đó, chuẩn hóa NFKC + áp 8 từ bổ nghĩa (M01–M08, ý nghĩa X/H/S/A giữ nguyên từ "
              "v1.0) rồi so khớp 18 phân loại — nhưng kết quả chỉ ghi vào cột `diagnosis_categories` (A16) để "
              "reviewer tham khảo, **không** còn dùng để chọn hay loại candidate như Set A/Q10 cũ.",
        "ja": "**ステップ3 — D1による病名メタデータの付加**：各候補について、該当期間に有効な `disease_records` "
              "をNFKC正規化＋8種の修飾語（M01〜M08、X/H/S/Aの意味はv1.0と同じ）で判定し18分類に照合 — ただし結果"
              "は `diagnosis_categories`（A16）列にレビュー参考として記録するのみで、旧 集合A／Q10のように候補"
              "の選定・除外には**使わない**。",
    },
    "glossary.overview_d3": {
        "vi": "**Bước 4 — Con người xác định episode/Day0/case_status**: reviewer đọc 電子カルテ (NAHT/HOMIS) "
              "thật, áp \"quy tắc 14 ngày\" (khoảng cách 2 lần truyền ≥15 ngày = episode mới) theo ngày thật để "
              "tách 1 candidate thành nhiều `episode_id` (`candidate_id-1`, `candidate_id-2`...), rồi gán "
              "`case_status` = 対象/対象外/保留 (B02) + lý do B03. Tool **không được** tự quyết diagnosis, Day0, "
              "14-day rule hay case_status (`検索ツール設計の考え方` §2–4).",
        "ja": "**ステップ4 — 人によるエピソード／Day0／case_status判定**：レビュー担当者が実際の電子カルテ"
              "（NAHT／HOMIS）を読み、「14日ルール」（2回の投与の間隔が15日以上＝新しいエピソード）を実際の日付"
              "で適用して候補を複数の`episode_id`（`candidate_id-1`、`candidate_id-2`…）に分割し、`case_status`"
              "＝対象／対象外／保留（B02）＋理由B03を判定する。ツールは診断・Day0・14日ルール・case_statusを**"
              "自動で決定してはならない**（検索ツール設計の考え方§2〜4）。",
    },
    "glossary.overview_d4": {
        "vi": "**Bước 5 — 転帰 30 ngày (sau khi reviewer xác nhận Day0)**: cửa sổ Day0–Day30 (cả 2 đầu); "
              "複合転帰 = bất kỳ 1/3 (nhập viện/cấp cứu/tử vong) = \"あり\"; \"なし\" chỉ ghi khi xác nhận dương "
              "không có event — im lặng/thiếu ghi chép luôn ra \"不明\", không mặc định \"なし\". **保留 không "
              "vào mẫu số chính** — báo riêng (`held_back_count`), theo quyết định tạm thời 2026-11-11 (xem tab "
              "Nghi vấn & Xác nhận, mục D).",
        "ja": "**ステップ5 — 30日転帰（レビュー担当者がDay0を確定した後）**：Day0〜Day30（両端含む）の観察期間。"
              "複合転帰＝入院・救急搬送・死亡のいずれか1つでも「あり」。「なし」は陰性を確認できた場合のみ記録し"
              "、記録がない／不明な場合は常に「不明」（デフォルトで「なし」にはしない）。**保留は主分母に含めな"
              "い** — `held_back_count`として別掲（2026-11-11の暫定決定、詳細は「未確認・確認済み事項」タブD"
              "項）。",
    },
    "glossary.overview_source": {
        "vi": "Tóm tắt theo `deliverables/session00/15_addendum_v1.3.1_migration_plan_2026-11-11.md` Mục 2.1–2.6 "
              "+ `後ろ向き集計 手順書v1.3.1` §3/§5/§6 + `CSV設計説明書v1.3.1` §4/§6 — nguồn thẩm quyền cao nhất "
              "vẫn là `手順書v1.3.1` (正本, CLAUDE.md mục 2); đây chỉ là tóm tắt điều hướng, không thay thế nó.",
        "ja": "`deliverables/session00/15_addendum_v1.3.1_migration_plan_2026-11-11.md` Mục2.1〜2.6 ＋『後ろ向き"
              "集計 手順書v1.3.1』§3／§5／§6 ＋『CSV設計説明書v1.3.1』§4／§6 の要約。最上位の権威源は引き続き"
              "`手順書v1.3.1`（正本、CLAUDE.md §2）であり、これはナビゲーション用の要約に過ぎません。",
    },
    "glossary.tab_open_questions": {"vi": "Nghi vấn & Xác nhận", "ja": "未確認・確認済み事項"},
    "glossary.tab_howitworks": {"vi": "Cách hoạt động (dễ hiểu)", "ja": "仕組み（やさしい説明）"},
    "glossary.oq_caption": {
        "vi": "Tổng hợp các nghi vấn/quyết định nghiên cứu ảnh hưởng tới cách đọc kết quả tìm kiếm — nguyên trạng "
              "thái như tài liệu gốc, không tự nâng mục nào lên 'đã xác minh'.",
        "ja": "検索結果の解釈に影響する未確認事項・研究上の決定事項のまとめです。ステータスは原典のまま表示し、"
              "どの項目も独自に「確認済み」へ引き上げてはいません。",
    },
    "glossary.oq_filter_label": {"vi": "Lọc theo trạng thái", "ja": "ステータスで絞り込み"},
    "glossary.oq_filter_all": {"vi": "Tất cả", "ja": "すべて"},
    "glossary.oq_col_id": {"vi": "Mã", "ja": "ID"},
    "glossary.oq_col_status": {"vi": "Trạng thái", "ja": "ステータス"},
    "glossary.oq_col_content": {"vi": "Nội dung / Thông tin được xác nhận", "ja": "内容／確認済み情報"},
    "glossary.oq_col_owner": {"vi": "Chủ sở hữu quyết định", "ja": "決定権者"},
    "glossary.oq_status_unverified": {"vi": "⚠️ Chưa xác minh", "ja": "⚠️ 未確認"},
    "glossary.oq_status_resolved": {"vi": "✅ Đã xác nhận", "ja": "✅ 確認済み"},
    "glossary.oq_status_proposed": {"vi": "🟡 Đề xuất, chưa phê duyệt", "ja": "🟡 提案中（未承認）"},
    "glossary.oq_source": {
        "vi": "Nguồn mục A/B/C: deliverables/session00/08_unresolved_decisions_register.md (Session 00, "
              "2026-11-04) — chỉ lấy phần A/B/C (quyết định nghiên cứu/lâm sàng, logic D1–D4/Q/QC, mô hình CSV) "
              "**của model v1.0**; phần D (phát hiện kỹ thuật/code, INT-00-xx) và E (housekeeping) thuộc backlog "
              "kỹ thuật, xem trực tiếp file gốc. Nguồn mục D: "
              "deliverables/session00/15_addendum_v1.3.1_migration_plan_2026-11-11.md (Mục 0 + Mục 5) — trạng "
              "thái migrate sang model v1.3.1, đã giải quyết/còn tồn đọng, cập nhật 2026-11-11/12.",
        "ja": "A/B/C項の出典：deliverables/session00/08_unresolved_decisions_register.md（Session 00、"
              "2026-11-04）— **v1.0モデル**のA/B/C（研究・臨床上の決定、D1〜D4/Q/QCのロジック、CSVデータモデル）"
              "のみを掲載。D項（実装・コードレベルの指摘、INT-00-xx）とE項（housekeeping）は技術バックログのため"
              "原典を直接参照してください。D項の出典：deliverables/session00/15_addendum_v1.3.1_migration_"
              "plan_2026-11-11.md（Mục0＋Mục5）— v1.3.1モデルへの移行状況（解決済み／未解決）、2026-11-11/12更"
              "新。",
    },
    "glossary.tab_d1": {"vi": "D1 — Bệnh danh", "ja": "D1 — 傷病名"},
    "glossary.tab_d2": {"vi": "D2 — Kháng sinh tiêm", "ja": "D2 — 注射用抗菌薬"},
    "glossary.tab_d3": {"vi": "D3 — Ma trận phán đoán", "ja": "D3 — 判定マトリクス"},
    "glossary.tab_d4": {"vi": "D4 — Thủ thuật/truyền dịch", "ja": "D4 — 手技・注射"},
    "glossary.d1_categories_header": {
        "vi": "18 nhóm bệnh danh (thử theo thứ tự, dừng ở nhóm đầu tiên khớp)",
        "ja": "傷病名18分類（順番に判定し、最初に一致した分類で確定）",
    },
    "glossary.d1_categories_caption": {
        "vi": "Cột 'Tiêu chí khớp' là mô tả gốc tiếng Nhật trong CSV, không phải bản dịch.",
        "ja": "「判定条件」列はCSV原文で、翻訳ではありません。",
    },
    "glossary.d1_modifiers_header": {
        "vi": "8 hậu tố điều chỉnh trạng thái (M01–M08)",
        "ja": "状態を調整する接尾語8種（M01〜M08）",
    },
    "glossary.d1_modifiers_caption": {
        "vi": "Nếu bệnh danh khớp nhiều hậu tố, ưu tiên theo thứ tự X > H > S > A "
              "(services/match_d1.py, theo dictionary_specification.md §4).",
        "ja": "複数の接尾語に一致する場合は X > H > S > A の優先順位で判定します"
              "（services/match_d1.py、dictionary_specification.md §4 準拠）。",
    },
    "glossary.d1_status_legend": {
        "vi": "X = phòng ngừa (loại khỏi bằng chứng) · H = tiền sử/đã điều trị (không dùng cho đợt bệnh hiện tại) "
              "· S = nghi ngờ (giữ lại nhưng hạ 1 bậc ở D3) · A = đang hoạt động (giữ nguyên bậc).",
        "ja": "X＝予防（根拠から除外）・H＝既往／治療後（今回エピソードの根拠にしない）・"
              "S＝疑い（候補にするがD3で1段階下げる）・A＝活動性（区分を下げない）。",
    },
    "glossary.d2_header": {"vi": "Danh mục thành phần kháng sinh (search_term)", "ja": "抗菌薬成分の検索語一覧"},
    "glossary.d2_caption": {
        "vi": "search_term đã NFKC-normalize; dùng để khớp chuỗi trong bản ghi thuốc. "
              "'Cần kiểm tra dạng bào chế' = search_term_type có ghi '要剤形確認'.",
        "ja": "search_term はNFKC正規化済みで、医薬品レコードの文字列照合に使用します。"
              "「剤形確認要」は search_term_type に「要剤形確認」の記載があるものです。",
    },
    "glossary.d2_footer": {
        "vi": "{confirmed} / {total} thành phần ở trạng thái 'Đã xác nhận' (確認済); phần còn lại là 'Chưa xác nhận' (未確認).",
        "ja": "{confirmed} / {total} 成分が「確認済」、残りは「未確認」です。",
    },
    "glossary.d3_groups_header": {"vi": "7 nhóm kháng sinh (G1–G6)", "ja": "抗菌薬グループ7種（G1〜G6）"},
    "glossary.d3_judgment_header": {"vi": "4 mã phán đoán rà soát (A/B/C/X)", "ja": "判定コード4種（A/B/C/X）"},
    "glossary.d3_matrix_header": {
        "vi": "Ma trận nhóm bệnh danh × nhóm kháng sinh → mã phán đoán",
        "ja": "傷病名分類 × 抗菌薬グループ → 判定コード マトリクス",
    },
    "glossary.d3_matrix_caption": {
        "vi": "Mỗi ô = mã phán đoán (A/B/C/X) áp dụng khi một ứng viên vừa khớp nhóm bệnh danh (hàng) "
              "vừa khớp nhóm kháng sinh (cột). Đây là tín hiệu ưu tiên rà soát, KHÔNG phải kết luận lâm sàng.",
        "ja": "各セルは、傷病名分類（行）と抗菌薬グループ（列）の両方に一致した候補に適用される判定コード"
              "（A/B/C/X）です。レビュー優先度の目安であり、臨床的な結論ではありません。",
    },
    "glossary.d4_header": {"vi": "Mã thủ thuật tiêm/truyền (P01–P11…)", "ja": "注射・輸液の手技コード（P01〜P11…）"},
    "glossary.d4_v131_info": {
        "vi": "v1.3.1: D4 không còn là \"loại thủ thuật tham khảo\" (P01-P24 cũ) mà là nguồn chọn candidate "
              "trực tiếp (V1-ROUTE). 2 cột mới `候補にするか` / `A13投与経路` cho biết medical_class nào được "
              "tính là candidate.",
        "ja": "v1.3.1：D4はもはや「参考の手技種別」（旧P01-P24）ではなく、候補を直接選ぶための情報源"
              "（V1-ROUTE）です。新しい2列`候補にするか`／`A13投与経路`が、どのmedical_classが候補として"
              "カウントされるかを示します。",
    },
    "glossary.d5_version_caption": {"vi": "D5 version: {version}", "ja": "D5バージョン：{version}"},
    "glossary.d5_not_found_caption": {
        "vi": "dictionaries/D5_context_flags.csv chưa có trong lần chạy này.",
        "ja": "この実行には dictionaries/D5_context_flags.csv がありません。",
    },
    "glossary.d4_caption": {
        "vi": "Phân loại dựa trên mã thanh toán (billing_classification) — chỉ là manh mối về đường dùng thuốc, "
              "KHÔNG phải bằng chứng xác nhận đã thực sự dùng thuốc (CLAUDE.md mục 3).",
        "ja": "算定区分（billing_classification）に基づく分類です。投与経路の手がかりに過ぎず、"
              "実際に投与されたことを確定する根拠ではありません（CLAUDE.md 第3項）。",
    },
    "glossary.version_footer": {
        "vi": "Version chỉ đổi khi nạp bộ dictionaries/*.csv mới từ Session 03 — không chỉnh được từ UI.",
        "ja": "バージョンは Session 03 から新しい dictionaries/*.csv を取り込んだ時のみ変わります。UIからは変更できません。",
    },
    # ---- Nhãn điều hướng sidebar (ADDENDUM 2026-11-08) -- st.navigation() đọc
    # lại các key này mỗi lần rerun nên đổi ngôn ngữ cũng đổi luôn nhãn sidebar ----
    "nav.home": {"vi": "Trang chủ", "ja": "ホーム"},
    "nav.search": {"vi": "Tìm kiếm", "ja": "検索"},
    "nav.stats": {"vi": "Thống kê", "ja": "統計"},
    "nav.candidates": {"vi": "Danh sách ứng viên", "ja": "候補一覧"},
    "nav.detail": {"vi": "Chi tiết bệnh nhân", "ja": "患者詳細"},
    "nav.export": {"vi": "Xuất dữ liệu", "ja": "データ出力"},
    "nav.glossary": {"vi": "Giải thích thuật ngữ", "ja": "用語解説"},
    # ---- Tab "Cách hoạt động" (ADDENDUM 2026-11-06, bản giải thích phi kỹ thuật) ----
    "how.caption": {
        "vi": "Tab này giải thích tool đang làm gì theo ngôn ngữ phi kỹ thuật — các bảng "
              "dữ liệu thật của D1/D2/D4 nằm ở 3 tab riêng bên cạnh.",
        "ja": "このタブは専門用語を使わずツールの仕組みを説明します。D1/D2/D4 の実データ表は"
              "隣の3つのタブにあります。",
    },
    "how.sets_header": {
        "vi": "Chỉ 1 điều kiện chọn candidate — không còn ghép 3 \"tập hợp\" như trước",
        "ja": "候補を選ぶ条件は1つだけ — 以前のような3つの「集合」の組み合わせではない",
    },
    "how.sets_intro": {
        "vi": "v1.0 nhìn mỗi bệnh nhân qua 3 câu hỏi độc lập (3 vòng tròn chồng lên nhau); v1.3.1 đơn giản hoá "
              "hẳn, chỉ còn 1 điều kiện:",
        "ja": "v1.0は各患者を3つの独立した質問（重なる3つの輪）で見ていましたが、v1.3.1は条件を1つだけに簡素"
              "化しました：",
    },
    "how.compare_old": {
        "vi": "3 trục độc lập: 病名 (D1/Tập A) × 注射薬 (D2/Tập B) × 点滴手技 (D4 cũ/Tập C), kết hợp qua "
              "Q10/Q20/Q30 thành ma trận 7 vùng (chỉ A, chỉ B, chỉ C, A+B, A+C, B+C, A+B+C). Tool tự judge D3 "
              "→ gán mã A/B/C/X cho từng candidate.",
        "ja": "3つの独立した軸：病名（D1／集合A）×注射薬（D2／集合B）×点滴手技（旧D4／集合C）をQ10／Q20／"
              "Q30で組み合わせ、7領域のマトリクス（Aのみ、Bのみ、Cのみ、A+B、A+C、B+C、A+B+C）を作る。ツール"
              "がD3で自動判定しA/B/C/Xのコードを付与。",
    },
    "how.compare_new": {
        "vi": "1 điều kiện duy nhất: có bản ghi tính tiền kháng sinh tiêm/truyền, lọc qua `D4_注射区分` (mã "
              "`.310`–`.350`). 病名 (D1) chỉ còn là metadata gắn kèm — **không** dùng để chọn hay loại "
              "candidate. Con người (reviewer) xác định episode/Day0/case_status/転帰, không phải tool.",
        "ja": "条件は1つだけ：`D4_注射区分`（コード`.310`〜`.350`）でフィルタした注射用抗菌薬の算定記録がある"
              "こと。病名（D1）は付加メタデータに過ぎず、候補の選定・除外には**使わない**。エピソード／Day0／"
              "case_status／転帰は人（レビュー担当者）が判断し、ツールは判断しない。",
    },
    "how.sets_note": {
        "vi": "A_only/C_only/A+C (chỉ病名 hoặc chỉ thủ thuật, không có thuốc tiêm) **không bao giờ** là candidate "
              "ở v1.3.1 — khác hẳn v1.0 (nơi các vùng này vẫn được giữ lại để rà soát).",
        "ja": "A_only／C_only／A+C（病名のみ、または手技のみで薬剤なし）は v1.3.1 では**候補になりません** — "
              "これらの領域もレビュー対象として保持していたv1.0とは異なります。",
    },
    "how.certainty_header": {
        "vi": "Mức độ chắc chắn của病名 gắn kèm (A / S / H / X) — vẫn dùng để gắn metadata, không dùng để chọn candidate",
        "ja": "付加される病名の確からしさ（A・S・H・X）— メタデータ付加に使うが、候補選定には使わない",
    },
    "how.certainty_intro": {
        "vi": "Không phải cứ thấy tên bệnh là chắc chắn 100%. \"Viêm phổi\" (đang mắc) khác hẳn \"tiền sử "
              "viêm phổi\" hay \"phòng viêm phổi\". Mỗi dòng bệnh được phân vào 1 trong 4 mức sau, dựa trên "
              "các từ đứng sau tên bệnh (D1 — 8 \"từ bổ nghĩa\", ý nghĩa giữ nguyên từ v1.0). Lưu ý: ở v1.3.1, "
              "D1 không còn quyết định ai là candidate — 4 mức dưới đây chỉ ảnh hưởng tới nội dung cột "
              "`diagnosis_categories` (A16) gắn kèm mỗi candidate, để reviewer tham khảo:",
        "ja": "傷病名があるだけで100%確実とは限りません。「肺炎」（現在罹患）と「肺炎の既往」「肺炎予防」は"
              "全く別です。各行は病名の後に付く語（D1の8個の修飾語、意味はv1.0のまま）によって次の4段階に分類"
              "されます。注意：v1.3.1ではD1はもはや候補の選定を決めません — 以下の4段階は各候補に付加される "
              "`diagnosis_categories`（A16）列の内容にのみ影響し、レビュー参考情報として使われます：",
    },
    "how.certainty_a": {"vi": "✓ **A — Đang hoạt động**: dùng làm căn cứ, giữ nguyên độ tin cậy (gồm cả \"tái phát/bùng phát\").", "ja": "✓ **A — 活動性**：根拠として使用、信頼度は下げない（「再燃・増悪」含む）。"},
    "how.certainty_s": {"vi": "✓ **S — Nghi ngờ**: dùng, nhưng gắn vào metadata ở mức thấp hơn A.", "ja": "✓ **S — 疑い**：使用するが、メタデータ上はAより低い段階として記録する。"},
    "how.certainty_h": {"vi": "✕ **H — Tiền sử**: KHÔNG dùng — không phải đợt bệnh lần này (đã qua/sau điều trị/di chứng).", "ja": "✕ **H — 既往**：使用しない — 今回のエピソードではない（既往・治療後・後遺症）。"},
    "how.certainty_x": {"vi": "✕ **X — Dự phòng**: KHÔNG dùng — chưa mắc bệnh, chỉ là phòng ngừa.", "ja": "✕ **X — 予防**：使用しない — まだ罹患していない、予防のみ。"},
    "how.undecided_header": {
        "vi": "Vì sao vẫn còn nhiều mục \"cần quyết định\" sau khi migrate xong?",
        "ja": "移行完了後も「要決定」項目が多いのはなぜ？",
    },
    "how.undecided_body": {
        "vi": "Việc viết lại code (model 1 trục, group theo tháng, 6 trang app, test) đã **xong** 2026-11-11 — "
              "nhưng đó chỉ là phần kỹ thuật. Các câu hỏi **nghiệp vụ/lâm sàng** (công thức急変率chính thức, "
              "danh sách lý do 保留/対象外 cuối cùng, quyền dữ liệu cá nhân, quy trình xác nhận nhập viện ngoài "
              "cơ sở...) vẫn cần chủ dự án/bác sĩ quyết định. Đây **không phải lỗi của tool** — CLAUDE.md mục 3 "
              "yêu cầu tool không tự chốt thay con người khi chưa có đủ bằng chứng/phê duyệt. Xem danh sách đầy "
              "đủ, có đánh dấu rõ đã giải quyết/còn mở, ở mục **D** trong tab \"Nghi vấn & Xác nhận\".",
        "ja": "コードの書き直し（単一軸モデル、月単位グルーピング、appの6ページ、テスト）は2026-11-11に**完了**"
              "しましたが、これは技術面だけです。**業務・臨床面**の論点（急変率の正式な計算式、保留／対象外の"
              "最終的な理由リスト、個人データの利用権限、施設外入院の確認プロセスなど）は、依然としてチーム"
              "責任者・医師の決定が必要です。これは**ツールの欠陥ではありません** — CLAUDE.md第3項は、十分な"
              "根拠・承認がない場合にツールが人に代わって決定しないことを求めています。解決済み／未解決を明示"
              "した全リストは「未確認・確認済み事項」タブのD項にあります。",
    },
    "how.d5_header": {"vi": "D5 — cờ cảnh báo bổ sung (DRAFT, chưa phê duyệt chính thức)", "ja": "D5 — 追加コンテキストフラグ（DRAFT・未承認）"},
    "how.d5_body": {
        "vi": "Mới thêm 2026-11-05 từ tài liệu *CSV Design Guide v1.0*, dùng cho cột `context_review_flags` "
              "của file xuất bổ sung. **Khác với D1–D4**, D5 chưa qua quy trình đối chiếu với Master Document "
              "— chỉ dùng để tham khảo khi rà soát, không module nào tự điền/kiểm tra theo bộ mã này.",
        "ja": "2026年11月5日に *CSV Design Guide v1.0* から追加され、追加出力ファイルの "
              "`context_review_flags` 列に使用されます。**D1〜D4とは異なり**、D5はマスタードキュメントとの"
              "照合を経ていません — レビュー時の参考のみで、このコードに基づいて自動入力・検証を行う"
              "モジュールはありません。",
    },
    "how.patterns_header": {"vi": "Tài liệu 15 tình huống mẫu rà soát", "ja": "レビュー用15パターン資料"},
    "how.patterns_body": {
        "vi": "`document/A/AGRI_CARE_Retrospective_15patterns_Updated_20261103.pdf` — 15 tổ hợp bệnh×kháng "
              "sinh điển hình, dùng làm điểm khởi đầu khi đọc hồ sơ (gồm ngưỡng 14 ngày tạm thời cho ranh "
              "giới đợt điều trị). Đây là **ví dụ minh hoạ cho người rà soát**, không phải quy tắc tự động "
              "của tool.",
        "ja": "`document/A/AGRI_CARE_Retrospective_15patterns_Updated_20261103.pdf` — 典型的な傷病名×抗菌薬"
              "の組み合わせ15例で、診療録を読む際の出発点として使います（治療エピソードの境界を暫定的に"
              "14日とする目安を含む）。これは**レビュー担当者向けの例示**であり、ツールの自動判定ルール"
              "ではありません。",
    },
    "how.refs_header": {"vi": "Nguồn tài liệu tham khảo đã dùng để xây tool (v1.3.1)", "ja": "ツール構築に使用した参照資料（v1.3.1）"},
    "how.ref_master": {
        "vi": "**後ろ向き集計 手順書v1.3.1.docx (正本)** — nguồn thẩm quyền cao nhất hiện tại (CLAUDE.md mục 2); "
              "định nghĩa mô hình candidate, Day0/14-day rule, case_status/転帰. Khi tài liệu khác mâu thuẫn, "
              "tài liệu này thắng. (Master Document v1.0 cũ hạ xuống chỉ tham khảo lịch sử.)",
        "ja": "**後ろ向き集計 手順書v1.3.1.docx（正本）** — 現在の最上位の権威資料（CLAUDE.md §2）。候補モデル、"
              "Day0／14日ルール、case_status／転帰を定義。他文書と矛盾する場合はこれが優先（旧v1.0マスタードキ"
              "ュメントは歴史的参考のみに格下げ）。",
    },
    "how.ref_policy": {
        "vi": "**後ろ向き集計 実施方針の概要v1.3.1.docx** — tổng quan mục đích/phạm vi, liệt kê 5 tài liệu chính "
              "thức (tài liệu thứ 5 \"急変率の計算\" chưa tồn tại trong document/A/v1.3.1/).",
        "ja": "**後ろ向き集計 実施方針の概要v1.3.1.docx** — 目的・範囲の概要、5つの公式文書を列挙（5番目「急変率"
              "の計算」はdocument/A/v1.3.1/にまだ存在しない）。",
    },
    "how.ref_pharma": {
        "vi": "**後ろ向き集計 CSV設計説明書v1.3.1.docx + 診療録レビューの判定基準v1.3.1.docx** — quy định 41 "
              "cột CSV (A/B/C) và tiêu chí Day0/case_status/転帰 cho reviewer.",
        "ja": "**後ろ向き集計 CSV設計説明書v1.3.1.docx＋診療録レビューの判定基準v1.3.1.docx** — CSV41列"
              "（A/B/C）の仕様と、レビュー担当者向けDay0／case_status／転帰の判定基準。",
    },
    "how.ref_csvguide": {
        "vi": "**後ろ向き集計 検索ツールの設計基準と辞書v1.3.1.docx + 検索ツール辞書v1.3.1.xlsx** — nguồn "
              "D1/D2/D3/D4/D5, bao gồm sheet mới D4_注射区分.",
        "ja": "**後ろ向き集計 検索ツールの設計基準と辞書v1.3.1.docx＋検索ツール辞書v1.3.1.xlsx** — D1/D2/D3/"
              "D4/D5の出典。新シートD4_注射区分を含む。",
    },
    "how.ref_patterns": {
        "vi": "**在宅抗菌薬点滴エピソード特定・転帰判定ガイド(早見表)v1.3.1.docx** — hướng dẫn nhanh step-by-"
              "step cho reviewer, thay vai trò tài liệu \"15 tình huống mẫu\" cũ (xem mục bên trên).",
        "ja": "**在宅抗菌薬点滴エピソード特定・転帰判定ガイド（早見表）v1.3.1.docx** — レビュー担当者向けのス"
              "テップバイステップ早見表。旧「15パターン資料」（上記参照）の役割を引き継ぐ。",
    },
    "how.ref_dbprofile": {
        "vi": "**Hồ sơ khảo sát cơ sở dữ liệu thật (Session 02) + rà soát trực tiếp orca_snapshot.db "
              "(2026-11-11)** — kiểm tra trực tiếp trên hệ thống thật, đảm bảo tool dùng đúng tên bảng/cột đang "
              "tồn tại.",
        "ja": "**実データベース調査報告（Session 02）＋orca_snapshot.dbの直接確認（2026-11-11）** — 実システム"
              "を直接確認し、存在する正しいテーブル名・列名を使用していることを保証。",
    },
    # ---- Trang "Home" (Block 1 — Database Overview) ------------------------
    "home.caption": {
        "vi": "Công cụ trích xuất ứng viên cho rà soát thủ công — KHÔNG phải công cụ chẩn đoán/xác nhận điều trị tự động.",
        "ja": "手動レビュー向けの候補抽出ツールです — 自動診断・自動治療確認ツールではありません。",
    },
    "home.db_connected": {"vi": "● Kết nối database: READ-ONLY OK", "ja": "● データベース接続：READ-ONLY OK"},
    "home.metric_clinic": {"vi": "Clinic (clinic_master)", "ja": "施設（clinic_master）"},
    "home.metric_patients": {"vi": "Bệnh nhân riêng biệt", "ja": "重複なし患者数"},
    "home.metric_patients_help": {
        "vi": "COUNT DISTINCT (clinic_id, patient_id) — KHÔNG dùng patient_id một mình vì nó lặp lại tới 19 clinic.",
        "ja": "COUNT DISTINCT (clinic_id, patient_id) — patient_id 単独は19施設で重複するため使用しません。",
    },
    "home.metric_disease": {"vi": "Bệnh danh (dòng)", "ja": "傷病名（行数）"},
    "home.metric_medical": {"vi": "Thuốc/hành vi (dòng)", "ja": "医薬品・行為（行数）"},
    "home.metric_points": {"vi": "medical_points (dòng)", "ja": "medical_points（行数）"},
    "home.metric_points_help": {
        "vi": "Chỉ nhóm HOMIS có dữ liệu; NAHT = 0 dòng (giới hạn pipeline đã xác nhận, Session 02).",
        "ja": "HOMISグループのみデータあり；NAHT = 0行（Session 02で確認済みのパイプライン上の制約）。",
    },
    "home.scope_header": {
        "vi": "Phạm vi dữ liệu theo nhóm công cụ crawl (NAHT / HOMIS)",
        "ja": "クロールツールグループ別のデータ範囲（NAHT / HOMIS）",
    },
    "home.scope_caption": {
        "vi": "2 pipeline crawl khác nhau — KHÔNG coi là 1 snapshot chung (document/A/clinic_tool_mapping_v1.0.md).",
        "ja": "2つの異なるクロールパイプラインです — 単一の共通スナップショットとして扱わないでください"
              "（document/A/clinic_tool_mapping_v1.0.md）。",
    },
    "home.group_naht": {"vi": "NAHT (11 clinic)", "ja": "NAHT（11施設）"},
    "home.group_homis": {"vi": "HOMIS (còn lại)", "ja": "HOMIS（残り）"},
    "home.clinic_list_header": {"vi": "Danh sách clinic", "ja": "施設一覧"},
    "home.col_patient_count": {"vi": "Số bệnh nhân", "ja": "患者数"},
    "home.col_notes": {"vi": "Ghi chú", "ja": "備考"},
    "home.note_zero_data": {
        "vi": "⚠ 0 dòng cả 3 bảng — đã xác nhận không phải vấn đề",
        "ja": "⚠ 3テーブルすべて0行 — 問題ではないことを確認済み",
    },
    "home.note_small_clinic": {"vi": "⚠ cơ sở nhỏ (<30 bệnh nhân)", "ja": "⚠ 小規模施設（患者数30人未満）"},
    "home.dict_version_header": {
        "vi": "Phiên bản từ điển / điều kiện tìm kiếm đang dùng",
        "ja": "使用中の辞書／検索条件バージョン",
    },
    "home.metric_d1": {"vi": "D1 (bệnh danh)", "ja": "D1（傷病名）"},
    "home.metric_d2": {"vi": "D2 (kháng sinh)", "ja": "D2（抗菌薬）"},
    "home.metric_d3": {"vi": "D3 (ma trận)", "ja": "D3（マトリクス）"},
    "home.metric_d4": {"vi": "D4 (thủ thuật)", "ja": "D4（手技）"},
    "home.link_search": {"vi": "➜ Sang trang Tìm kiếm (Block 2 + 3)", "ja": "➜ 検索ページへ（Block 2 + 3）"},
    "home.link_glossary": {
        "vi": "➜ Giải thích thuật ngữ & từ điển (D1–D4)",
        "ja": "➜ 用語・辞書解説へ（D1〜D4）",
    },
    # ---- Trang "Tìm kiếm" (Block 2 filters + Block 3 search) ---------------
    "search.filter_header": {"vi": "Bộ lọc dữ liệu (Block 2)", "ja": "データフィルター（Block 2）"},
    "search.facility_label": {"vi": "Cơ sở (facility)", "ja": "施設（facility）"},
    "search.facility_help": {
        "vi": "Tên đầy đủ có tiền tố chung \"{prefix}\" (đã rút gọn trong nhãn để tên cơ sở không bị cắt mất "
              "phần phân biệt) — xem Block 1 (Home) để tra tên đầy đủ.",
        "ja": "正式名称には共通の接頭辞「{prefix}」があります（ラベルでは省略し、識別に必要な部分が切れない"
              "ようにしています）— 正式名称は Block 1（Home）を参照してください。",
    },
    "search.month_range_caption": {
        "vi": "Phạm vi dữ liệu có: {min} → {max} (đơn vị: THÁNG)",
        "ja": "データの存在範囲：{min} → {max}（単位：月）",
    },
    "search.month_start_label": {"vi": "Từ tháng (YYYY-MM)", "ja": "開始月（YYYY-MM）"},
    "search.month_end_label": {"vi": "Đến tháng (YYYY-MM)", "ja": "終了月（YYYY-MM）"},
    "search.exclusion_radio_label": {
        "vi": "Cấp độ loại trừ cho Q31/Q32 (DEC-04-02)",
        "ja": "Q31/Q32 の除外粒度（DEC-04-02）",
    },
    "search.exclusion_opt_patient": {
        "vi": "Toàn kỳ tìm kiếm (mặc định, đúng 表7-1)",
        "ja": "検索期間全体（デフォルト、表7-1準拠）",
    },
    "search.exclusion_opt_month": {
        "vi": "Theo tháng (tùy chọn, REQ11 — KHÔNG phải cấp bản ghi thật) ⚠ CHƯA triển khai",
        "ja": "月単位（オプション、REQ11 — 実際のレコード単位ではない）⚠ 未実装",
    },
    "search.exclusion_month_warning": {
        "vi": "⚠ Chế độ 'Theo tháng' CHƯA được triển khai trong pipeline hiện tại — Q31/Q32 vẫn luôn được "
              "tính ở cấp toàn kỳ tìm kiếm (patient-level) dù đã chọn tùy chọn này. Nhãn "
              "`exclusion_granularity` trong CSV xuất ra sẽ ghi 'month' nhưng số liệu Q31/Q32 thực tế KHÔNG "
              "đổi theo — xem IMPLEMENTATION_TRACEABILITY.md §6. Không dùng tùy chọn này cho báo cáo chính thức.",
        "ja": "⚠「月単位」モードは現在のパイプラインには未実装です — このオプションを選んでもQ31/Q32は常に"
              "検索期間全体（患者単位）で計算されます。出力CSVの `exclusion_granularity` 列には 'month' と"
              "記録されますが、Q31/Q32 の実際の値は変わりません — IMPLEMENTATION_TRACEABILITY.md §6 参照。"
              "正式な報告にはこのオプションを使用しないでください。",
    },
    "search.reset_button": {"vi": "Đặt lại bộ lọc", "ja": "フィルターをリセット"},
    "search.title": {"vi": "Tìm kiếm ứng viên (Block 3)", "ja": "候補検索（Block 3）"},
    "search.info_full_dict": {
        "vi": "Pipeline áp dụng ĐẦY ĐỦ từ điển D1 (18 category)/D2 (89 search_term) đã được phê duyệt — "
              "không có control nào tắt riêng từng category/search_term (tránh làm sai lệch điều kiện Q10/Q20 chính thức).",
        "ja": "パイプラインは承認済みの D1（18カテゴリ）/D2（89 search_term）辞書を全件適用します — "
              "カテゴリ・search_term単位で個別にオフにするコントロールはありません（正式なQ10/Q20条件の"
              "ずれを防ぐため）。",
    },
    "search.warn_qc_not_official": {
        "vi": "⚠ 暫定 — QC1/QC2 (Tập C) KHÔNG phải Q chính thức của 表7-1 (DEC-04-01).",
        "ja": "⚠ 暫定 — QC1/QC2（集合C）は表7-1の正式なQではありません（DEC-04-01）。",
    },
    "search.warn_qc2_unverified": {
        "vi": "⚠ QC2 (C005-2) dùng chuỗi khớp CHƯA xác minh với dữ liệu thật (OPEN-04-01) — mọi khớp QC2 "
              "hiển thị là UNCONFIRMED, không bao giờ là Y.",
        "ja": "⚠ QC2（C005-2）の照合文字列は実データで未検証です（OPEN-04-01）— QC2の一致は常に"
              "UNCONFIRMEDと表示され、Yにはなりません。",
    },
    "search.model_info": {
        "vi": "Model v1.3.1: 1 candidate = 1 chuỗi tháng liên tục có算定注射用抗菌薬 (静注/点滴静注) cho "
              "1 bệnh nhân. Công cụ KHÔNG tự xác định treatment episode (quy tắc 14 ngày), Day 0, case_status "
              "hay転帰 — việc đó do reviewer làm trên file xuất ra (xem trang Xuất dữ liệu).",
        "ja": "モデル v1.3.1：1候補＝1人の患者について、注射用抗菌薬（静注／点滴静注）が算定された月が連続して"
              "いるひとまとまり。本ツールは治療エピソード（14日ルール）、Day 0、case_status、転帰を自動では"
              "判定しません — それらはレビュー担当者が出力ファイル上で行います（「データ出力」ページ参照）。",
    },
    "search.data_limit_warning": {
        "vi": "Giới hạn dữ liệu đã biết (không phải lỗi, xem addendum v1.3.1 Mục 2.9/§6): A06 (tuổi) và A07 "
              "(giới tính) luôn để trống — DB không có trường nhân khẩu học nào. Bệnh danh gắn vào candidate "
              "chỉ lọc theo ngày bắt đầu, không lọc theo ngày転帰 (DB không có cột này).",
        "ja": "既知のデータ制約（不具合ではありません。addendum v1.3.1 第2.9項/§6参照）：A06（年齢）と"
              "A07（性別）は常に空欄です — DBに人口統計学的フィールドが存在しないためです。候補に紐づく"
              "病名は開始日のみで絞り込み、転帰日では絞り込みません（DBにそのカラムがないため）。",
    },
    "search.dict_version_caption": {
        "vi": "Dictionary version: D1={d1} · D2={d2} · D3={d3} · D4={d4} · D6={d6} (DRAFT)",
        "ja": "辞書バージョン：D1={d1} · D2={d2} · D3={d3} · D4={d4} · D6={d6}（DRAFT）",
    },
    "search.run_button": {"vi": "▶ CHẠY TÌM KIẾM", "ja": "▶ 検索実行"},
    "search.spinner": {
        "vi": "Đang tải dữ liệu (chỉ đọc) và chạy pipeline D1→D2→D3→D4...",
        "ja": "データを読み込み（読み取り専用）、D1→D2→D3→D4 パイプラインを実行中...",
    },
    "search.success_msg": {
        "vi": "Xong — run_id={run_id} · {n_candidates} ứng viên ({n_disease} dòng bệnh danh, {n_medical} dòng thuốc đã quét).",
        "ja": "完了 — run_id={run_id} · 候補{n_candidates}件（傷病名{n_disease}行、医薬品{n_medical}行をスキャン）。",
    },
    "search.last_result_caption": {
        "vi": "Kết quả gần nhất: run_id={run_id} · {n_candidates} ứng viên.",
        "ja": "直近の結果：run_id={run_id} · 候補{n_candidates}件。",
    },
    "search.link_stats": {"vi": "➜ Xem thống kê (Block 4)", "ja": "➜ 統計を見る（Block 4）"},
    "search.link_candidates": {"vi": "➜ Xem danh sách ứng viên (Block 5)", "ja": "➜ 候補一覧を見る（Block 5）"},
    # ---- Dùng chung giữa nhiều trang (sau khi tìm kiếm) --------------------
    "common.no_run_warning": {"vi": "Chưa chạy tìm kiếm.", "ja": "検索がまだ実行されていません。"},
    "common.link_to_search": {"vi": "➜ Sang trang Tìm kiếm", "ja": "➜ 検索ページへ"},
    # ---- Trang "Thống kê" (Block 4) -----------------------------------------
    "stats.title": {"vi": "Thống kê ứng viên (Block 4)", "ja": "候補統計（Block 4）"},
    "stats.no_candidates": {
        "vi": "Không có ứng viên nào trong phạm vi tìm kiếm hiện tại.",
        "ja": "現在の検索範囲に該当する候補はありません。",
    },
    "stats.matrix_header": {
        "vi": "Ma trận 7 ô A/B/C (04_candidate_combination_matrix_vn.md)",
        "ja": "A/B/C 7セルマトリクス（04_candidate_combination_matrix_vn.md）",
    },
    "stats.matrix_caption": {
        "vi": "A = Q10 (bệnh danh hô hấp) · B = Q20 (kháng sinh tiêm) · C = QC1 (rộng, 暫定, DEC-04-01)",
        "ja": "A＝Q10（呼吸器系傷病名）・B＝Q20（注射用抗菌薬）・C＝QC1（広義、暫定、DEC-04-01）",
    },
    "stats.col_total": {"vi": "Tổng", "ja": "合計"},
    "stats.metric_total_a": {"vi": "Tổng A (Q10)", "ja": "A合計（Q10）"},
    "stats.metric_total_b": {"vi": "Tổng B (Q20)", "ja": "B合計（Q20）"},
    "stats.metric_total_c": {"vi": "Tổng C (QC1, 暫定)", "ja": "C合計（QC1、暫定）"},
    "stats.qc2_caption": {
        "vi": "c_narrow_c005_2 (QC2) = UNCONFIRMED trong: {n} ứng viên ⚠ chưa xác minh (OPEN-04-01).",
        "ja": "c_narrow_c005_2（QC2）＝UNCONFIRMED：候補{n}件 ⚠ 未検証（OPEN-04-01）。",
    },
    "stats.d3_header": {
        "vi": "Phân bố D3 (chỉ trong Q30) — tín hiệu ưu tiên rà soát, KHÔNG phải kết luận lâm sàng",
        "ja": "D3の分布（Q30内のみ）— レビュー優先度の目安であり、臨床的な結論ではありません",
    },
    "stats.metric_competing": {
        "vi": "Số ứng viên có cờ 'cạnh tranh chẩn đoán' (APPLY-4, category O)",
        "ja": "「競合診断」フラグが立った候補数（APPLY-4、カテゴリO）",
    },
    "stats.by_clinic_header": {"vi": "Phân bố theo cơ sở", "ja": "施設別の分布"},
    "stats.col_candidate_count": {"vi": "Số ứng viên", "ja": "候補数"},
    "stats.unconfirmed_header": {
        "vi": "Trường dữ liệu chưa xác nhận / phụ thuộc EHR ngoài ORCA (cố định, không thể ẩn)",
        "ja": "未確認／ORCA外EHR依存のデータ項目（固定、非表示不可）",
    },
    "stats.col_field": {"vi": "Trường", "ja": "項目"},
    "stats.row_req02_field": {
        "vi": "REQ02 — ngày bắt đầu/kết cục cho bệnh danh",
        "ja": "REQ02 — 傷病名の発症日／転帰日",
    },
    "stats.status_req02": {
        "vi": "Phụ thuộc EHR ngoài ORCA (Session 02, 2026-11-04)",
        "ja": "ORCA外EHRに依存（Session 02、2026-11-04）",
    },
    "stats.row_req03_field": {"vi": "REQ03 — ngày cấp thuốc theo ngày", "ja": "REQ03 — 投薬日（日単位）"},
    "stats.status_req03": {
        "vi": "Phụ thuộc EHR ngoài ORCA (chỉ có perform_month)",
        "ja": "ORCA外EHRに依存（perform_monthのみ保持）",
    },
    "stats.status_zzz": {
        "vi": "{n} ứng viên có cờ — ý nghĩa chưa xác nhận (Session 02 nghi vấn #3)",
        "ja": "候補{n}件にフラグあり — 意味は未確認（Session 02 疑問点#3）",
    },
    "stats.status_qc2": {"vi": "Chuỗi khớp chưa xác minh (OPEN-04-01)", "ja": "照合文字列は未検証（OPEN-04-01）"},
    "stats.status_d4": {
        "vi": "Chưa ánh xạ được lên cột DB (OPEN-04-02) — QC1 chỉ ở mức medical_class thô",
        "ja": "DB列へのマッピング未確認（OPEN-04-02）— QC1はmedical_classの粗い単位のみ",
    },
    # ---- Trang "Thống kê" — 複合急変 / 集計保留 (ADDENDUM 2026-11-08, v1.1 §9) ----
    "stats.outcome_header": {
        "vi": "Tỷ lệ biến chứng 30 ngày (複合急変, §9) — cần đã tải lên file Rà soát + Kết cục",
        "ja": "30日複合急変割合（§9）— レビュー＋転帰ファイルのアップロードが必要",
    },
    "stats.outcome_no_data": {
        "vi": "Chưa có dữ liệu Rà soát/Kết cục đã tải lên trong phiên này — sang trang Xuất dữ liệu "
              "(Block 7) để tải lên `07_manual_review` và `08_outcome` đã điền, rồi quay lại đây.",
        "ja": "このセッションではレビュー／転帰データがまだアップロードされていません — 「データ出力」"
              "ページ（Block 7）で記入済みの `07_manual_review` と `08_outcome` をアップロードしてから"
              "お戻りください。",
    },
    "stats.outcome_caveat": {
        "vi": "⚠ Chưa triển khai luật differ-loop §6 (\"3 転帰 đều なし nhưng追跡未đủ\" → trả rà soát sơ "
              "cấp trước khi = 確認不能) — cần Session04 chốt spec. Hiện tại episode có cả 3 転帰 = N luôn "
              "tính là 複合なし.",
        "ja": "⚠ §6の差し戻しルール（「3転帰すべて『なし』だが追跡不十分」→確認不能とする前に一次レビュー"
              "へ差し戻す）は未実装（Session04のスペック確定待ち）。現在は3転帰すべて「なし」のエピソード"
              "は常に複合「なし」として扱われます。",
    },
    "stats.outcome_denominator_t": {"vi": "Mẫu số T (対象, đã trừ 集計保留)", "ja": "分母T（対象、集計保留を除く）"},
    "stats.outcome_held_back": {"vi": "Số episode bị loại khỏi T (集計保留フラグ)", "ja": "Tから除外した件数（集計保留フラグ）"},
    "stats.outcome_composite_rate": {"vi": "Tỷ lệ 複合急変 あり", "ja": "複合急変「あり」割合"},
    "stats.outcome_fukaku_rate": {"vi": "Tỷ lệ 確認不能 (trên tổng T)", "ja": "確認不能割合（T全体に対して）"},
    "stats.outcome_admission_rate": {"vi": "Tỷ lệ nhập viện (B06)", "ja": "入院割合（B06）"},
    "stats.outcome_transport_rate": {"vi": "Tỷ lệ cấp cứu (B08)", "ja": "救急搬送割合（B08）"},
    "stats.outcome_death_rate": {"vi": "Tỷ lệ tử vong (B10)", "ja": "死亡割合（B10）"},
    # ---- Trang "Thống kê" (model v1.3.1, dùng thật bởi 2_Thong_ke.py) -------
    "stats.overview_header": {"vi": "Tổng quan", "ja": "概要"},
    "stats.metric_candidates": {"vi": "Số candidate", "ja": "候補数"},
    "stats.metric_patients": {"vi": "Số bệnh nhân (施設+患者番号)", "ja": "患者数（施設＋患者番号）"},
    "stats.metric_facilities": {"vi": "Số cơ sở", "ja": "施設数"},
    "stats.by_group_header": {"vi": "Theo nhóm NAHT/HOMIS", "ja": "グループ別（NAHT/HOMIS）"},
    "stats.by_route_header": {"vi": "Theo đường dùng (A13 route_class)", "ja": "投与経路別（A13 route_class）"},
    "stats.route_caption": {
        "vi": "皮下筋肉注射 (medical_class 31) không được tính là candidate, không xuất hiện ở đây.",
        "ja": "皮下筋肉注射（medical_class 31）は候補としてカウントされないため、ここには表示されません。",
    },
    "stats.length_header": {
        "vi": "Độ dài candidate (số tháng liên tục có算定)",
        "ja": "候補の期間（算定が連続した月数）",
    },
    "stats.diagnosis_header": {
        "vi": "Bệnh danh gắn vào candidate (A16 diagnosis_categories)",
        "ja": "候補に紐づく病名（A16 diagnosis_categories）",
    },
    "stats.diagnosis_caption": {
        "vi": "Mỗi candidate có thể có nhiều病名, mỗi病名 có 1 trạng thái: A=確定（活動性）, S=疑い, "
              "theo D1_修飾語. 保留「呼吸器感染症の疑い」(B02) vẫn là quyết định của reviewer, không phải ở đây.",
        "ja": "1候補に複数の病名が紐づくことがあり、各病名はD1_修飾語によりA=確定（活動性）／S=疑いのいずれかの"
              "状態を持ちます。保留「呼吸器感染症の疑い」（B02）はあくまでレビュー担当者の判断であり、ここでの"
              "分類ではありません。",
    },
    "stats.diagnosis_counts_caption": {
        "vi": "⚪ 確定/活動性 (A): {a} lượt   ·   🟡 疑い (S): {s} lượt — luôn tách biệt, không gộp chung.",
        "ja": "⚪ 確定/活動性（A）：{a}件　・　🟡 疑い（S）：{s}件 — 常に別々に表示し、合算しません。",
    },
    "stats.no_diagnosis": {"vi": "Không có病名 nào được gắn.", "ja": "病名は紐づいていません。"},
    "stats.table_col_item": {"vi": "Hạng mục", "ja": "項目"},
    "stats.table_col_status": {"vi": "Trạng thái", "ja": "状態"},
    "stats.row1_status": {
        "vi": "Luôn trống — DB không có trường nhân khẩu học",
        "ja": "常に空欄 — DBに人口統計学的フィールドが存在しない",
    },
    "stats.row2_status": {
        "vi": "DB không có cột này — chỉ lọc theo ngày bắt đầu",
        "ja": "DBにこのカラムは存在しない — 開始日のみで絞り込み",
    },
    "stats.row3_status": {
        "vi": "Chưa xác minh đầy đủ với medical_class thật — xem addendum Mục 5 #6",
        "ja": "実際のmedical_classでの検証がまだ不十分 — addendum 第5項#6参照",
    },
    "stats.row4_status": {
        "vi": "Chưa có ý nghĩa chính thức, chỉ đánh dấu",
        "ja": "正式な意味はまだなく、フラグのみ",
    },
    "stats.outcome_decision_caption": {
        "vi": "Quyết định tạm thời 2026-11-11: 保留 KHÔNG vào mẫu số chính, chỉ báo riêng. Nhập viện tính cả "
              "2 cách (toàn bộ / chỉ ngoài kế hoạch) vì công thức急変率 chính thức chưa chốt (addendum Mục 5 #1).",
        "ja": "2026-11-11暫定決定：保留は主分母に含めず、別掲のみとします。急変率の正式な計算式がまだ確定して"
              "いないため（addendum 第5項#1）、入院は2通り（入院すべて／予定外のみ）の両方で集計します。",
    },
    "stats.metric_denominator": {"vi": "Mẫu số chính (対象, qua QC)", "ja": "主分母（対象、QC通過）"},
    "stats.metric_held_back": {"vi": "保留 (báo riêng)", "ja": "保留（別掲）"},
    "stats.metric_not_qc": {"vi": "対象 nhưng chưa qua QC", "ja": "対象だがQC未通過"},
    "stats.tab_all_admissions": {"vi": "Định nghĩa 1: toàn bộ nhập viện", "ja": "定義1：入院すべて"},
    "stats.tab_unplanned": {"vi": "Định nghĩa 2: chỉ ngoài kế hoạch", "ja": "定義2：予定外のみ"},
    "stats.ratio_formula_caption": {
        "vi": "Mọi tỉ lệ đều tính bằng あり ÷ (あり + なし). Số dòng/tỉ lệ 確認不能 không được tính vào tử số "
              "(CSV設計説明書v1.3.1 §8).",
        "ja": "割合はいずれもあり÷（あり＋なし）。確認不能の件数・割合は分子に含めない（CSV設計説明書v1.3.1 "
              "§8）。",
    },
    "stats.no_review_uploaded": {
        "vi": "Chưa có file review đã điền B/C được upload (trang Danh sách ứng viên / Xuất dữ liệu).",
        "ja": "記入済みB/Cのレビューファイルがまだアップロードされていません"
              "（「候補一覧」／「データ出力」ページ参照）。",
    },
    # ---- Trang "Danh sách ứng viên" (Block 5) -------------------------------
    "candidates.title": {"vi": "Danh sách ứng viên (Block 5)", "ja": "候補一覧（Block 5）"},
    "candidates.no_candidates": {"vi": "Không có ứng viên nào.", "ja": "候補がありません。"},
    "candidates.small_clinic_warning": {
        "vi": "⚠ Cơ sở nhỏ ({n} ứng viên trong kết quả hiện tại, OPEN-05-01) — candidate_id gần như định "
              "danh được cá nhân nếu kết hợp thông tin ngoài. Cân nhắc kiểm soát truy cập trước khi chia sẻ.",
        "ja": "⚠ 小規模施設（現在の結果に候補{n}件、OPEN-05-01）— candidate_id は外部情報と組み合わせると"
              "個人を特定できる可能性があります。共有前にアクセス制御を検討してください。",
    },
    "candidates.upload_header": {
        "vi": "⬆ Nạp Review/Outcome CSV đã điền (chỉ đọc)",
        "ja": "⬆ 記入済み Review/Outcome CSVを読み込む（読み取り専用）",
    },
    "candidates.upload_review_label": {
        "vi": "07_manual_review_template.csv đã điền",
        "ja": "記入済み 07_manual_review_template.csv",
    },
    "candidates.upload_outcome_label": {
        "vi": "08_outcome_template.csv đã điền",
        "ja": "記入済み 08_outcome_template.csv",
    },
    "candidates.loaded_review_msg": {
        "vi": "Đã nạp {n} dòng Review (chỉ đọc).",
        "ja": "Reviewを{n}行読み込みました（読み取り専用）。",
    },
    "candidates.loaded_outcome_msg": {
        "vi": "Đã nạp {n} dòng Outcome (chỉ đọc).",
        "ja": "Outcomeを{n}行読み込みました（読み取り専用）。",
    },
    "candidates.quick_filter_header": {"vi": "Bộ lọc nhanh", "ja": "クイックフィルター"},
    "candidates.filter_source_label": {"vi": "Nguồn (combination_cell)", "ja": "出所（combination_cell）"},
    "candidates.filtered_caption": {"vi": "{shown}/{total} ứng viên sau lọc.", "ja": "フィルター後：{shown}/{total} 件。"},
    "candidates.col_evidence": {"vi": "Evidence (D/M/P)", "ja": "エビデンス（D/M/P）"},
    "candidates.detail_header": {"vi": "Xem chi tiết 1 ứng viên", "ja": "候補の詳細を見る"},
    "candidates.open_detail_button": {"vi": "➜ Mở chi tiết (Block 6)", "ja": "➜ 詳細を開く（Block 6）"},
    "candidates.link_export": {"vi": "➜ Sang trang Xuất dữ liệu (Block 7)", "ja": "➜ データ出力ページへ（Block 7）"},
    # ---- model v1.3.1, dùng thật bởi 3_Danh_sach_ung_vien.py ----------------
    "candidates.upload_v131_header": {
        "vi": "Upload file review đã điền (B/C)", "ja": "記入済みレビューファイルをアップロード（B/C）",
    },
    "candidates.upload_v131_caption": {
        "vi": "v1.3.1: chỉ 1 file (41 cột) — không còn 2 file Manual Review / Outcome riêng.",
        "ja": "v1.3.1：ファイルは1つ（41列）のみ — Manual Review/Outcomeの2ファイルに分かれていません。",
    },
    "candidates.upload_v131_label": {"vi": "File review (CSV, 41 cột)", "ja": "レビューファイル（CSV、41列）"},
    "candidates.route_label": {"vi": "Đường dùng (A13)", "ja": "投与経路（A13）"},
    "candidates.suspect_checkbox": {
        "vi": "Chỉ candidate có病名疑い (S)", "ja": "病名疑い（S）がある候補のみ",
    },
    # ---- Trang "Chi tiết ứng viên" (Block 6) --------------------------------
    "detail.no_candidate_selected": {"vi": "Chưa chọn candidate_id.", "ja": "candidate_idが選択されていません。"},
    "detail.link_back_to_list": {"vi": "➜ Quay lại danh sách ứng viên", "ja": "➜ 候補一覧に戻る"},
    "detail.candidate_not_found": {
        "vi": "candidate_id không tồn tại trong kết quả hiện tại.",
        "ja": "candidate_id は現在の結果に存在しません。",
    },
    "detail.title": {"vi": "Chi tiết ứng viên: {id}", "ja": "候補の詳細：{id}"},
    "detail.metric_combination_cell": {"vi": "Nhóm tổ hợp", "ja": "組み合わせセル"},
    "detail.metric_competing": {"vi": "Cạnh tranh chẩn đoán", "ja": "競合診断"},
    "detail.progress_label": {
        "vi": "Tiến độ nội bộ (KHÔNG phải Review Record thật — không xuất vào CSV nào)",
        "ja": "内部進捗（実際のReview Recordではありません — どのCSVにも出力されません）",
    },
    "detail.review_record_header": {
        "vi": "Review Record / Outcome Event thật (chỉ đọc, đã nạp)",
        "ja": "実際の Review Record／Outcome Event（読み取り専用、読み込み済み）",
    },
    "detail.no_review_row_caption": {
        "vi": "Chưa có dòng Review Record nào cho candidate_id này trong file đã nạp.",
        "ja": "読み込んだファイルにこの candidate_id の Review Record はありません。",
    },
    "detail.disease_evidence_header": {"vi": "Bằng chứng bệnh danh ({n} dòng)", "ja": "傷病名の根拠（{n}行）"},
    "detail.no_rows_caption": {"vi": "— không có dòng nào", "ja": "— 該当する行はありません"},
    "detail.medication_evidence_header": {"vi": "Bằng chứng thuốc ({n} dòng)", "ja": "薬剤の根拠（{n}行）"},
    "detail.medication_ehr_caption": {
        "vi": "⚠ Phụ thuộc EHR ngoài ORCA (REQ03) — perform_month là tháng, KHÔNG phải ngày dùng thuốc cụ thể.",
        "ja": "⚠ ORCA外EHRに依存（REQ03）— perform_monthは月単位であり、実際の投与日ではありません。",
    },
    "detail.procedure_evidence_header": {"vi": "Bằng chứng thủ thuật/truyền dịch ({n} dòng)", "ja": "手技・輸液の根拠（{n}行）"},
    "detail.no_procedure_rows_caption": {
        "vi": "— không có dòng nào (bệnh nhân NAHT thường không có medical_points; QC1/QC2 cũng có thể không khớp).",
        "ja": "— 該当する行はありません（NAHTの患者は通常medical_pointsを持たず、QC1/QC2も一致しない場合があります）。",
    },
    "detail.q40_header": {
        "vi": "Gợi ý kết cục Q40 (chỉ dấu, KHÔNG xác nhận outcome) — {n} hit",
        "ja": "Q40転帰ヒント（手がかりのみ、転帰を確定しません）— {n}件",
    },
    "detail.no_hit_caption": {"vi": "Không có hit.", "ja": "ヒットなし。"},
    "detail.q40_disclaimer": {
        "vi": "KHÔNG xác nhận outcome — cần giấy chuyển viện/giấy báo tử/bệnh án, không chỉ dựa vào billing hint.",
        "ja": "転帰は確定しません — 紹介状／死亡診断書／診療録が必要で、billing hintのみでは判断できません。",
    },
    "detail.download_evidence_label": {
        "vi": "⬇ Xuất 3 Evidence CSV (gộp 1 file để tải nhanh — các file riêng ở Block 7)",
        "ja": "⬇ 3種のEvidence CSVを出力（1ファイルにまとめて高速ダウンロード — 個別ファイルはBlock 7）",
    },
    "detail.download_review_label": {
        "vi": "⬇ Xuất Review Template trống (1 dòng)",
        "ja": "⬇ 空のReview Templateを出力（1行）",
    },
    # ---- model v1.3.1, dùng thật bởi 4_Chi_tiet_benh_nhan.py ----------------
    "detail.metric_month_range": {"vi": "Tháng đầu/cuối", "ja": "開始/終了月"},
    "detail.metric_months_count": {"vi": "Số tháng liên tục", "ja": "連続月数"},
    "detail.drug_v131_header": {
        "vi": "Thuốc kháng sinh tiêm/truyền (A11-A12)", "ja": "注射・点滴抗菌薬（A11-A12）",
    },
    "detail.drug_name_label": {"vi": "**Tên thuốc:**", "ja": "**薬剤名：**"},
    "detail.drug_code_label": {"vi": "**Mã thuốc:**", "ja": "**薬剤コード：**"},
    "detail.diagnosis_v131_header": {
        "vi": "病名 gắn vào candidate (A14-A16)", "ja": "候補に紐づく病名（A14-A16）",
    },
    "detail.diagnosis_state_caption": {
        "vi": "Mỗi病名 có 1 trạng thái D1 riêng (A=確定/活動性, S=疑い) — hiển thị tách biệt, không gộp.",
        "ja": "各病名はD1固有の状態（A=確定/活動性、S=疑い）を持ち、合算せず別々に表示します。",
    },
    "detail.no_diagnosis_v131_caption": {
        "vi": "Không có病名 nào được gắn trong khung thời gian của candidate này.",
        "ja": "この候補の期間には病名が紐づいていません。",
    },
    "detail.evidence_v131_header": {"vi": "Evidence reference (A17)", "ja": "エビデンス参照（A17）"},
    "detail.progress_not_reviewed": {"vi": "Chưa rà soát", "ja": "未確認"},
    "detail.progress_in_review": {"vi": "Đang rà soát", "ja": "確認中"},
    "detail.progress_reviewed": {"vi": "Đã xem", "ja": "確認済"},
    "detail.review_data_v131_header": {
        "vi": "Dữ liệu review đã upload cho candidate này", "ja": "この候補にアップロードされたレビューデータ",
    },
    "detail.no_review_match_caption": {
        "vi": "Chưa có dòng review nào khớp candidate_id này trong file đã upload.",
        "ja": "アップロードしたファイルにこのcandidate_idに一致する行がありません。",
    },
    "detail.download_review_v131_button": {
        "vi": "⬇ Tải file review (41 cột, A đã điền, B/C trống) cho candidate này",
        "ja": "⬇ この候補のレビューファイルをダウンロード（41列、A記入済み、B/C空欄）",
    },
    # ---- Trang "Xuất dữ liệu" (Block 7) -------------------------------------
    "export.title": {"vi": "Xuất dữ liệu (Block 7)", "ja": "データ出力（Block 7）"},
    "export.draft_warning": {
        "vi": "⚠ Theo đặc tả Session 05 (DRAFT) — DEC-05-01 (phạm vi Candidate CSV = union 7 ô), "
              "DEC-05-02/03/04 chưa được chủ dự án phê duyệt. Xuất ra vẫn hợp lệ cho thử nghiệm/rà soát nội bộ, "
              "nhưng cấu trúc có thể đổi khi các quyết định này chốt.",
        "ja": "⚠ Session 05仕様（DRAFT）に基づく — DEC-05-01（Candidate CSVの範囲＝7セルの和集合）、"
              "DEC-05-02/03/04はプロジェクトオーナー未承認です。出力自体は試験・内部レビュー用として有効"
              "ですが、これらの決定が確定すると構造が変わる可能性があります。",
    },
    "export.run_caption": {"vi": "run_id = {run_id} · {n} ứng viên", "ja": "run_id = {run_id} · 候補{n}件"},
    "export.blank_files_header": {
        "vi": "File người tạo (trống) — dashboard không bao giờ tự điền cột lâm sàng",
        "ja": "人が記入するファイル（空）— ダッシュボードは臨床列を自動入力しません",
    },
    "export.dl_review_template": {"vi": "⬇ 07_manual_review_template.csv (trống)", "ja": "⬇ 07_manual_review_template.csv（空）"},
    "export.dl_outcome_template": {"vi": "⬇ 08_outcome_template.csv (trống)", "ja": "⬇ 08_outcome_template.csv（空）"},
    "export.outcome_disabled_help": {
        "vi": "Cần nạp file 07 đã điền có episode_id trước khi xuất Outcome Template.",
        "ja": "Outcome Templateを出力する前に、episode_id入りの記入済み07ファイルを読み込む必要があります。",
    },
    "export.supp_header": {
        "vi": "Export bổ sung — schema 39 cột (song song, ADDENDUM 2026-11-05)",
        "ja": "追加出力 — 39列スキーマ（並行、ADDENDUM 2026-11-05）",
    },
    "export.supp_warning": {
        "vi": "⚠ Phần lớn cột A (tự động trích xuất) để trống — chưa có quy tắc tổng hợp được chủ dự án phê duyệt "
              "(xem session05/11_supplementary_csv_schema_mapping_vn.md). Export này bổ sung song song cho REQ12, "
              "KHÔNG thay thế 6 file ở trên.",
        "ja": "⚠ A列（自動抽出）の大部分は空欄です — プロジェクトオーナー承認済みの集計ルールがまだありません"
              "（session05/11_supplementary_csv_schema_mapping_vn.md参照）。この出力はREQ12の並行追加であり、"
              "上記6ファイルを置き換えるものではありません。",
    },
    "export.dl_supplementary": {"vi": "⬇ 12_supplementary_export.csv (39 cột)", "ja": "⬇ 12_supplementary_export.csv（39列）"},
    "export.supp_disabled_help": {
        "vi": "Cần nạp CẢ file 07 đã điền (có episode_id) VÀ file 08 đã điền ở dưới trước khi xuất.",
        "ja": "出力前に、episode_id入りの記入済み07ファイルと記入済み08ファイルの両方を読み込む必要があります。",
    },
    "export.upload_header": {"vi": "⬆ Nạp 07/08 đã điền (chỉ đọc)", "ja": "⬆ 記入済み 07/08 を読み込む（読み取り専用）"},
    "export.loaded_generic_msg": {"vi": "Đã nạp {n} dòng.", "ja": "{n}行を読み込みました。"},
    # ---- model v1.3.1, dùng thật bởi 5_Xuat_du_lieu.py ----------------------
    "export.create_csv_button": {"vi": "🔄 Tạo file CSV", "ja": "🔄 CSVファイルを作成"},
    "export.not_created_info": {
        "vi": "Bấm 'Tạo file CSV' ở trên để tạo file tải xuống cho lần chạy hiện tại.",
        "ja": "上の「CSVファイルを作成」を押すと、今回の実行結果のダウンロードファイルを作成します。",
    },
    "export.dl_candidate_v131_button": {
        "vi": "⬇ Candidate (17 cột A, chỉ tool)", "ja": "⬇ 候補（Aの17列のみ、ツール出力）",
    },
    "export.dl_review_v131_button": {
        "vi": "⬇ File review (41 cột, A đã điền + B/C trống)",
        "ja": "⬇ レビューファイル（41列、A記入済み＋B/C空欄）",
    },
    "export.col_dict_caption": {
        "vi": "📖 File riêng giải thích ý nghĩa 41 cột bằng tiếng Nhật, lấy nguyên văn từ "
              "CSV設計説明書v1.3.1 §4 — không tự dịch/diễn giải lại (CLAUDE.md mục 3).",
        "ja": "📖 41列それぞれの意味を日本語で説明する別ファイルです。CSV設計説明書v1.3.1 §4の原文のまま"
              "であり、独自に翻訳・解釈し直してはいません（CLAUDE.md 第3項）。",
    },
    "export.dl_col_dict_button": {
        "vi": "⬇ Từ điển cột (column_dictionary.csv, 41 dòng)", "ja": "⬇ 列の説明（column_dictionary.csv、41行）",
    },
    "export.qc_upload_header": {
        "vi": "Upload file review đã điền để kiểm tra (V01-V09)",
        "ja": "記入済みレビューファイルをアップロードしてチェック（V01-V09）",
    },
    "export.qc_caption": {
        "vi": "Điểm kiểm tra chỉ tìm lỗi nhập liệu (CSV設計説明書v1.3.1 §7) — không đánh giá case_status/Day0/"
              "転帰 có ĐÚNG hay không, chỉ xem có NHẤT QUÁN hay không. Người二次確認 (C01/C02) vẫn là người quyết.",
        "ja": "このチェックは入力ミスのみを検出します（CSV設計説明書v1.3.1 §7）— case_status/Day0/転帰が"
              "正しいかどうかは判定せず、一貫しているかどうかのみを見ます。二次確認（C01/C02）は引き続き人が"
              "判断します。",
    },
    "export.qc_no_issues": {
        "vi": "Không phát hiện vấn đề nào qua V01-V09.", "ja": "V01-V09でのチェックで問題は見つかりませんでした。",
    },
    "export.qc_issues_warning": {
        "vi": "{n} dòng có vấn đề — {n_error} lỗi (エラー), {n_warn} cảnh báo (警告).",
        "ja": "{n}行に問題があります — エラー{n_error}件、警告{n_warn}件。",
    },
    "export.qc_col_row": {"vi": "dòng", "ja": "行"},
    "export.qc_col_level": {"vi": "mức", "ja": "レベル"},
    "export.qc_col_content": {"vi": "nội dung", "ja": "内容"},
    # ---- Cột dùng chung ----------------------------------------------------
    "col.order": {"vi": "Thứ tự", "ja": "順序"},
    "col.id": {"vi": "Mã", "ja": "ID"},
    "col.code": {"vi": "Mã", "ja": "コード"},
    "col.name_jp": {"vi": "Tên (tiếng Nhật, nguyên bản)", "ja": "名称（原文）"},
    "col.pattern": {"vi": "Tiêu chí khớp (nguyên bản)", "ja": "判定条件（原文）"},
    "col.status": {"vi": "Trạng thái", "ja": "ステータス"},
    "col.disposition": {"vi": "Xử lý khi khớp (nguyên bản)", "ja": "一致時の扱い（原文）"},
    "col.search_term": {"vi": "search_term", "ja": "search_term"},
    "col.group": {"vi": "Nhóm", "ja": "グループ"},
    "col.confirmed": {"vi": "Trạng thái xác nhận", "ja": "確認状況"},
    "col.form_check": {"vi": "Cần kiểm tra dạng bào chế", "ja": "剤形確認要"},
    "col.description": {"vi": "Mô tả (nguyên bản)", "ja": "説明（原文）"},
    "col.members": {"vi": "Thành phần (nguyên bản)", "ja": "構成成分（原文）"},
    "col.row_type": {"vi": "Loại hàng", "ja": "行種別"},
    "col.category": {"vi": "Phân loại (nguyên bản)", "ja": "分類（原文）"},
    "col.confirmation_status": {"vi": "Trạng thái xác nhận", "ja": "確認状況"},
    "col.source": {"vi": "Nguồn (tài liệu + mục/bảng)", "ja": "出典（文書＋章・表）"},
}
