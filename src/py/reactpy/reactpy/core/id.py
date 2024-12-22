from __future__ import annotations

from asyncio import current_task

from exceptiongroup import catch


def ID() -> int:
    """An immutable counter. Returns  0, 1, 2 ... on each successive call

    Returns:
        int: count 0, 1, 2 ...
    """

    if not hasattr(ID, "counter"):
        setattr(ID, "counter", 0)

    ID.counter += 1  # type: ignore
    return ID.counter  # type: ignore


def task_name():
    try:
        return current_task().get_name()
    except Exception:
        return f"Unknown-{ID()}"
