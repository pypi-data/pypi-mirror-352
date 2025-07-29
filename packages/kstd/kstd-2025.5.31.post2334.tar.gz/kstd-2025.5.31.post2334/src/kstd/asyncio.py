"""
A collection of `asyncio`-related utilities that make working with coroutines more ergonomic.

This module provides helper functions for common asyncio patterns, with a focus on type safety
and proper handling of concurrent execution.
"""

import asyncio as stdlib_asyncio
from collections.abc import Callable, Coroutine, Iterable, Mapping, Sequence
from typing import overload

type SimpleCoroutine[T] = Coroutine[None, None, T]
"""A coroutine that doesn't yield anything"""


async def awaitable_value[T](value: T) -> T:  # noqa: RUF029
    """
    A helper function that wraps a value in an awaitable.

    Useful when you need to maintain consistent awaitable interfaces.

    Examples:
        When you need to conditionally process values in `gather(...)`:

            ```python
            res_a, res_b, res_c = await gather(
                process(a),
                process(b),
                process(c) if c is not None else awaitable_value(DEFAULT_VALUE),
            )
            ```

    Warning:
        Using this function adds event loop overhead. It should be used sparingly and only
        when necessary to maintain consistent async interfaces.

    Args:
        value: The value to be wrapped in an awaitable.

    Returns:
        The provided value.
    """
    return value


@overload
async def gather[T1](
    c1: SimpleCoroutine[T1],
    /,
) -> tuple[T1]: ...
@overload
async def gather[T1, T2](
    c1: SimpleCoroutine[T1],
    c2: SimpleCoroutine[T2],
    /,
) -> tuple[T1, T2]: ...
@overload
async def gather[T1, T2, T3](
    c1: SimpleCoroutine[T1],
    c2: SimpleCoroutine[T2],
    c3: SimpleCoroutine[T3],
    /,
) -> tuple[T1, T2, T3]: ...
@overload
async def gather[T1, T2, T3, T4](
    c1: SimpleCoroutine[T1],
    c2: SimpleCoroutine[T2],
    c3: SimpleCoroutine[T3],
    c4: SimpleCoroutine[T4],
    /,
) -> tuple[T1, T2, T3, T4]: ...
@overload
async def gather[T1, T2, T3, T4, T5](
    c1: SimpleCoroutine[T1],
    c2: SimpleCoroutine[T2],
    c3: SimpleCoroutine[T3],
    c4: SimpleCoroutine[T4],
    c5: SimpleCoroutine[T5],
    /,
) -> tuple[T1, T2, T3, T4, T5]: ...
@overload
async def gather[T1, T2, T3, T4, T5, T6](
    c1: SimpleCoroutine[T1],
    c2: SimpleCoroutine[T2],
    c3: SimpleCoroutine[T3],
    c4: SimpleCoroutine[T4],
    c5: SimpleCoroutine[T5],
    c6: SimpleCoroutine[T6],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6]: ...
@overload
async def gather[T1, T2, T3, T4, T5, T6, T7](
    c1: SimpleCoroutine[T1],
    c2: SimpleCoroutine[T2],
    c3: SimpleCoroutine[T3],
    c4: SimpleCoroutine[T4],
    c5: SimpleCoroutine[T5],
    c6: SimpleCoroutine[T6],
    c7: SimpleCoroutine[T7],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7]: ...
@overload
async def gather[T1, T2, T3, T4, T5, T6, T7, T8](
    c1: SimpleCoroutine[T1],
    c2: SimpleCoroutine[T2],
    c3: SimpleCoroutine[T3],
    c4: SimpleCoroutine[T4],
    c5: SimpleCoroutine[T5],
    c6: SimpleCoroutine[T6],
    c7: SimpleCoroutine[T7],
    c8: SimpleCoroutine[T8],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8]: ...
@overload
async def gather[T1, T2, T3, T4, T5, T6, T7, T8, T9](
    c1: SimpleCoroutine[T1],
    c2: SimpleCoroutine[T2],
    c3: SimpleCoroutine[T3],
    c4: SimpleCoroutine[T4],
    c5: SimpleCoroutine[T5],
    c6: SimpleCoroutine[T6],
    c7: SimpleCoroutine[T7],
    c8: SimpleCoroutine[T8],
    c9: SimpleCoroutine[T9],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9]: ...
@overload
async def gather[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10](
    c1: SimpleCoroutine[T1],
    c2: SimpleCoroutine[T2],
    c3: SimpleCoroutine[T3],
    c4: SimpleCoroutine[T4],
    c5: SimpleCoroutine[T5],
    c6: SimpleCoroutine[T6],
    c7: SimpleCoroutine[T7],
    c8: SimpleCoroutine[T8],
    c9: SimpleCoroutine[T9],
    c10: SimpleCoroutine[T10],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]: ...
