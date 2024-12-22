import asyncio
import logging
import sys
import threading
import traceback
from functools import wraps
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger("asyncio_debug")


class TaskSwitchMonitor:
    def __init__(self):
        self._original_run_once = None
        self._original_call_soon = None
        self._task_history = {}

    def start_monitoring(self):
        """Monkey patch asyncio to track task switches"""
        loop = asyncio.get_event_loop()

        # Store original method
        self._original_run_once = loop._run_once

        def _monitored_run_once():
            try:
                current_task = asyncio.current_task()
                if current_task:
                    frame = sys._getframe(1)
                    stack = traceback.extract_stack(frame, limit=3)
                    caller = f"{stack[-2].filename}:{stack[-2].lineno}"

                    # Log task switch
                    last_task = self._task_history.get(threading.get_ident())
                    current_name = getattr(
                        current_task, "get_name", lambda: str(current_task)
                    )()
                    if last_task != current_name:
                        logger.debug(
                            f"Task switch: {last_task} -> {current_name} "
                            f"at {caller}"
                        )
                        self._task_history[threading.get_ident()] = current_name
            except Exception as e:
                logger.error(f"Error in task switch monitoring: {e}")

            # Call original method correctly
            return self._original_run_once()

        # Bind the new method to the loop instance
        loop._run_once = _monitored_run_once

        # Optionally patch call_soon for more detailed tracking
        self._original_call_soon = loop.call_soon

        def _monitored_call_soon(callback, *args, context=None):
            try:
                frame = sys._getframe(1)
                stack = traceback.extract_stack(frame, limit=3)
                caller = f"{stack[-2].filename}:{stack[-2].lineno}"

                logger.debug(f"Scheduling callback from {caller}")
            except Exception as e:
                logger.error(f"Error in call_soon monitoring: {e}")

            return self._original_call_soon(callback, *args, context=context)

        loop.call_soon = _monitored_call_soon

    def stop_monitoring(self):
        """Restore original asyncio behavior"""
        try:
            loop = asyncio.get_event_loop()
            if self._original_run_once:
                loop._run_once = self._original_run_once

            if self._original_call_soon:
                loop.call_soon = self._original_call_soon
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")


# Example usage
async def example_task(name):
    logger.info("Task starting %s", name)
    await asyncio.sleep(1)
    logger.info("Task finishing %s", name)


async def main():
    # Create and start multiple tasks
    tasks = [asyncio.create_task(example_task(f"Task{i}"), name=f"Task{i}") for i in range(3)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # Setup monitoring
    monitor = TaskSwitchMonitor()
    monitor.start_monitoring()

    try:
        asyncio.run(main())
    finally:
        monitor.stop_monitoring()
