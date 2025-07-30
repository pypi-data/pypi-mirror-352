"""
MIT License

Copyright (c) 2025-present aqur1n

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import asyncio
from queue import SimpleQueue
from threading import Thread
from typing import Any, Generator


def set_result(future: asyncio.Future, result: Any) -> None:
    """Set a future result if this has not already been done. """
    if not future.done():
        future.set_result(result)

def set_exception(future: asyncio.Future, exception: BaseException) -> None:
    """Set a future exception if this has not already been done. """
    if not future.done():
        future.set_exception(exception)


class _StopRunningAsyncSentinel:
    def __init__(self) -> None:
        self.future = asyncio.get_event_loop().create_future()

    def __await__(self) -> Generator[Any, None, Any]:
        return self.future.__await__()

class _QueueItem:
    def __init__(self, future: asyncio.Future, args: tuple, kwargs: dict) -> None:
        self.future = future
        self.args = args
        self.kwargs = kwargs

class Worker(Thread):
    """An abstract class that provides a base worker.

    You can create a child class and override the :func:`execute` method where you will execute the job.

    You can also override :func:`check` method where you will check if the worker can do the given job.

    Examples
    -------

    .. code-block:: python3
        
        class MyWorker(workerio.Worker):
            def check(self, arg1, arg2, ...) -> bool:
                if ...:
                    return True
                return False

            def execute(self, arg1, arg2, ...) -> Any:
                result = mylogic(...)
                return result
    """

    def __init__(self):
        super().__init__()

        self._running = False
        self._tx: SimpleQueue[_QueueItem | _StopRunningAsyncSentinel] = SimpleQueue()

    @property
    def is_running(self) -> bool:
        """Returns whether the worker has been started. """
        return self._running
    
    @property
    def is_empty(self) -> bool:
        """Returns whether the work queue is empty (not reliable!). """
        return self._tx.empty()
    
    @property
    def qsize(self) -> int:
        """Returns the number of jobs in the queue (not reliable!). """
        return self._tx.qsize()

    def run(self) -> None:
        while True:
            if not self._running:
                break

            item = self._tx.get()

            if isinstance(item, _StopRunningAsyncSentinel):
                item.future.get_loop().call_soon_threadsafe(set_result, item.future, True)
                break
            
            try:
                result = self.execute(*item.args, **item.kwargs)
                item.future.get_loop().call_soon_threadsafe(set_result, item.future, result)

            except BaseException as e:
                item.future.get_loop().call_soon_threadsafe(set_exception, item.future, e)

        self._running = False

    def start(self) -> None:
        """Start the worker. """
        self._running = True
        super().start()
    
    async def stop(self) -> None:
        """Stop the worker and waits for all work to be completed. """
        s = _StopRunningAsyncSentinel()
        self._tx.put_nowait(s)

        await s

    def stop_nowait(self) -> _StopRunningAsyncSentinel:
        """Stop the worker (does not wait for all work to be completed). """
        s = _StopRunningAsyncSentinel()
        self._tx.put_nowait(s)

        return s
    
    def put_job(self, *args, **kwargs) -> asyncio.Future:
        """Add a job to the job queue. 
        
        Parameters
        ----------
        ...:
            The ``args`` and ``kwargs`` that workers get in the :func:`execute` method.

        Returns
        -------
        :class:`asyncio.Future`
            Future job result. Use `await` to get it.
        """
        future = asyncio.get_event_loop().create_future()
        self._tx.put_nowait(_QueueItem(future, args, kwargs))

        return future

    def check(self, *args, **kwargs) -> bool:
        """To see if the worker can do the job.

        You must override this method with your logic, otherwise it always returns ``True``.

        Parameters
        ----------
        ...:
            The ``args`` and ``kwargs`` that workers get in the :func:`execute` method.

        Returns
        -------
        :class:`bool`
            Whether the worker can do the job.
        """
        return True

    def execute(self, *args, **kwargs) -> Any:
        """Get the job done. 

        Must be overridden in the child class.

        Parameters
        ----------
        ...:
            Arguments of the job.

        Returns
        -------
        Any
            Job Result. May be ``None``.
        """
        raise NotImplementedError
