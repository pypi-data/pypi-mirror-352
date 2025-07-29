import pytest

from kstd import strings


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("a", "a"),
        ("\n", " "),
        ("\n\n", "  "),
        (" a ", " a "),
        ("a" * 50, "a" * 50),
        ("a" * 51, "a" * 47 + "..."),
    ],
)
def test_head(
    value: str,
    expected: str,
) -> None:
    assert strings.head(value) == expected
