# -*- coding: utf-8 -*-

"""
Provides tools for timing


"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

import time


class Timer(object):
    """Class to stop time and print results in formatted way
    
    Attributes:
        time (float): the time since the timer was started
    """
    def __init__(self, verbose=False):
        self.verbose = verbose;
        self.start();

    def start(self):
        """Start the timer"""
        self.time = time.time();
    
    def reset(self):
        """Reset the timer"""
        self.time = time.time();
    
    def elapsedTime(self, head = None, asstring = True):
        """Calculate elapsed time and return as formated string
        
        Arguments:
            head (str or None): prefix to the string
            asstring (bool): return as string or float
        
        Returns:
            str or float: elapsed time
        """
        
        t = time.time();
        
        if asstring:
            t = self.formatElapsedTime(t - self.time);
            if head != None:
                return head + ": elapsed time: " + t;
            else:
                return "Elapsed time: " + t;
        else:
            return t - self.time;
    
    def printElapsedTime(self, head = None):
        """Print elapsed time as formated string
        
        Arguments:
            head (str or None): prefix to the string
        """
        print self.elapsedTime(head = head);
    
    def formatElapsedTime(self, t):
        """Format time to string
        
        Arguments:
            t (float): time in seconds prefix
        
        Returns:
            str: time as hours:minutes:seconds
        """
        m, s = divmod(t, 60);
        h, m = divmod(m, 60);
        
        return "%d:%02d:%02d" % (h, m, s);

