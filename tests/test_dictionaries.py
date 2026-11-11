from services.dictionaries import load_d1, load_d2, load_d3, load_d4


def test_d1_counts():
    d1 = load_d1()
    assert len(d1.modifiers) == 8
    assert len(d1.categories) == 18
    assert [c.order for c in d1.categories] == list(range(1, 19))
    assert d1.categories[0].code == "Q"
    assert d1.categories[-1].code == "Z"


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
