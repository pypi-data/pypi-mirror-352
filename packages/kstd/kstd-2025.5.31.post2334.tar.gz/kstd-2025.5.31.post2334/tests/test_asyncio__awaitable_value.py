from kstd.asyncio import awaitable_value


async def test_none() -> None:
    assert (await awaitable_value(None)) is None


async def test_some_value() -> None:
    assert (await awaitable_value(42)) == 42
