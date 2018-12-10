 #!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-12-20 16:41:01
# @Author  : Kailun Luo (luokl3@mail2.sysu.edu.cn)
# @Link    : https://sdcs.sysu.edu.cn
# @Version : $Id$


import os
import re
import base64
import context_operator
import json
import itertools
from functools import reduce
import sys
sys.path.append("..")



encode_pair = (['(',')'],['[',']'])
encode_pair_forall = (['[',']'],['{','}'])
encode_pair_unmatch = (['(',')'],['{','}'])
encode_pair_para = (['(',')',','],['[',']','#'])

exp_pattern_str = r"(?:(?:\d|[A-Z]|[\+\-\*\|\(\)\s])*)"
const_pattern_str = r"(?:[a-z][a-z\d]*)"    
var_pattern_str = r"(?:[A-Z][A-Z\d]*)"

parenth_pattern_str = r"\([^\(\)]*\)"
parenth_pattern = re.compile(parenth_pattern_str)

bracket_pattern_str=r"\[[^\[\]]*\]"
bracket_pattern = re.compile(bracket_pattern_str)

#forall_pattern_str = r"(?:forall|exists)\([\w\s\d,]+?\)\[[^\[\]]+\]"      #depth 0 patter
forall_pattern_str = r"(?:forall|exists)\([\w\:\s\d,]+?\)\[[^\[\]]+\]"
forall_pattern =re.compile(forall_pattern_str)

notlogic_pattern_str = r"(?:(?:(?<!and)(?<!or)(?<!=>).(?!and)(?!or)(?!=>))+)"
function_pattern_str = r"\s*([\w\d]+?)\(((?:(?<!=).)*)\)(?:\s*=\s*(" +notlogic_pattern_str + "))?"
#function_pattern_str = r"\s*([\w\d]+)\(?((?:(?<!=).)+)?\)?(?:\s*=\s*(" +notlogic_pattern_str + "))?" 
function_pattern = re.compile(function_pattern_str)

rename_pattern_str = r"(?:forall|exists)\((?P<var>[\w\:\s\d,]+?)\)\[(?P<body>[^\[\]]+)\]"
rename_pattern = re.compile(rename_pattern_str)

grounding_pattern_str = r"(?P<head>(?:forall|exists))\((?P<var>[\w\:\s\d,]+?)\)\[(?P<body>[^\[\]]+)\]"
grounding_pattern = re.compile(grounding_pattern_str)

#take =lambda *varList: reduce(lambda x,y: re.sub(y[0],str(y[1]),x),zip([r'\bA\b',r'j\b'],list(varList)),m)

sub_lambda_exp = lambda x,y: re.sub(y[0],y[1],x)
replace_lambda_exp = lambda x,y: x.replace(y[0],y[1])



def endecode_string(my_str, old_symbols, new_symbols):
	return repeat_do_function(replace_lambda_exp, zip(old_symbols, new_symbols), my_str)

# repeat to do function f with a list of arguments, initial argument is mbase
def repeat_do_function(f,args_list,mbase):
	return reduce(lambda x,y: f(x,y),args_list,mbase)


def __mrepl_encode(matched):
	match_str=matched.group()
	encoded_str=endecode_string(match_str, encode_pair_para[0], encode_pair_para[1])
	return encoded_str


def __mrepl_unmatch(matched):
	match_str=matched.group()
	encoded_str=endecode_string(match_str, encode_pair_unmatch[0], encode_pair_unmatch[1])
	return encoded_str

#my_str="take(1,X,fun(1,2))"
#print repeat_do_function(sub_lambda_exp, zip([r'\bX\b',r'j\b'],['1','2']), my_str)
#print repeat_do_function(sub_lambda_exp, zip([r'\bX\b',r"fun\(1,2\)"],[__mrepl,__mrepl]), my_str)


