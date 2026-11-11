from services.dictionaries import load_d1, load_d2, load_d3, load_d4, load_d6


def test_d1_counts():
    d1 = load_d1()
    assert len(d1.modifiers) == 8
    assert len(d1.categories) == 18
    assert [c.order for c in d1.categories] == list(range(1, 19))
    assert d1.categories[0].code == "Q"
    assert d1.categories[-1].code == "Z"
    assert d1.version == "v1.3.1"  # highest row version wins (category rows bumped)


def test_d1_category_status_column_blanked_in_v1_3_1():
    # v1.3.1 removed the per-category 確定/暫定/未決定 status column entirely
    # (検索ツール辞書v1.3.1.xlsx D1_区分) -- D1Category never exposed `status`
    # as a field anyway, so check the raw CSV directly: every CATEGORY row's
    # `status` cell must now be blank (MODIFIER rows are unaffected).
    import csv
    from services.dictionaries import DICT_DIR
    with open(DICT_DIR / "D1_disease.csv", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    category_rows = [r for r in rows if r["row_type"] == "CATEGORY"]
    assert len(category_rows) == 18
    assert all(r["status"] == "" for r in category_rows)
    modifier_rows = [r for r in rows if r["row_type"] == "MODIFIER"]
    assert all(r["status"] != "" for r in modifier_rows)


def test_d2_counts():
    d2 = load_d2()
    assert len(d2.search_terms) == 89
    confirmed = [t for t in d2.search_terms if t.confirmed_status == "A"]
    unconfirmed = [t for t in d2.search_terms if t.confirmed_status == "U"]
    assert len(confirmed) == 78
    assert len(unconfirmed) == 11


def test_d3_matrix_cells():
    d3 = load_d3()
    assert len(d3.matrix) == 56  # 8 D1 row-keys x 7 D2 groups
    assert d3.matrix[("PS・PB・PG", "G1")] == "A"
    assert d3.matrix[("呼吸器感染症の病名なし", "G6")] == "X"


def test_d4_loads():
    d4 = load_d4()
    assert len(d4.entries) > 0


def test_d4_injection_eligibility_v1_3_1():
    d4 = load_d4()
    injections = {e.id: e for e in d4.injection_types()}
    assert len(injections) == 11  # P01-P11
    assert injections["P01"].candidate_eligible_v1_3_1 == "いいえ"  # 皮下筋肉内注射
    assert injections["P04"].candidate_eligible_v1_3_1 == "はい"
    assert injections["P04"].route_class_a13_v1_3_1 == "静注"
    assert injections["P06"].route_class_a13_v1_3_1 == "点滴静注"
    assert injections["P08"].candidate_eligible_v1_3_1 == "いいえ"  # 入院中の手術日算定


def test_d6_case_status_reasons_draft():
    d6 = load_d6()
    assert d6.version == "v1.3.1-draft"
    hold_reasons = d6.reasons_for("保留")
    excluded_reasons = d6.reasons_for("対象外")
    assert len(hold_reasons) == 3
    assert len(excluded_reasons) == 5
    assert all(r.excluded_from_outcome_denominator for r in hold_reasons)
    assert all(not r.excluded_from_outcome_denominator for r in excluded_reasons)
