#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-12-23 15:57:26
# @Author  : Kailun Luo (luokl3@mail2.sysu.edu.cn)
# @Link    : https://sdcs.sysu.edu.cn
# @Version : $Id$


LOCAL_DICT = dict()
VAR_INDEX = 0
ACTION = ""
ZERO_FLUENT_SET = set()
  
 
AXIOMS = dict()
AXIOMS['ssa'] = dict()
AXIOMS['poss'] = dict()
AXIOMS['win'] = dict()
AXIOMS['init'] = dict()
AXIOMS['end'] = dict()


ACTION_LIST = list()
FLUENT_LIST = list()
PREDICATES = list()


NREGX_FUNCTION_PATTERNS = list()
FUNCTION_PATTERNS = list()


FUNCTION_LAMBDA_REGRESS = None
PREDICATE_LAMBDA_REGRESS = None

UNIVERSE = None 
FEATURE_LIST = list()

EFFECTS = list()

'''
import re
s = "ahhhh_fdlsfj and ffslfsf or jflsdfjl"

pattern =re.compile(r"(?:(?<!and)(?<!or).(?!and)(?!or))+")

print pattern.findall(s)

'''

#x = list(set(a[i]+a[j]))
#y = len(a[j])+len(a[i])
'''
a= ['INT', 'INT', ('m', 2), 'INT', ('f', 1), ('num', 1), ('g', 1), 'INT', ('m', 2), 'INT', ('num', 1)]
b= ['num']
print len(list(set(a+b)))
print len(set(a)),len(set(b))
[['num', 'num'],  
[  ['INT', 'INT', ('m', 2), 'INT', ('f', 1), ('num', 1), ('g', 1), 'INT', ('m', 2), 'INT', ('num', 1)]]

[  [('m', 2), ('f', 1), 'INT', ('g', 1), 'num', ('num', 1)]]

'''



#apply(hello,[('Init', '', ' numStone >0  '), ('Init', '', ' turn(p1) and !turn(p2)    ')])


#hello()