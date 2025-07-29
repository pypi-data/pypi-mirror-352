from asyncio import sleep

from kstd.asyncio import filter_async


async def _is_odd(number: int) -> bool:
    await sleep(0)
    return number % 2 == 1


async def test() -> None:
    values = [1, 2, 3, 4]

    filtered_values = await filter_async(_is_odd, values)

    assert filtered_values == [1, 3]
