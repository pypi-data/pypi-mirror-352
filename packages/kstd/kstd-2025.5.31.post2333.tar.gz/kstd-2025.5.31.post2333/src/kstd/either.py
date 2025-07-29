"""
Implementation of the `Either` type for handling computation results with two possible types.

The `Either` type represents a value that can be one of two types: `Left` or `Right`.
Typically used for computations that can either succeed (`Right`) or fail (`Left`).
"""

from collections.abc import Callable
from typing import Any, NoReturn, Protocol, override


class _IEither(Protocol):
    def is_left(self) -> bool:
        """
        Check if this is a `Left` value.

        Returns:
            `True` if this is a `Left` value, `False` if this is a `Right` value.
        """
        ...

    def is_right(self) -> bool:
        """
        Check if this is a `Right` value.

        Returns:
            `True` if this is a `Right` value, `False` if this is a `Left` value.
        """
        ...

    def get_left_or_raise(self) -> object:
        """
        Get the contained value if this is a `Left` value.

        Returns:
            The contained value if this is a `Left` value.

        Raises:
            ValueError: If this is a `Right` value.
        """
        ...

    def get_right_or_raise(self) -> object:
        """
        Get the contained value if this is a `Right` value.

        Returns:
            The contained value if this is a `Right` value.

        Raises:
            ValueError: If this is a `Left` value.
        """
        ...

    def map(
        self,
        left: Callable[[Any], Any],
        right: Callable[[Any], Any],
    ) -> object:
        """
        Transform the contained value using the appropriate function.

        Args:
            left: Function to transform the value if this is `Left`.
            right: Function to transform the value if this is `Right`.

        Returns:
            Result of applying the appropriate function to the contained value.
        """
        ...


class Left[TLeft](_IEither):
    """
    The left variant of an `Either` type.

    Typically represents the failure case in an `Either` computation.
    """

    def __init__(self, value: TLeft) -> None:
        """
        Initialize a `Left` value.

        Args:
            value: The value to store.
        """
        super().__init__()
        self.value = value

    @override
    def is_left(self) -> bool:
        return True

    @override
    def is_right(self) -> bool:
        return False

    @override
    def get_left_or_raise(self) -> TLeft:
        return self.value

    @override
    def get_right_or_raise(self) -> NoReturn:
        raise ValueError("Value is left")

    @override
    def map[TReturnLeft](
        self,
        left: Callable[[TLeft], TReturnLeft],
        right: Callable[[Any], Any],
    ) -> TReturnLeft:
        return left(self.value)


class Right[TRight](_IEither):
    """
    The right variant of an `Either` type.

    Typically represents the success case in an `Either` computation.
    """

    def __init__(self, value: TRight) -> None:
        """
        Initialize a `Right` value.

        Args:
            value: The value to store.
        """
        super().__init__()
        self.value = value

    @override
    def is_left(self) -> bool:
        return False

    @override
    def is_right(self) -> bool:
        return True

    @override
    def get_left_or_raise(self) -> NoReturn:
        raise ValueError("Value is right")

    @override
    def get_right_or_raise(self) -> TRight:
        return self.value

    @override
    def map[TReturnRight](
        self,
        left: Callable[[Any], Any],
        right: Callable[[TRight], TReturnRight],
    ) -> TReturnRight:
        return right(self.value)


type Either[TLeft, TRight] = Left[TLeft] | Right[TRight]
"""
Implementation of the `Either` type for handling computation results with two possible types.

The `Either` type represents a value that can be one of two types: `Left` or `Right`.
Typically used for computations that can either succeed (`Right`) or fail (`Left`).
"""
