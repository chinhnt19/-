from services.dictionaries import load_d3
from services.judge_d3 import judge_patient

D3 = load_d3()


def test_main8_direct_hit():
    r = judge_patient([("PS", "A")], ["G1"], D3)
    assert r.judgment_code == "A"
    assert not r.competing_diagnosis_flag


def test_state_s_downgrades_one_step():
    r = judge_patient([("PS", "S")], ["G1"], D3)
    assert r.judgment_code == "B"  # A -> B


def test_highest_priority_wins_across_combinations():
    # PS+G1 -> A ; PA+G2a -> B ; best must be A (APPLY-2)
    r = judge_patient([("PS", "A"), ("PA", "A")], ["G1", "G2a"], D3)
    assert r.judgment_code == "A"


def test_urvibi_only_synthetic_row():
    r = judge_patient([("UR", "A")], ["G1"], D3)
    assert r.judgment_code == "C"


def test_urvibi_only_all_state_s_downgrades():
    # synthetic-row downgrade interpretation: all contributing hits state S
    r = judge_patient([("UR", "S")], ["G1"], D3)
    assert r.judgment_code == "C"  # C downgrades to C (floor)


def test_no_respiratory_category_is_always_x():
    r = judge_patient([], ["G1"], D3)
    assert r.judgment_code == "X"
    r2 = judge_patient([("K", "A")], ["G6"], D3)  # K (malignancy) isn't main8 or UR/VI/BI
    assert r2.judgment_code == "X"


def test_competing_diagnosis_flag_does_not_change_code():
    r_with_o = judge_patient([("PS", "A"), ("O", "A")], ["G1"], D3)
    r_without_o = judge_patient([("PS", "A")], ["G1"], D3)
    assert r_with_o.judgment_code == r_without_o.judgment_code == "A"
    assert r_with_o.competing_diagnosis_flag
    assert not r_without_o.competing_diagnosis_flag
