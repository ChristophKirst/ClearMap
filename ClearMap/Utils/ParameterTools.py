# -*- coding: utf-8 -*-
"""
ParameterTools

Provides simple formatting tools to handle / print parameter dictionaries
organized as key:value pairs.

"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.


def getParameter(parameter, key, default = None):
    """Gets a parameter from a dict, returns default value if not defined
    
    Arguments:
        parameter (dict): parameter dictionary
        key (object): key 
        default (object): deault return value if parameter not defined
    
    Returns:
       object: parameter value for key
    """
    
    if not isinstance(parameter, dict):
        return default;
    
    if key in parameter.keys():
        return parameter[key];
    else:
        return default;


def writeParameter(head = None, out = None, **args):
    """Writes parameter settings in a formatted way
    
    Arguments:
        head (str or None): prefix of each line
        out (object or None): write to a specific output, if None return string
        **args: the parameter values as key=value arguments
    
    Returns:
        str or None: a formated string with parameter info
    """
    if head is None:
        head = '';
        
    keys = args.keys();
    vals = args.values();
    parsize = max([len(x) for x in keys]);
    
    s = [head + ' ' + keys[i].ljust(parsize) + ': ' + str(vals[i]) for i in range(len(keys))];
    
    if out is None:
        return '\n'.join(s)
    else:
        out.write('\n'.join(s) + '\n');

    
def joinParameter(*args):
    """Joins dictionaries in a consitent way
    
    For multiple occurences of a key the  value is defined by the first key : value pair.
    
    Arguments:
        *args: list of parameter dictonaries
    
    Returns:
        dict: the joined dictionary
    """
    
    keyList = [x.keys() for x in args];
    n = len(args);
    
    keys = [];
    values = [];
    for i in range(n):
        values = values + [args[i][k] for k in keyList[i] if k not in keys];
        keys   = keys + [k for k in keyList[i] if k not in keys];
    
    return {keys[i] : values[i] for i in range(len(keys))}
    
    
    
    