# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 13:33:30 2015

@author: ckirst
"""

import numpy as np;

def dosomething(x):
    x = x.transpose();
    
    return x;
    
    
z = np.random.rand(215000,5);


print z.shape
y = dosomething(z);
print z.shape
print y.shape