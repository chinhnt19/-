"""Japanese column descriptions for the 41-column unified CSV (17 A-columns
from the tool + 22 B-columns the chart reviewer fills in + 2 C QC columns).

Copied verbatim from 後ろ向き集計 CSV設計説明書v1.3.1 §4 (tables for A01-A17,
B01-B22, C01-C02) -- never invent or re-translate a column's meaning here
(CLAUDE.md §3: "Never invent missing medical terms... Do not silently modify
or reinterpret its rules."). Column order/names themselves are fixed in
models/csv_schemas.py; this module only adds the Japanese explanation text
for display (dashboard tooltips, CSV column-dictionary export). No Vietnamese
translation of `description`/`type_value` -- confirmed with project owner
2026-11-12: these are research/CSV-spec definition text (same category as
D1-D4 dictionary content), not tool UI chrome, so services/i18n.py's
"never translate dictionary content" rule applies here too.

`label_ja`: a short Japanese display label per column, 2026-11-12 addition.
Not a separate field in the source document (後ろ向き集計 CSV設計説明書v1.3.1
has no distinct "Japanese column name" -- only the English key itself as
"列名" and this `description` prose; confirmed by direct read of §3-§4). Each
`label_ja` here is a compression of that already-approved `description` text
into a short label (e.g. "患者ID" from patient_local_id's "施設内の患者番号"),
not a new/independent definition. Used ONLY to build the human-readable
"label_ja_english_key" column-name format in exports/export_csv.py's
column_dictionary.csv (reviewer-facing helper file) -- per project owner
request 2026-11-12. Does NOT apply to the real candidate_*.csv/review_*.csv
headers, which stay the plain English key per 手順書/CSV設計説明書v1.3.1 §3
("1行目は列名（4章の英字の列名）") -- changing those would contradict the
正本, so this hybrid format is deliberately scoped to the dictionary file
only.
"""
from __future__ import annotations

