#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: concurrency.py
# Author: Yuxin Wu <ppwwyyxxc@gmail.com>

import multiprocessing as mp
from .base import Callback
from ..utils.concurrency import start_proc_mask_signal, StoppableThread
from ..utils import logger

__all__ = ['StartProcOrThread']


class StartProcOrThread(Callback):
    """
    Start some threads or processes before training.
    """

    def __init__(self, startable, stop_at_last=True):
        """
        Args:
            startable (list): list of processes or threads which have ``start()`` method.
                Can also be a single instance of process of thread.
            stop_at_last (bool): whether to stop the processes or threads
                after training. It will use :meth:`Process.terminate()` or
                :meth:`StoppableThread.stop()`, but will do nothing on normal
                `threading.Thread` or other startable objects.
        """
        if not isinstance(startable, list):
            startable = [startable]
        self._procs_threads = startable
        self._stop_at_last = stop_at_last

    def _before_train(self):
        logger.info("Starting " +
                    ', '.join([k.name for k in self._procs_threads]))
        # avoid sigint get handled by other processes
        start_proc_mask_signal(self._procs_threads)

    def _after_train(self):
        if not self._stop_at_last:
            return
        for k in self._procs_threads:
            if isinstance(k, mp.Process):
                k.terminate()
                k.join()
            elif isinstance(k, StoppableThread):
                k.stop()
            else:
                logger.warn(
                    "[StartProcOrThread] {} "
                    "is neither a Process nor a StoppableThread, won't stop it.".format(k.name))
