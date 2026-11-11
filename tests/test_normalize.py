from services.normalize import nfkc


def test_fullwidth_alnum_to_halfwidth():
    assert nfkc("Ｎａ１２３") == "Na123"


def test_none_passthrough():
    assert nfkc(None) is None


def test_kana_kanji_unchanged():
    assert nfkc("誤嚥性肺炎") == "誤嚥性肺炎"
