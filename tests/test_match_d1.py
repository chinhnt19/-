import pytest

from services.dictionaries import load_d1
from services.match_d1 import classify_d1

D1 = load_d1()


@pytest.mark.parametrize("name,expected_category,expected_state", [
    ("誤嚥性肺炎", "PS", "A"),
    ("誤嚥性肺炎の疑い", "PS", "S"),
    ("誤嚥性肺炎の既往", "PS", "H"),
    ("誤嚥性肺炎の予防", "PS", "X"),
    ("肺炎球菌性肺炎", "PB", "A"),
    ("大葉性肺炎", "PG", "A"),  # "肺炎" present, no organism name, no other earlier category -> PG
    ("間質性肺炎", "N", "A"),  # N (order 5) must win over PG (order 11)
    ("肺癌", "K", "A"),
    ("肺結核", "T", "A"),
    ("COVID-19肺炎", "PV", "A"),
    ("ウイルス性肺炎", "PV", "A"),
    # PV's "インフルエンザ(除く「インフルエンザ菌」)" branch has no AND-肺炎
    # requirement in the source text (it is its own OR term, distinct from
    # the "ウイルス性"+"肺炎" AND branch) -- so any インフルエンザ mention
    # resolves to PV (order 6), before VI (order 15) is ever reached.
    ("インフルエンザ感染症", "PV", "A"),
    ("インフルエンザ菌感染症", "VI", "Z"),  # placeholder, overridden by dedicated test below
    ("マイコプラズマ肺炎", "PA", "A"),
    ("肺膿瘍", "PL", "A"),
    ("急性気管支炎", "LB", "A"),
    ("細菌感染症", "BI", "A"),
    ("急性上気道炎", "UR", "A"),
    ("ウイルス感染症", "VI", "A"),
    ("サイトメガロウイルス感染症", "VI", "A"),
    ("尿路感染症", "O", "A"),
    ("原発性胆汁性胆管炎", "Z", "A"),  # literally one of O's own exclusion terms -> must NOT be O
    ("胸膜炎", "Q", "A"),
    ("謎の病気", "Z", "A"),
])
def test_classify_d1(name, expected_category, expected_state):
    if name == "インフルエンザ菌感染症":
        pytest.skip("covered separately below")
    result = classify_d1(name, D1)
    assert result.category == expected_category, f"{name} -> expected {expected_category}, got {result.category}"
    assert result.state == expected_state


def test_influenza_bacterium_does_not_trigger_influenza_branch():
    # "インフルエンザ菌" must not satisfy PV/VI's インフルエンザ(exclude 菌) branch.
    # It isn't a 肺炎 (no PB/PG), has no organism match besides the excluded
    # one, and isn't one of BI's/O's exact terms either -> falls to Z.
    result = classify_d1("インフルエンザ菌感染症", D1)
    assert result.category not in ("PV", "VI")
    assert result.category == "Z"


def test_modifier_priority_prevention_wins():
    result = classify_d1("肺炎の予防", D1)
    assert result.state == "X"


def test_order_enforced_pneumonia_abscess_before_other_pneumonia():
    result = classify_d1("肺膿瘍", D1)
    assert result.category == "PL"  # order 8, before PG (order 11)


def test_o_exclusion_term_blocks_match():
    # "原発性胆汁性胆管炎" contains O's own positive term "胆管炎" but is
    # explicitly listed as an EXCLUSION_TERM for O -- must not be classified O.
    result = classify_d1("原発性胆汁性胆管炎", D1)
    assert result.category != "O"
