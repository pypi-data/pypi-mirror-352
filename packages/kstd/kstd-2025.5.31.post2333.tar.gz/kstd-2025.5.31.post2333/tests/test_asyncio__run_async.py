from kstd.asyncio import gather, run_async


def raise_to_power(base: int, exponent: int = 2) -> int:
    return base**exponent


async def test_run_async() -> None:
    provided_input = 3
    expected_result = 9

    # test the sync function directly
    sync_result = raise_to_power(provided_input)
    assert sync_result == expected_result

    # test the async function
    async_result = await run_async(raise_to_power, provided_input)
    assert async_result == expected_result


async def test_gathered() -> None:
    coroutine_1 = run_async(raise_to_power, 3)
    coroutine_2 = run_async(raise_to_power, 4)

    async_result_1, async_result_2 = await gather(
        coroutine_1,
        coroutine_2,
    )

    assert async_result_1 == 9
    assert async_result_2 == 16


async def test_argument_order() -> None:
    positional_normal_order = await run_async(
        raise_to_power,
        2,
        1,
    )

    keyword_normal_order = await run_async(
        raise_to_power,
        base=2,
        exponent=1,
    )

    keyword_flipped_order = await run_async(
        raise_to_power,
        exponent=1,
        base=2,
    )

    assert positional_normal_order == 2
    assert keyword_normal_order == positional_normal_order
    assert keyword_flipped_order == positional_normal_order

    positional_flipped_order = await run_async(
        raise_to_power,
        1,
        2,
    )

    assert positional_flipped_order == 1