@overload
async def gather[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11](
    c1: SimpleCoroutine[T1],
    c2: SimpleCoroutine[T2],
    c3: SimpleCoroutine[T3],
    c4: SimpleCoroutine[T4],
    c5: SimpleCoroutine[T5],
    c6: SimpleCoroutine[T6],
    c7: SimpleCoroutine[T7],
    c8: SimpleCoroutine[T8],
    c9: SimpleCoroutine[T9],
    c10: SimpleCoroutine[T10],
    c11: SimpleCoroutine[T11],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11]: ...
@overload
async def gather[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12](
    c1: SimpleCoroutine[T1],
    c2: SimpleCoroutine[T2],
    c3: SimpleCoroutine[T3],
    c4: SimpleCoroutine[T4],
    c5: SimpleCoroutine[T5],
    c6: SimpleCoroutine[T6],
    c7: SimpleCoroutine[T7],
    c8: SimpleCoroutine[T8],
    c9: SimpleCoroutine[T9],
    c10: SimpleCoroutine[T10],
    c11: SimpleCoroutine[T11],
    c12: SimpleCoroutine[T12],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12]: ...
@overload
async def gather[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13](
    c1: SimpleCoroutine[T1],
    c2: SimpleCoroutine[T2],
    c3: SimpleCoroutine[T3],
    c4: SimpleCoroutine[T4],
    c5: SimpleCoroutine[T5],
    c6: SimpleCoroutine[T6],
    c7: SimpleCoroutine[T7],
    c8: SimpleCoroutine[T8],
    c9: SimpleCoroutine[T9],
    c10: SimpleCoroutine[T10],
    c11: SimpleCoroutine[T11],
    c12: SimpleCoroutine[T12],
    c13: SimpleCoroutine[T13],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13]: ...
@overload
async def gather[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14](
    c1: SimpleCoroutine[T1],
    c2: SimpleCoroutine[T2],
    c3: SimpleCoroutine[T3],
    c4: SimpleCoroutine[T4],
    c5: SimpleCoroutine[T5],
    c6: SimpleCoroutine[T6],
    c7: SimpleCoroutine[T7],
    c8: SimpleCoroutine[T8],
    c9: SimpleCoroutine[T9],
    c10: SimpleCoroutine[T10],
    c11: SimpleCoroutine[T11],
    c12: SimpleCoroutine[T12],
    c13: SimpleCoroutine[T13],
    c14: SimpleCoroutine[T14],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14]: ...
@overload
async def gather[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15](
    c1: SimpleCoroutine[T1],
    c2: SimpleCoroutine[T2],
    c3: SimpleCoroutine[T3],
    c4: SimpleCoroutine[T4],
    c5: SimpleCoroutine[T5],
    c6: SimpleCoroutine[T6],
    c7: SimpleCoroutine[T7],
    c8: SimpleCoroutine[T8],
    c9: SimpleCoroutine[T9],
    c10: SimpleCoroutine[T10],
    c11: SimpleCoroutine[T11],
    c12: SimpleCoroutine[T12],
    c13: SimpleCoroutine[T13],
    c14: SimpleCoroutine[T14],
    c15: SimpleCoroutine[T15],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15]: ...
async def gather(*coroutines: SimpleCoroutine[object]) -> tuple[object, ...]:
    """
    Like asyncio.gather, but awaits all coroutines even if some of them raise an exception.

    This is important, as an exception will otherwise bubble up the call stack, potentially
    deleting things that the other coroutines need, leading to weird and hard to debug errors. An
    example of this behavior is when gathering two DB queries, where the first query fails, the
    exception bubbles up and rolls back the transaction, while the second query is still trying to
    fetch some extra data.

    Args:
        *coroutines: A variable number of coroutines to be executed concurrently.

    Returns:
        A tuple containing the results of all coroutines in the same order they were passed in.

    Raises:
        If any of the coroutines raise an exception, the first exception that occurred is re-raised.
            In that case, other coroutines are cancelled. Even if more than coroutine managed to
            raise an exception, only one of them is re-raised.
    """
    try:
        async with stdlib_asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(coroutine) for coroutine in coroutines]
    except ExceptionGroup as exc_group:
        raise exc_group.exceptions[0] from exc_group.exceptions[0]
    return tuple(t.result() for t in tasks)


async def gather_iterable[T](
    coroutines: Iterable[SimpleCoroutine[T]],
) -> Sequence[T]:
    """
    Concurrently executes and gathers results from multiple coroutines of the same type.

    This function is similar to `asyncio.gather()` but specifically handles an iterable of
    coroutines that return the same type. It uses `TaskGroup` for structured concurrency and
    proper error handling.

    Args:
        coroutines: An iterable of coroutines.

    Returns:
        A sequence containing the results of all coroutines in the order they were
        submitted.

    Raises:
        If any of the coroutines raise an exception, the first exception that occurred is re-raised.
            In that case, other coroutines are cancelled. Even if more than coroutine managed to
            raise an exception, only one of them is re-raised.

    Example:
        >>> async def fetch(url: str) -> str:
        ...     async with aiohttp.ClientSession() as session:
        ...         async with session.get(url) as response:
        ...             return await response.text()
        ...
        >>> urls = ['http://example.com', 'http://example.org']
        >>> results = await gather_iterable(fetch(url) for url in urls)
    """
    try:
        async with stdlib_asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(coroutine) for coroutine in coroutines]
    except ExceptionGroup as exc_group:
        raise exc_group.exceptions[0] from exc_group.exceptions[0]

    return [t.result() for t in tasks]


