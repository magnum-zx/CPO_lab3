import collections
import time
from functools import wraps
from typing import Any, Callable, Tuple, Union, List


class StateMachine(object):
    """
    'Design a representation of the finite state machine using decorators to specify state machine handlers.'
    """

    def __init__(self, T: int, HALT: int) -> None:
        """
        Initialize a State Machine.
        """
        self.handlers = collections.OrderedDict()
        self.delay_pool = collections.OrderedDict()
        self.delay_start_state = collections.OrderedDict()
        self.in_seq = collections.OrderedDict()
        self.work_pool = collections.OrderedDict()
        self.res_pool = collections.OrderedDict()
        self.channel = collections.OrderedDict()
        self.wait_count = 0
        self.PID = 0
        self.cycle = 1
        self.T = T
        # signal of End
        self.HALT = HALT
        # IO switch
        self.IO_enable = False
        # log the process
        self.log = {}
        self.queue = []
        self.queue_temp = []
        self.queue_init = []
        self.current = -1


    def after_delay(self, delay_cycle: int) -> Any:
        """
         make a task execute after a delay.
        """
        def decorator(func: Callable[[str, str], Any]) -> Any:
            @wraps(func)
            def wrapper(a: str, b: str) -> None:
                self.handlers[self.wait_count] = func
                self.delay_pool[self.wait_count] = delay_cycle
                self.delay_start_state[self.wait_count] = b
                func(a, b)

            return wrapper

        return decorator

    def queue_(self, input: str) -> Any:
        """
        make handlers enter the queue.
        when running, the handler in the handlers queue will be executed in sequence.
        """
        def decorator(func: Callable[[str, str], Any]) -> Any:
            @wraps(func)
            def wrapper(a: str, b: str) -> None:
                self.queue.append(func)
                self.queue_temp.append(input)
                self.queue_init.append(b)

            return wrapper

        return decorator

    def seq_sup(self, input: str) -> Any:
        """
        perform a task and load a string of input signals.
        """
        def decorator(func: Callable[[str, str], Any]) -> Any:
            @wraps(func)
            def wrapper(a: str, b: str) -> None:
                if self.cycle not in self.log.keys():
                    self.log[self.cycle] = []
                self.work_pool[self.PID] = func
                self.in_seq[self.PID] = input
                self.res_pool[self.PID] = b
                self.log[self.cycle].append(["Running", self.PID])
                self.PID += 1
                func(a, b)

            return wrapper

        return decorator

    def task_transition(self, PID_: int):
        def decorator(func: Callable[[str, str], Any]) -> Any:
            @wraps(func)
            def wrapper(a: str, b: str) -> None:
                if self.cycle not in self.log.keys():
                    self.log[self.cycle] = []
                self.work_pool[self.PID] = func
                self.in_seq[self.PID] = []
                self.res_pool[self.PID] = b
                self.log[self.cycle].append(["Running", self.PID])
                if PID_ in self.channel.keys():
                    self.channel[PID_].append(self.PID)
                else:
                    self.channel[PID_] = [self.PID]
                self.PID += 1
                func(a, b)

            return wrapper

        return decorator

    def run(self) -> None:
        while True:
            if self.cycle not in self.log.keys():
                self.log[self.cycle] = []
            if self.current == -1:
                if len(self.queue) > 0:
                    self.work_pool[self.PID] = self.queue[0]
                    self.in_seq[self.PID] = self.queue_temp[0]
                    self.res_pool[self.PID] = self.queue_init[0]

                    # log current Process
                    self.log[self.cycle].append(["Running", self.PID])
                    self.current = self.PID
                    self.PID += 1

                    # del finished work in queue
                    del self.queue[0]
                    del self.queue_temp[0]
                    del self.queue_init[0]

            # cycle is end
            if self.cycle == self.HALT:
                break
            for i in self.delay_pool:
                if self.delay_pool[i] == 0:
                    self.work_pool[self.PID] = self.handlers[i]
                    self.in_seq[self.PID] = []
                    self.res_pool[self.PID] = self.delay_start_state[i]
                    self.log[self.cycle].append(["Running", self.PID])
                    self.PID += 1
                self.delay_pool[i] = self.delay_pool[i] - 1

            delList = []
            for i in self.res_pool:
                if len(self.in_seq[i]) != 0:
                    self.res_pool[i], Terminal = self.work_pool[i](self.res_pool[i], self.in_seq[i][0])
                    del self.in_seq[i][0]
                else:
                    self.res_pool[i], Terminal = self.work_pool[i](self.res_pool[i], None)
                if Terminal:
                    self.log[self.cycle].append(["Finished", i])
                    delList.append(i)
                    if self.current == i:
                        if len(self.queue) > 0:
                            self.work_pool[self.PID] = self.queue[0]
                            self.in_seq[self.PID] = self.queue_temp[0]
                            self.res_pool[self.PID] = self.queue_init[0]
                            self.log[self.cycle].append(["Running", self.PID])
                            self.current = self.PID
                            self.PID += 1
                            del self.queue[0]
                            del self.queue_temp[0]
                            del self.queue_init[0]
            for i in self.channel:
                for j in self.channel[i]:
                    if i in self.work_pool.keys() and j in self.work_pool.keys():
                        self.in_seq[j].append(self.res_pool[i])
            for i in delList:
                del self.work_pool[i]
                del self.in_seq[i]
                del self.res_pool[i]
            self.cycle += 1
            time.sleep(self.T)
