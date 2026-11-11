from services.dictionaries import load_d2
from services.match_d2 import match_d2
from services.match_qc import match_q40_hints, match_qc1, match_qc2

D2 = load_d2()


def test_match_d2_ceftriaxone():
    hits = match_d2("セフトリアキソンナトリウム注射用1g", D2)
    assert any(h.ingredient_id == "A01" and h.group == "G1" for h in hits)


def test_match_d2_needs_form_check_flagged_not_rejected():
    hits = match_d2("ユナシン静注用", D2)
    assert hits, "ユナシン must still match (flagged for manual confirmation, not auto-rejected)"
    assert any(h.needs_form_check for h in hits)


def test_match_d2_no_hit_for_unrelated_drug():
    assert match_d2("アセトアミノフェン錠", D2) == []


def test_qc1_wide_injection_classes():
    assert match_qc1("31") and match_qc1("32") and match_qc1("33")
    assert not match_qc1("21")  # oral medication class, not injection


def test_qc2_candidate_string():
    assert match_qc2("在宅患者訪問点滴注射管理指導料")
    assert not match_qc2("セフトリアキソンナトリウム注射用1g")


def test_q40_hints():
    assert match_q40_hints("往診料") == ["往診料"]
    assert match_q40_hints("セフトリアキソンナトリウム注射用1g") == []
