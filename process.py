"""
This module is a parallel dispatcher for command lines

TODO: Make it really in parallel ;)
"""

# If True just print the cmd and not execute it
just_print  = False

import os

class MultiProcess(object):
    def add(self, cmd):
        """ Enqueue a new process """
        print cmd
        if not just_print:
            os.system(cmd)

    def wait(self):
        """ Wait for all process to finish """
        return


            