async def gather_mapping[K, V](
    coroutines: Mapping[K, SimpleCoroutine[V]],
) -> Mapping[K, V]:
    """
    Concurrently awaits all coroutines in the input mapping and returns a new mapping with the same keys and their corresponding awaited values.

    Args:
        coroutines: A mapping where values are coroutines to be awaited.

    Returns:
        A mapping with the same keys as the input, but with awaited values.

    Raises:
        If any of the coroutines raise an exception, the first exception that occurred is re-raised.
            In that case, other coroutines are cancelled. Even if more than coroutine managed to
            raise an exception, only one of them is re-raised.

    Example:
        ```python
        async def example():
            tasks = {
                'a': some_coroutine(),
                'b': another_coroutine()
            }
            results = await gather_mapping(tasks)
            # results will be like {'a': value1, 'b': value2}
        ```
    """
    values = await gather_iterable(coroutines.values())

    return dict(zip(coroutines.keys(), values, strict=True))


async def filter_async[T](
    filter_func: Callable[[T], SimpleCoroutine[bool]],
    iterable: Iterable[T],
) -> Sequence[T]:
    """
    Asynchronously filters elements from an iterable based on an async predicate function.

    This function applies the async `filter_func` to all elements concurrently and returns
    a sequence containing only the elements for which `filter_func` returns `True`.

    Args:
        filter_func: An async function that takes an item and returns a coroutine that resolves
            to a boolean value.
        iterable: The input iterable containing items to filter.

    Returns:
        A sequence containing only the items for which `filter_func` returned `True`.

    Raises:
        If any of the `filter_func` raise an exception, the first exception that occurred is re-raised.
            In that case, other coroutines are cancelled. Even if more than coroutine managed to
            raise an exception, only one of them is re-raised.

    Example:
        ```python
        async def is_even(x: int) -> bool:
            await asyncio.sleep(0.1)  # Simulate async work
            return x % 2 == 0

        numbers = [1, 2, 3, 4, 5]
        even_numbers = await filter_async(is_even, numbers)
        # Result: [2, 4]
        ```
    """
    filter_results = await gather_iterable(filter_func(item) for item in iterable)

    return [
        value
        for value, filter_result in zip(iterable, filter_results, strict=True)
        if filter_result is True
    ]


async def unblock_event_loop() -> None:
    """
    Yields control back to the event loop, giving other in-progress tasks a chance to progress.

    Use it to split up a block of long-running, CPU-bound code in a coroutine function. Asyncio
    follows a cooperative, rather than preemptive, approach to scheduling - so each task should
    periodically yield control back to the event loop.
    """
    await stdlib_asyncio.sleep(0)


async def run_async[**P, T](
    sync_func: Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    """
    Executes a sync function in the default executor of the currently running event loop, preventing it from blocking the said event loop.

    Can be used for non-async IO-bound functions, as well as long-running CPU-bound ones.

    Always wrap in it any function which performs an IO operation (HTTP request, DB query, etc.)
    and isn't async - i.e. doesn't use an `asyncio`-based library for IO. It will enable
    concurrently executing multiple calls to it using helpers like `gather` or `gather_iterable`.

    In a webserver, it is important to wrap *all* non-async IO-bound functions in `run_async`, even
    if you don't intend to invoke them concurrently. This is because a long-running sync operation
    will block *other* in-progress work from progressing (e.g. concurrently served requests).

    `run_async` can be also used to wrap long-running CPU-bound functions. It won't allow parallel
    processing due to Python's global interpret lock, but it will interleave the work - allowing
    other shorter-running and IO-bound work to progress and complete sooner. As a rule of thumb,
    consider any function that takes more than 10 ms to complete to be long-running.

    Args:
        sync_func: A synchronous function to be executed asynchronously.
        *args: Positional arguments to pass to the synchronous function.
        **kwargs: Keyword arguments to pass to the synchronous function.

    Returns:
        The result of the synchronous function execution.
    """

    def parametrized_func() -> T:
        return sync_func(*args, **kwargs)

    # Get the current event loop. We can safely assume that there is one, because we're in an
    # async function.
    loop = stdlib_asyncio.get_running_loop()

    return await loop.run_in_executor(
        # Run this function in the default loop executor (by passing `None`), as it's the simplest
        # and most portable solution.
        #
        # See https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor
        None,
        parametrized_func,
    )
