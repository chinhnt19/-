from services.dictionaries import load_d2
from services.match_d2 import match_d2
from rules.q_conditions import ELIGIBLE_INJECTION_MEDICAL_CLASSES

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


def test_v1_route_eligible_injection_classes():
    # D4 P04-P09: medical_class 32 (静注) and 33 (点滴静注) are candidate-eligible.
    assert ELIGIBLE_INJECTION_MEDICAL_CLASSES == {"32": "静注", "33": "点滴静注"}
    # medical_class 31 (皮下筋肉内注射, D4 P01-P03) is explicitly excluded.
    assert "31" not in ELIGIBLE_INJECTION_MEDICAL_CLASSES
    assert "21" not in ELIGIBLE_INJECTION_MEDICAL_CLASSES  # oral medication class
