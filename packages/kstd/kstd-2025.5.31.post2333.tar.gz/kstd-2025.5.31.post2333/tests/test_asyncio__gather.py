from asyncio import CancelledError, sleep

import pytest

from kstd.asyncio import gather, gather_iterable


class CoroutineGenerator:
    def __init__(self) -> None:
        super().__init__()
        self.finished = list[str]()
        self.cancelled = list[str]()

    async def succeeds(self, label: str, wait_ms: int) -> str:
        try:
            await sleep(wait_ms / 1000)
        except CancelledError:
            self.cancelled.append(label)
            raise

        self.finished.append(label)
        return label

    async def fails(self, label: str, wait_ms: int) -> str:
        try:
            await sleep(wait_ms / 1000)
        except CancelledError:
            self.cancelled.append(label)
            raise

        self.finished.append(label)
        raise RuntimeError(f"{label} failed")


async def test_gather_returns_tuple_of_results_when_all_are_successful() -> None:
    generator = CoroutineGenerator()

    results = await gather(
        generator.succeeds("first", 10),
        generator.succeeds("second", 20),
    )
    assert results == ("first", "second")

    assert generator.finished == ["first", "second"]
    assert generator.cancelled == []


async def test_gather_raises_first_exception__one_exception() -> None:
    generator = CoroutineGenerator()

    with pytest.raises(RuntimeError, match="second failed"):
        _ = await gather(
            generator.succeeds("first", 10),
            generator.fails("second", 20),
            generator.fails("third", 30),
        )

    assert generator.finished == ["first", "second"]
    assert generator.cancelled == ["third"]


async def test_gather_raises_first_exception__two_exceptions() -> None:
    generator = CoroutineGenerator()

    with pytest.raises(RuntimeError) as exc_info:
        _ = await gather(
            generator.fails("first", 10),
            generator.fails("second", 10),
        )

    assert str(exc_info.value) in {"first failed", "second failed"}

    assert generator.finished == ["first", "second"]


async def test_gather_iterable_returns_list_of_results_when_all_are_successful() -> None:
    generator = CoroutineGenerator()

    results = await gather_iterable([
        generator.succeeds("first", 10),
        generator.succeeds("second", 20),
    ])
    assert results == ["first", "second"]

    assert generator.finished == ["first", "second"]
    assert generator.cancelled == []


async def test_gather_iterable_raises_first_exception() -> None:
    generator = CoroutineGenerator()

    with pytest.raises(RuntimeError, match="second failed"):
        _ = await gather_iterable([
            generator.succeeds("first", 10),
            generator.fails("second", 20),
            generator.fails("third", 30),
        ])

    assert generator.finished == ["first", "second"]
    assert generator.cancelled == ["third"]
