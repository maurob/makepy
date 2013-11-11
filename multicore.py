# -*- coding: utf-8 -*-

"""
Module to give multiprossesing facilities for external execultable
"""

import multiprocessing
import subprocess
import time

from multiprocessing import cpu_count

class Multicore(object):
    def __init__(self, count=None):
        if not count:
            self.cpu_count = cpu_count()
        else:
            self.cpu_count = count

        self.processes = {}

    def __len__(self):
        return self.cpu_count


    def clean(self):
        for p in self.processes:
            print p, p.returncode
            if p.returncode is not None:
                
                def save(text, filename):
                    if len(text) > 0 and filename:
                        with open(filename, 'w') as f:
                            f.write(text)
                
                save(p.stdout.read(), p.stdout_filename)
                save(p.stderr.read(), p.stderr_filename)

                del self.processes[p]


    def shell(self, cmd, stdout=None, stderr=None):
        """
        Run the shell cmd in a separate process and write the output to the
        *stdout* and *stderr* if specified.

        shell is non blocking is the actual concurrency is less than
        *self.cpu_count*, otherwise it blocks until there's room
        """
        self.wait()
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        p.stdout_filename = stdout
        p.stderr_filename = stderr
        self.processes[p] = p

    def _wait(self, n):
        print self.processes
        self.clean()
        while len(self.processes) > n:
            print self.processes
            time.sleep(1)
            self.clean()

    def wait_all(self):
        self._wait(0)

    def wait(self):
        self._wait(self.cpu_count)
        
    def __del__(self):
        self.wait_all()
        
    