COLUMN_GLOSSARY: dict[str, dict[str, str]] = {
    "extract_batch_id": {"code": "A01", "label_ja": "抽出バッチID", "type_value": "文字列", "description": "抽出処理の識別子。抽出日時、対象期間、検索条件の版、データ取得最終日を、この識別子ごとに別に記録する"},
    "candidate_id": {"code": "A02", "label_ja": "候補ID", "type_value": "文字列（一意）", "description": "候補のID。「施設ID:患者番号:最初の算定月」とする（例：clinic_001:00000004:2025-11）。同じ条件で再抽出したときも同じIDになる"},
    "facility_id": {"code": "A03", "label_ja": "施設ID", "type_value": "文字列", "description": "施設のID"},
    "patient_local_id": {"code": "A04", "label_ja": "患者ID", "type_value": "文字列", "description": "施設内の患者番号。数値型にしない（先頭の0を消さない）"},
    "ehr_source": {"code": "A05", "label_ja": "電子カルテ種別", "type_value": "列挙：NAHT／HOMIS", "description": "レビューで開く電子カルテ"},
    "age_at_start": {"code": "A06", "label_ja": "開始時年齢", "type_value": "整数", "description": "A08の月の初日の年齢"},
    "sex": {"code": "A07", "label_ja": "性別", "type_value": "文字列", "description": "ORCAに登録された性別"},
    "first_record_month": {"code": "A08", "label_ja": "初回算定月", "type_value": "年月", "description": "候補の最初の算定月。Day 0はレビューで決める"},
    "last_record_month": {"code": "A09", "label_ja": "最終算定月", "type_value": "年月", "description": "候補の最後の算定月"},
    "record_months": {"code": "A10", "label_ja": "算定月数", "type_value": "整数", "description": "算定のあった月の数"},
    "drug_names": {"code": "A11", "label_ja": "薬剤名", "type_value": "文字列（複数）", "description": "注射用抗菌薬の名称（ORCAの表記のまま）"},
    "drug_codes": {"code": "A12", "label_ja": "医薬品コード", "type_value": "文字列（複数）", "description": "医薬品コード（A11と同じ順）"},
    "route_class": {"code": "A13", "label_ja": "投与経路", "type_value": "複数列挙：静注／点滴静注", "description": "ORCAの注射の区分から判定した投与経路"},
    "diagnosis_names": {"code": "A14", "label_ja": "病名", "type_value": "文字列（複数）", "description": "候補の期間に有効だった病名（6章）。元の表記のまま"},
    "diagnosis_codes": {"code": "A15", "label_ja": "病名コード", "type_value": "文字列（複数）", "description": "病名コード（A14と同じ順）"},
    "diagnosis_categories": {"code": "A16", "label_ja": "病名区分", "type_value": "文字列（複数）", "description": "病名辞書による区分と状態（例：PS:A|PG:S）。A14と同じ順。形式は「検索ツールの設計基準と辞書」2.2節"},
    "evidence_ref": {"code": "A17", "label_ja": "エビデンス参照", "type_value": "文字列（複数）", "description": "ORCAの元の記録に戻るための参照キー"},
    "episode_id": {"code": "B01", "label_ja": "エピソードID", "type_value": "文字列（一意）", "description": "治療エピソードのID。「candidate_id-連番」とする（例：clinic_001:00000004:2025-11-1）。1つの候補に治療が2つ以上あるときは、行をコピーして連番を付ける（6.4）"},
    "case_status": {"code": "B02", "label_ja": "対象判定", "type_value": "列挙：対象／対象外／保留", "description": "研究対象かどうかの判定"},
    "case_reason": {"code": "B03", "label_ja": "判定理由", "type_value": "列挙（語彙は9章）", "description": "理由のコード"},
    "day0_date": {"code": "B04", "label_ja": "Day0日付", "type_value": "日付", "description": "在宅で初めて抗菌薬を静注または点滴静注した日"},
    "day0_evidence": {"code": "B05", "label_ja": "Day0根拠", "type_value": "文字列", "description": "Day 0の投与を確認した記録の参照キー"},
    "last_infusion_date": {"code": "B06", "label_ja": "最終投与日", "type_value": "日付", "description": "在宅で最後に抗菌薬を静注または点滴静注した日"},
    "infusion_days": {"code": "B07", "label_ja": "投与日数", "type_value": "整数", "description": "投与した日数"},
    "home_completed": {"code": "B08", "label_ja": "在宅完了", "type_value": "列挙：はい／いいえ／不明", "description": "入院せずに、在宅で抗菌薬の治療を終えたか"},
    "residence_type": {"code": "B09", "label_ja": "居住形態", "type_value": "列挙：自宅／施設／不明", "description": "Day 0の時点の居住形態"},
    "admission_30d": {"code": "B10", "label_ja": "30日以内入院", "type_value": "列挙：あり／なし／不明", "description": "Day 0からDay 30までの入院"},
    "admission_date": {"code": "B11", "label_ja": "入院日", "type_value": "日付", "description": "入院した日"},
    "admission_type": {"code": "B12", "label_ja": "入院区分", "type_value": "列挙：予定／予定外／不明", "description": "入院の区分"},
    "admission_facility": {"code": "B13", "label_ja": "入院先", "type_value": "文字列", "description": "入院先（分かる範囲）"},
    "transport_30d": {"code": "B14", "label_ja": "30日以内搬送", "type_value": "列挙：あり／なし／不明", "description": "Day 0からDay 30までの救急搬送。救急車を呼んだが搬送されなかった場合は「あり」にしない"},
    "transport_date": {"code": "B15", "label_ja": "搬送日", "type_value": "日付", "description": "搬送された日"},
    "death_30d": {"code": "B16", "label_ja": "30日以内死亡", "type_value": "列挙：あり／なし／不明", "description": "Day 0からDay 30までの死亡（原因を問わない）"},
    "death_date": {"code": "B17", "label_ja": "死亡日", "type_value": "日付", "description": "死亡した日"},
    "death_place": {"code": "B18", "label_ja": "死亡場所", "type_value": "列挙：自宅／施設／病院／不明", "description": "死亡した場所"},
    "followup_status": {"code": "B19", "label_ja": "転帰確認状況", "type_value": "列挙：完了／一部不明／追跡不能", "description": "3つの転帰（入院・搬送・死亡）をどこまで確認できたか"},
    "last_followup_date": {"code": "B20", "label_ja": "最終確認日", "type_value": "日付", "description": "最後に経過を確認できた日"},
    "followup_unknown_reason": {"code": "B21", "label_ja": "追跡不能理由", "type_value": "列挙：他院へ転院／連携記録なし／その他", "description": "追跡できなかった理由"},
    "outcome_evidence_ref": {"code": "B22", "label_ja": "転帰エビデンス参照", "type_value": "文字列（複数）", "description": "転帰を確認した記録の参照キー"},
    "qc_status": {"code": "C01", "label_ja": "QC状態", "type_value": "列挙：未確認／問題なし／要修正／修正確認済", "description": "入力の不備を点検した結果。「問題なし」または「修正確認済」の行だけを集計に使う"},
    "qc_issue": {"code": "C02", "label_ja": "QC指摘", "type_value": "列挙（複数）：空欄あり／日付の矛盾／根拠なし／転記ミス", "description": "不備の種類。医学的な判断の誤りは二次確認で直さず、レビュー担当者に戻す"},
}


def describe(column_name: str) -> str | None:
    """"{code} {type_value}: {description}", or None if the column has no entry
    (e.g. columns outside the 41-column unified CSV)."""
    entry = COLUMN_GLOSSARY.get(column_name)
    if entry is None:
        return None
    return f"{entry['code']} {entry['type_value']}: {entry['description']}"


def dictionary_display_name(column_name: str) -> str:
    """"{label_ja}_{column_name}" (e.g. "患者ID_patient_id"), for the 列名
    column of column_dictionary.csv ONLY -- per project owner request
    2026-11-12, so the Japanese reviewer opening that helper file sees the
    meaning directly next to the real English key. Falls back to the bare
    column_name if there's no glossary entry (should not happen for the 41
    unified-CSV columns)."""
    entry = COLUMN_GLOSSARY.get(column_name)
    if entry is None:
        return column_name
    return f"{entry['label_ja']}_{column_name}"
