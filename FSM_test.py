# -*- coding: utf-8 -*-
"""
# @Author: Wzx
# @Date: 2021/6/27 0:58
# @File: FSM_test.py
# @Software: PyCharm
# @Description: 

"""
import unittest
import io
import sys
from FSM import StateMachine


class StateMachineTest(unittest.TestCase):

    def test_after_delay(self):
        fsm = StateMachine(1, 10)

        @fsm.after_delay(5)
        def task(inp, out):
            if not inp:
                return "0", False
            elif inp == "0":
                if out == '0':
                    return "0", False
                elif out == "1":
                    return "1", True
            return inp, False

        task("0", "0")
        fsm.run()
        self.assertEqual(fsm.log[6][0][0], "Running")
        self.assertEqual(fsm.log[6][0][1], 0)


    def test_IO(self):
        fsm = StateMachine(1, 10)

        @fsm.IO_en(True)
        @fsm.seq_sup(["0"])
        def task(inp, out):
            if not inp:
                return "0", False
            elif inp == "0":
                if out == '0':
                    return "0", False
                elif out == "1":
                    return "1", True
            return inp, False
        task("0", "0")

        def stub_stdin(test, inputs):
            stdin = sys.stdin

            def cleanup():
                sys.stdin = stdin
            test.addCleanup(cleanup)
            sys.stdin = io.StringIO(inputs)

        stub_stdin(self, '0\n0 0 0 1\n\n\n\n\n\n\n\n\n\n\n\n\n')
        fsm.run()
        self.assertEqual(fsm.log[1][0][0], "Running")
        self.assertEqual(fsm.log[1][0][1], 0)

    def test_parallel(self):
        fsm = StateMachine(1, 10)

        @fsm.seq_sup(['0', '0', '1'])
        def task1(inp, out):
            if not inp:
                return "0", False
            elif inp == "0":
                if out == '0':
                    return "0", False
                elif out == "1":
                    return "1", True
            return inp, False

        @fsm.after_delay(1)
        def task2(inp, out):
            if not inp:
                return "a", False
            elif inp == "a":
                if out == "a":
                    return "a", False
                elif out == "b":
                    return "b", True
            return inp, False

        task1("0", "0")
        task2("a", "a")

        fsm.run()
        self.assertEqual(fsm.log[1][0][0], "Running")
        self.assertEqual(fsm.log[1][0][1], 0)
        self.assertEqual(fsm.log[3][0][0], "Finished")
        self.assertEqual(fsm.log[3][0][1], 0)


    def test_queue(self):
        fsm = StateMachine(1, 10)

        @fsm.queue_(["0", "0", "1"])
        def task1(inp, out):
            if not inp:
                return "0", False
            elif inp == "0":
                if out == '0':
                    return "0", False
                elif out == "1":
                    return "1", True
            return inp, False

        @fsm.queue_(["a", "a", "b", "b"])
        def task2(inp, out):
            if not inp:
                return "a", False
            elif inp == "a":
                if out == "a":
                    return "a", False
                elif out == "b":
                    return "b", True
            return inp, False

        task1("0", "0")
        task2("a", 'a')
        fsm.run()
        self.assertEqual(fsm.log[1][0][0], "Running")
        self.assertEqual(fsm.log[1][0][1], 0)
        self.assertEqual(fsm.log[3][0][0], "Finished")
        self.assertEqual(fsm.log[3][0][1], 0)
        self.assertEqual(fsm.log[3][1][0], "Running")
        self.assertEqual(fsm.log[3][1][1], 1)
        self.assertEqual(fsm.log[6][0][0], "Finished")
        self.assertEqual(fsm.log[6][0][1], 1)

    def test_transition(self):
        fsm = StateMachine(1, 10)

        @fsm.seq_sup(["0", "1", "2"])
        def task(inp, out):
            if not inp:
                return "0", False
            elif inp == "0":
                if out == '0':
                    return "0", False
                elif out == "1":
                    return "1", False
                elif out == '2':
                    return "0", False
            elif inp == '1':
                if out == '0':
                    return "0", False
                elif out == "1":
                    return "1", False
                elif out == '2':
                    return "2", True
            return inp, False

        @fsm.task_transition(0)
        def follow_task(inp, out):
            if not inp:
                return "0", False
            elif inp == "0":
                if out == '0':
                    return "0", False
                elif out == "1":
                    return "0", False
                elif out == '2':
                    return "1", True
            return inp, False

        task("1", "0")
        follow_task("1", '0')
        fsm.run()
        self.assertEqual(fsm.log[1][0][0], "Running")
        self.assertEqual(fsm.log[1][0][1], 0)
        self.assertEqual(fsm.log[1][1][0], "Running")
        self.assertEqual(fsm.log[1][1][1], 1)
        self.assertEqual(fsm.log[3][0][0], "Finished")
        self.assertEqual(fsm.log[3][0][1], 0)
        self.assertEqual(fsm.log[4][0][0], "Finished")
        self.assertEqual(fsm.log[4][0][1], 1)


if __name__ == '__main__':
    unittest.main()
