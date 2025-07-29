# sici/tests/test_utils.py

from sici.utils import clean_distribution_label, extract_variables_from_label, shorten_expr, bold, color

def test_clean_distribution_label():
    assert clean_distribution_label("P(Y | X, Z)") == "P(Y|X,Z)"
    assert clean_distribution_label(" P( A | B , C ) ") == "P(A|B,C)"

def test_extract_variables_from_label():
    assert extract_variables_from_label("P(Y|X,Z)") == ["Y", "X", "Z"]
    assert extract_variables_from_label("P(X,Z)") == ["X", "Z"]
    assert extract_variables_from_label("P(A)") == ["A"]

def test_shorten_expr():
    long_str = "x" * 100
    assert shorten_expr(long_str, maxlen=10) == "x" * 10 + "..."
    assert shorten_expr("short", maxlen=10) == "short"

def test_bold_and_color():
    text = "hello"
    assert "\033[1mhello\033[0m" == bold(text)
    assert color(text, "red").startswith("\033[91m")

if __name__ == "__main__":
    test_clean_distribution_label()
    test_extract_variables_from_label()
    test_shorten_expr()
    test_bold_and_color()
    print("✅ test_utils passed.")