#1,X,fun(1,2) -> 1,X,fun[1_2] -> ['1', 'X', 'fun[1_2]']
def repeat_replace_inner_with_pattern(repeat_pattern, mrepl, my_str):
	while(True):
		encoded_str=repeat_pattern.sub(mrepl, my_str)
		my_str = encoded_str if my_str!=encoded_str else None
		if my_str is None:
			break	
	return encoded_str


def eliminate_unmatched(m_str):
	m_str = repeat_replace_inner_with_pattern(parenth_pattern, __mrepl_unmatch, m_str)
	m_str = m_str.replace('(',"").replace(')',"").replace('[',"").replace(']',"")
	return endecode_string(m_str, encode_pair_unmatch[1], encode_pair_unmatch[0])

#s="function(ff,fs(d)f)+)]"
#print eliminate_unmatched(s)


def get_paras_from_str(para_str):
	encoded_str = repeat_replace_inner_with_pattern(parenth_pattern, __mrepl_encode, para_str)
	encoded_para_list = encoded_str.split(',')
	return [endecode_string(my_str, encode_pair_para[1], encode_pair_para[0]) for my_str in encoded_para_list]



def parse_function(function_str):
	match = function_pattern.match(function_str)
	if match:
		return match.group(1), match.group(2), "" if not match.group(3) else match.group(3)
	else:
		#logger.info('~~~~~~(ERROR): %s'%function_str)
		error_message = "#Error-----when parsing str %s-----Util.parse_function: Exist" %function_str
		raise Exception(error_message)


def generate_function_feature(function_str):
	function_name, function_args_str, function_value= parse_function(function_str)
	para_list = get_paras_from_str(function_args_str)
	function_feature = function_name + '_' + '_'.join(para_list)+'_'+function_value
	function_feature = re.sub(r'\s+', '', function_feature)
	return function_feature
'''
def __mrepl_rename(match):
	#print "hello",match.group(0)
	old_var_list = match.group('var').split(',')
	old_var_list = [r'\b' + var + r'\b' for var in old_var_list]
	new_var_list = [context_operator.get_new_var() for e in range(0, len(old_var_list))]
	#print zip(old_var_list,new_var_list)
	rename_str = Util.repeat_do_function(Util.sub_lambda_exp, zip(old_var_list,new_var_list), match.group(0))
	#print rename_str
	encoded_rename_str = Util.endecode_string(rename_str,Util.encode_pair_forall[0], Util.encode_pair_forall[1])
	return encoded_rename_str

#s="forall(X,Y)[(X=1 or X=2 or X=3) and exists(Y)[(Y=1 or Y=2 or Y=3)] => num(X)=num(Y)] and turn(P)"

def rename(formula):
	#print rename_pattern.findall(s)
	encoded_formula = Util.repeat_replace_inner_with_pattern(Util.rename_pattern, __mrepl_rename, formula)
	return Util.endecode_string(encoded_formula, Util.encode_pair_forall[1], Util.encode_pair_forall[0])

'''

def __mrepl_rename(match):
	#print "hello",match.group(0)
	old_var_list = match.group('var').split(',')
	old_var_list = [r'\b' + var + r'\b' for var in old_var_list]
	new_var_list = [context_operator.get_new_var() for e in range(0, len(old_var_list))]
	#print zip(old_var_list,new_var_list)
	rename_str = repeat_do_function(sub_lambda_exp, zip(old_var_list,new_var_list), match.group(0))
	#print rename_str
	encoded_rename_str = endecode_string(rename_str,encode_pair_forall[0], encode_pair_forall[1])
	return encoded_rename_str

#s="forall(X,Y)[(X=1 or X=2 or X=3) and exists(Y)[(Y=1 or Y=2 or Y=3)] => num(X)=num(Y)] and turn(P)"

def rename_forall(formula):
	#print rename_pattern.findall(s)
	encoded_formula = repeat_replace_inner_with_pattern(rename_pattern, __mrepl_rename, formula)
	return endecode_string(encoded_formula, encode_pair_forall[1], encode_pair_forall[0])



pre_fluent_replace_pair = (['(',')'],['\(','\)'])

