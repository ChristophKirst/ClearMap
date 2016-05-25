# -*- coding: utf-8 -*-
"""
Provides simple formatting tools to print text with parallel process header

"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.


import sys

class ProcessWriter(object):
    """Class to handle writing from parallel processes
    
    Attributes:
        process (int): the process number
    
    """
    
    def __init__(self, process = 0):
        self.process = process;
    
    def writeString(self, text):
        """Generate string with process prefix
        
        Arguments:
            text (str): the text input
            
        Returns:
            str: text with [process prefix
        """
        pre = ("Process %d: " % self.process);
        return pre + str(text).replace('\n', '\n' + pre);
    
    def write(self, text):
        """Write string with process prefix to sys.stdout
        
        Arguments:
            text (str): the text input
        """
        
        print self.writeString(text);
        sys.stdout.flush();

    