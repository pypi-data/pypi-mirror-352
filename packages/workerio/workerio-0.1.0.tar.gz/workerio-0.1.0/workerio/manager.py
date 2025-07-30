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


from asyncio import Future
from typing import Callable, Type

from .exceptions import (SuitableWorkerNotFound, WorkerAlreadyPresent,
                         WorkersNotFound)
from .worker import Worker
from .workers import PartialWorker


class Manager:
    """A class that gives basic control over your workers.
    
    You can create a child class and override the task division logic for workers.

    Examples
    -------

    Basic Usage:
    .. code-block:: python3

        manager = workerio.Manager()
        manager.add_worker(MyWorker())

        manager.start_all()
        manager.put_work(MyWorker, arg1, arg2, mykwarg = "arg3")

    Creating a child class:
    .. code-block:: python3
        
        class MyManager(workerio.Manager):
            def put_work(self, worker_type: Type[Worker], *args, **kwargs) -> Future:
                # My logic here
    """

    def __init__(self):
        self._started = False
        self._workers: dict[Type[Worker], list[Worker]] = {}

    def add_worker(self, worker: Worker) -> None:
        """Add a worker to the list of workers of this type.

        Parameters
        ----------
        worker: :class:`Worker`
            The worker to be added.

        Raises
        ------
        :exc:`TypeError`
            The worker parameter is not an object of the Worker child class.
        :exc:`WorkerAlreadyPresent`
            The worker is already on the list of workers.
        """
        if not isinstance(worker, Worker):
            raise TypeError("the worker parameter must be an object of the child class Worker")

        if self._workers.get(worker.__class__) is None:
            self._workers[worker.__class__] = []

        if worker in self._workers[worker.__class__]:
            raise WorkerAlreadyPresent()

        self._workers[worker.__class__].append(worker)

    def remove_worker(self, worker: Worker) -> None:
        """Remove an worker from the list of workers.

        Parameters
        ----------
        worker: :class:`Worker`
            The worker to be added.

        Raises
        ------
        :exc:`WorkersNotFound`
            The worker is not on the list of workers.

        .. note::

            This will also stop it from working.
        """
        if self._workers.get(worker.__class__) is None:
            raise WorkersNotFound(worker.__class__)

        if worker.is_running:
            worker.stop_nowait()

        self._workers[worker.__class__].remove(worker)

        if len(self._workers[worker.__class__]) == 0:
            del self._workers[worker.__class__]

    def start_all(self) -> None:
        """Start all workers that are in the list. This does not apply to workers that have already been started. """
        for workers_type in self._workers:
            for worker in self._workers[workers_type]:
                if not worker.is_running:
                    worker.start()

        self._started = True

    async def stop_all(self) -> None:
        """|coro|
        
        Stop all workers from working. And waiting for all work to be completed.
        """
        for workers_type in self._workers:
            for worker in self._workers[workers_type]:
                await worker.stop()
                
        self._started = False

    def stop_all_nowait(self) -> None:
        """Stop the work of all workers. The remaining work will continue, but this function will not wait for a complete stop."""
        for workers_type in self._workers:
            for worker in self._workers[workers_type]:
                worker.stop_nowait()
                
        self._started = False

    def get_workers(self, worker_type: Type[Worker]) -> list[Worker]:
        """Get all workers of this type from the list.
        
        Returns
        -------
        list[:class:`Worker`]
            List of workers.
        """
        if self._workers.get(worker_type) is None:
            return []
        return self._workers[worker_type]
    
    def get_all_workers(self) -> list[Worker]:
        """Get all workers from the list.
        
        Returns
        -------
        list[:class:`Worker`]
            List of workers.
        """
        workers = []
        for workers_type in self._workers:
            workers.extend(self._workers[workers_type])

        return workers
    
    def get_suitable_workers(self, worker_type: Type[Worker], *args, **kwargs) -> list[Worker]:
        """Get all workers of this type from the list who are willing to do the job.
        
        Parameters
        ----------
        worker_type: Type[:class:`Worker`]
            Type of workers.
        ...:
            The ``args`` and ``kwargs`` that workers get in the :func:`execute` method.

        Returns
        -------
        list[:class:`Worker`]
            List of workers.
        """
        suitable_workers: list[Worker] = []

        for worker in self._workers.get(worker_type, []):
            if worker.is_running and worker.check(*args, **kwargs): 
                suitable_workers.append(worker)

        return suitable_workers

    def put_work(self, worker_type: Type[Worker], *args, **kwargs) -> Future:
        """Send the job to a less burdened (if there is one, otherwise first come first served) worker of that type.
        
        Parameters
        ----------
        worker_type: Type[:class:`Worker`]
            Type of workers.
        ...:
            The ``args`` and ``kwargs`` that workers get in the :func:`execute` method.

        Returns
        -------
        :class:`asyncio.Future`
            Future job result. Use `await` to get it.

        Raises
        ------
        :exc:`WorkersNotFound`
            Workers of this type are not on the list.
        :exc:`SuitableWorkerNotFound`
            No matching worker was found. Perhaps the :func:`check` method of all workers returned `False` or they are not all running.
        """
        if self._workers.get(worker_type) is None or len(self._workers[worker_type]) == 0:
            raise WorkersNotFound(worker_type)
        
        suitable_workers = self.get_suitable_workers(worker_type, *args, **kwargs)

        if len(suitable_workers) == 0:
            raise SuitableWorkerNotFound()
        
        works = sum(w.qsize for w in suitable_workers) / len(suitable_workers)
        selected_worker = suitable_workers[0]

        for worker in suitable_workers:
            if worker.qsize <= works and worker.check(*args, **kwargs):
                selected_worker = worker
                break

        return selected_worker.put_job(*args, **kwargs)
    
    def puts_work(self, workers_types: tuple[Type[Worker]], *args, **kwargs) -> Future:
        """Send the job to a less burdened (if there is one, otherwise first come first served) worker of these types.
        
        Unlike :func:`put_work` this supports multiple worker types. For example, if you have different worker types doing the job differently.
        
        Parameters
        ----------
        workers_types: tuple[Type[:class:`Worker`]
            Types of workers.
        ...:
            The ``args`` and ``kwargs`` that workers get in the :func:`execute` method.

        Returns
        -------
        :class:`asyncio.Future`
            Future job result. Use `await` to get it.

        Raises
        ------
        :exc:`SuitableWorkerNotFound`
            No matching worker was found. Perhaps the :func:`check` method of all workers returned `False` or they are not all running.
        """
        suitable_workers: list[Worker] = []
        for wt in workers_types:
            suitable_workers.extend(self.get_suitable_workers(wt, *args, **kwargs))

        if len(suitable_workers) == 0:
            raise SuitableWorkerNotFound()
        
        works = sum(w.qsize for w in suitable_workers) / len(suitable_workers)
        selected_worker = suitable_workers[0]

        for worker in suitable_workers:
            if worker.qsize <= works and worker.check(*args, **kwargs):
                selected_worker = worker
                break

        return selected_worker.put_job(*args, **kwargs)

    def put_partial_work(self, func: Callable, *args, **kwargs) -> Future:
        """A wrapper for :func:`put_work` that sends work to :class:`workers.PartialWorker` to execute a synchronous function.

        .. note::
        
            The function will be called in another thread, so only use thread-safe functions.

        Parameters
        ----------
        func: :class:`Callable`
            The function that needs to be performed.
        ...:
            The ``args`` and ``kwargs`` of this function.

        Returns
        -------
        :class:`asyncio.Future`
            The future result returned by the function. Use `await` to get it.
        """
        if self._workers.get(PartialWorker) is None or len(self._workers[PartialWorker]) == 0:
            worker = PartialWorker()
            self.add_worker(worker)
            worker.start()
        
        return self.put_work(PartialWorker, func, *args, **kwargs)