def pre_fluent_replace(m_str):
	return repeat_do_function(replace_lambda_exp, zip(pre_fluent_replace_pair[0],pre_fluent_replace_pair[1]), m_str)


def handle_zero_fluents(formula):
	replaces = [ (r'\b' + fluent + r'\b', fluent+'()') for fluent in context_operator.get_zero_fluents()]
	return repeat_do_function(sub_lambda_exp, replaces ,formula)


def del_redundant_dict(dict_list):
	dict_list = set(json.dumps(elem) for elem in dict_list)
	return [json.loads(elem) for elem in dict_list]


def __get_set(mlist):
	return set([json.dumps(elem) for elem in mlist])

def __get_dict_elems(mlist):
	return 	[ json.loads(elem) for elem in mlist]

def __get_elems(mlist):
	return [ tuple(json.loads(elem)) for elem in mlist]

##############################################################################################################################################################


s = "exists(K12:Int)[     ! K12 % numStone() -3    ] and forall(X:Int)[exists(K10:Int)[      K10 = numStone() -3    ] and K10 >= X] or forall(X:Int,Y:Int)[exists(K11:Int)[      K11 = numStone() -3    ] and K11 + X =Y] and K12 <=0 and  !turn(p2)"


def __get_constraint_var_dict(var_list, formula):
	fluent_constraints = context_operator.get_fluent_constraint()
	#var_keys = sum([util_constraint.find_fluent_constraint_var(formula, var_name, fluent_constraints) for var_name in var_list],[])
	#var_constraints = {var: fluent_constraints[key] for var, key in var_keys}
	var_constraints = util_constraint.find_fluent_constraint_vars(formula, var_list, fluent_constraints)
	return dict(var_constraints)


def __mrepl_ground(match):
	logical_connector = "and" if match.group('head') =='forall' else 'or'
	
	#universe = {'Int': ['1', '0', '3', '2'], '_S1': [], '_S2': ['p2', 'p1'], 'Bool': ['True', 'False']}

	model = context_operator.get_current_model()
	universe = context_operator.get_universe()
	#if 'numStone()' in model:
		#print model['numStone()']
		#print [ str(elem) for elem in range(0, int(model['numStone()'])+1)]
		#print universe['Int']
		#print list(set(universe['Int'] + [ str(elem) for elem in range(0, int(model['numStone()'])+1)]))
	#	universe['Int'] = list(set(universe['Int'] + [ str(elem) for elem in range(0, int(model['numStone()'])+1)]))
	#print context_operator.get_sort_symbols_dict()
	#print universe
	#exit(0)
	vars_sorts = { elem.split(':')[0]: elem.split(':')[1] for elem in  match.group('var').split(',') }
	var_list = vars_sorts.keys()
	var_constraint_dict = __get_constraint_var_dict(var_list, match.group('body'))
	
	vars_consts = [ (var, var_constraint_dict[var])if var in var_constraint_dict else (var, universe[sort]) for var, sort in vars_sorts.iteritems()]
	vars_list = [ r'\b'+var+r'\b' for var in zip(*vars_consts)[0] ]
	consts_list = list(itertools.product(*zip(*vars_consts)[1]))

	instances = [ repeat_do_function(sub_lambda_exp, zip(vars_list,list(consts)), match.group('body')) for consts in consts_list ]

	return "(%s)"%logical_connector.join(["(%s)"%ins for ins in instances ])


def grounding_formula(formula):
	return repeat_replace_inner_with_pattern(grounding_pattern, __mrepl_ground, formula)


def strip_kuohao(formula):
	if len(formula)<2:
		return formula
	elif formula[0] == '(':
		return formula[1:len(formula)-1].strip()
	else:
		return formula
'''
s = "exists(K11:Int)[numStone()=K11+3]"
universe = {'Int': ['1', '0', '3', '2'], '_S1': [], '_S2': ['p2', 'p1'], 'Bool': ['True', 'False']}
print grounding_formula(s)
exit(0)

'''



