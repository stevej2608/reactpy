import asyncio
import sys
import threading
import traceback
import logging

logger = logging.getLogger(__name__)


def task_monitor():
    """Monkey patch asyncio to track task switches"""

    _original_run_once = None
    _original_call_soon = None
    _task_history = {}

    loop = asyncio.get_event_loop()

    # Store original method
    _original_run_once = loop._run_once

    def _monitored_run_once():
        try:
            current_task = asyncio.current_task()
            if current_task:
                frame = sys._getframe(1)
                stack = traceback.extract_stack(frame, limit=3)
                caller = f"{stack[-2].filename}:{stack[-2].lineno}"

                # Log task switch
                last_task = _task_history.get(threading.get_ident())
                current_name = getattr(
                    current_task, "get_name", lambda: str(current_task)
                )()
                if last_task != current_name:
                    logger.info(
                        f"Task switch: {last_task} -> {current_name} "
                        f"at {caller}"
                    )
                    _task_history[threading.get_ident()] = current_name
        except Exception as e:
            logger.error(f"Error in task switch monitoring: {e}")

        # Call original method correctly
        return _original_run_once()

    # Bind the new method to the loop instance
    loop._run_once = _monitored_run_once
    # loop._run_once = _monitored_run_once.__get__(loop)


    # Optionally patch call_soon for more detailed tracking
    _original_call_soon = loop.call_soon

    def _monitored_call_soon(callback, *args, context=None):
        try:
            frame = sys._getframe(1)
            stack = traceback.extract_stack(frame, limit=3)
            caller = f"{stack[-2].filename}:{stack[-2].lineno}"
            logger.info(f"call_soon {caller}")
        except Exception as e:
            logger.error(f"Error in call_soon monitoring: {e}")

        return _original_call_soon(callback, *args, context=context)

    loop.call_soon = _monitored_call_soon
    # loop.call_soon = _monitored_call_soon.__get__(loop)



# Example usage
async def example_task():
    print("Task starting")
    await asyncio.sleep(1)
    print("Task finishing")

async def main():
    # Create and start multiple tasks
    tasks = [
        asyncio.create_task(example_task(), name=f"Task{i}")
        for i in range(3)
    ]
    await asyncio.gather(*tasks)

# python -m src.py.reactpy.tests.test_stj.tooling.task_monitor


if __name__ == "__main__":

    # Setup monitoring
    task_monitor()

    try:
        asyncio.run(main())
    finally:
        logger.info("Exit")




