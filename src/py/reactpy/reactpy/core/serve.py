from __future__ import annotations

from collections.abc import Awaitable
from logging import getLogger
from typing import Callable
from warnings import warn

from anyio import create_task_group
from anyio.abc import TaskGroup

from reactpy.config import REACTPY_DEBUG_MODE
from reactpy.core.types import LayoutEventMessage, LayoutType, LayoutUpdateMessage

from reactpy.core.id import task_name

logger = getLogger(__name__)


SendCoroutine = Callable[[LayoutUpdateMessage], Awaitable[None]]
"""Send model patches given by a dispatcher"""

RecvCoroutine = Callable[[], Awaitable[LayoutEventMessage]]
"""Called by a dispatcher to return a :class:`reactpy.core.layout.LayoutEventMessage`

The event will then trigger an :class:`reactpy.core.proto.EventHandlerType` in a layout.
"""


class Stop(BaseException):
    """Deprecated

    Stop serving changes and events

    Raising this error will tell dispatchers to gracefully exit. Typically this is
    called by code running inside a layout to tell it to stop rendering.
    """


async def serve_layout(
    layout: LayoutType[LayoutUpdateMessage, LayoutEventMessage],
    send: SendCoroutine,
    recv: RecvCoroutine,
) -> None:
    """Run a dispatch loop for a single view instance"""
    logger.info("%s serve_layouts - run a dispatch loop for a single view instance", f"Task-{layout.count} ")
    async with layout:
        try:
            async with create_task_group() as task_group:
                logger.info("%s Start serving",  task_name())
                task_group.start_soon(_single_outgoing_loop, layout, send, name=f"Task-{layout.count}-outgoing_loop")
                task_group.start_soon(_single_incoming_loop, task_group, layout, recv, name=f"Task-{layout.count}-incoming_loop")
        except Stop:  # nocov
            warn(
                "The Stop exception is deprecated and will be removed in a future version",
                UserWarning,
                stacklevel=1,
            )
            logger.info(f"Stopped serving {layout}")


async def _single_outgoing_loop(
    layout: LayoutType[LayoutUpdateMessage, LayoutEventMessage], send: SendCoroutine
) -> None:
    while True:
        logger.info("%s _single_outgoing_loop - await layout.render",  task_name())
        update = await layout.render()
        try:
            logger.info("%s _single_outgoing_loop - await send(update)",  task_name())
            await send(update)
        except Exception:  # nocov
            if not REACTPY_DEBUG_MODE.current:
                msg = (
                    "Failed to send update. More info may be available "
                    "if you enabling debug mode by setting "
                    "`reactpy.config.REACTPY_DEBUG_MODE.current = True`."
                )
                logger.error(msg)
            raise


async def _single_incoming_loop(
    task_group: TaskGroup,
    layout: LayoutType[LayoutUpdateMessage, LayoutEventMessage],
    recv: RecvCoroutine,
) -> None:
    count = 0
    while True:
        # We need to fire and forget here so that we avoid waiting on the completion
        # of this event handler before receiving and running the next one.
        logger.info("%s _single_incoming_loop create task count=%d", task_name(), count)
        task_group.start_soon(layout.deliver, await recv(), name=f"Task-{layout.count}.{count}-incoming_loop")
        count += 1
