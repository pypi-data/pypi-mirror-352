from typing import assert_type

import pytest

from kstd.either import Either, Left, Right


def _get_int_or_string__1() -> Either[int, str]:
    return Left(1)


def _get_int_or_string__foo() -> Either[int, str]:
    return Right("foo")


def test_is__left() -> None:
    val = _get_int_or_string__1()

    assert val.is_left() is True
    assert val.is_right() is False


def test_is__right() -> None:
    val = _get_int_or_string__foo()

    assert val.is_left() is False
    assert val.is_right() is True


def test_match__left() -> None:
    val = _get_int_or_string__1()

    match val:
        case Left():
            res = val.value + 1
        case Right():
            res = val.value.upper()

    _ = assert_type(res, int | str)

    assert res == 2


def test_match__right() -> None:
    val = _get_int_or_string__foo()

    match val:
        case Left():
            res = val.value + 1
        case Right():
            res = val.value.upper()

    _ = assert_type(res, int | str)

    assert res == "FOO"


def test_map__left() -> None:
    val = _get_int_or_string__1()

    res = val.map(
        lambda left: left + 1,
        lambda right: right.upper(),
    )

    _ = assert_type(res, int | str)

    assert res == 2


def test_map__right() -> None:
    val = _get_int_or_string__foo()

    res = val.map(
        lambda left: left + 1,
        lambda right: right.upper(),
    )

    _ = assert_type(res, int | str)

    assert res == "FOO"


def test_map__wrong_type__left() -> None:
    """
    This test checks the scenario where we provide an incorrect mapper for the left value, and the value does happen to be left at runtime.

    We should get both a static type checker error and runtime error.
    """
    val = _get_int_or_string__1()

    with pytest.raises(AttributeError):
        _ = val.map(  # pyright: ignore[reportUnknownVariableType]
            lambda left: left.upper(),  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
            lambda right: right.upper(),
        )


def test_map__wrong_type__right() -> None:
    """
    This test checks the scenario where we provide an incorrect mapper for the right value, and the value does happen to be right at runtime.

    We should get both a static type checker error and runtime error.
    """
    val = _get_int_or_string__foo()

    with pytest.raises(TypeError):
        _ = val.map(  # pyright: ignore[reportUnknownVariableType]
            lambda left: left + 1,
            lambda right: right + 1,  # pyright: ignore[reportOperatorIssue,reportUnknownLambdaType]
        )
