#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-12-25 21:54:20
# @Author  : Kailun Luo (luokl3@mail2.sysu.edu.cn)
# @Link    : https://sdcs.sysu.edu.cn
# @Version : $Id$
   
import os
import global_context
import Util
import re


def get_replace_list():
	return global_context.RPLIST

def clear_replace_list():
	global_context.RPLIST = list()
	global_context.RP_INDEX =0


def add_replace_list(elem):
	repl = "RP%s"%str(global_context.RP_INDEX)
	global_context.RP_INDEX+=1
	global_context.RPLIST.append((r"\b%s\b"%repl, elem))
	return repl


def get_formula_from_local_dict():
	local_dict = get_local_dict()
	mvars = [local_dict[fluent] for fluent in local_dict.keys() ]
	formula_str=' and '.join([str( key )+"="+str(value) for key, value in local_dict.items()])
	return 'exists('+ ','.join(mvars)+ '){ '+ formula_str if formula_str!="" else formula_str


def use_local_dict():
	global_context.LOCAL_DICT = dict()

def update_local_dict(m_dict):
	global_context.LOCAL_DICT.update(m_dict)

def get_local_dict():
	return global_context.LOCAL_DICT


def get_new_var():
	global_context.VAR_INDEX += 1
	return 'K'+ str(global_context.VAR_INDEX)


def get_global_action():
	return global_context.ACTION#'take(1,a,f(x)+3)'


def set_global_action(action):
	global_context.ACTION = action


def add_zero_fluent(fluent_name):
	global_context.ZERO_FLUENT_SET.add(fluent_name)

def set_zero_fluent(fluents):
	global_context.ZERO_FLUENT_SET = fluents

def get_zero_fluents():
	return global_context.ZERO_FLUENT_SET




def get_axioms():
	return global_context.AXIOMS




def add_actions(actions):
	global_context.ACTION_LIST.extend(actions)
	global_context.ACTION_LIST = list(set(global_context.ACTION_LIST))

def add_fluents(fluents):
	global_context.FLUENT_LIST.extend(fluents)
	global_context.FLUENT_LIST = list(set(global_context.FLUENT_LIST))

def get_actions():
	return global_context.ACTION_LIST

def get_fluents():
	return global_context.FLUENT_LIST


def set_function_sorts(fun, sorts):
	global_context.FLUENT_SORT_DICT[fun] = sorts

def set_functions_sorts(m_dict):
	global_context.FLUENT_SORT_DICT = m_dict

def get_functions_sorts():
	return global_context.FLUENT_SORT_DICT


def add_predicates(p_list):
	global_context.PREDICATES.extend(p_list)

def get_predicates():
	return global_context.PREDICATES


def add_feature(feature):
	global_context.FEATURE_LIST.append(feature)

def get_feature(feature):
	return global_context.FEATURE_LIST


def add_predicate_sorts(p_dict):
	global_context.PREDICATE_SORT_DICT.update(p_dict)

def get_predicate_sorts():
	return global_context.PREDICATE_SORT_DICT


def add_nregx_function_patterns(pattern_list):
	global_context.NREGX_FUNCTION_PATTERNS.extend(pattern_list)

def get_nregx_function_patterns():
	return global_context.NREGX_FUNCTION_PATTERNS


def get_function_regress_lambda():
	return global_context.FUNCTION_LAMBDA_REGRESS 

def set_function_regress_lambda(lambda_exp):
	global_context.FUNCTION_LAMBDA_REGRESS = lambda_exp



def get_predicate_regress_lambda():
	return global_context.PREDICATE_LAMBDA_REGRESS 

def set_predicate_regress_lambda(lambda_exp):
	global_context.PREDICATE_LAMBDA_REGRESS = lambda_exp




def set_axiom(axiom_name, feature, var_list, formula):
	if var_list!=[]:
		var_list = [r'\b'+mvar+r'\b' for mvar in var_list]
		global_context.AXIOMS[axiom_name][feature] = lambda x: Util.repeat_do_function(Util.sub_lambda_exp, zip(var_list,x),formula)
	else:
		global_context.AXIOMS[axiom_name][feature] = formula
	# for stota
	#global_context.AXIOMS_STR[axiom_name][feature] = (axiom_name, feature, var_list, formula)


def find_axiom_with_feature(axiom_name, feature):
	axioms_features = global_context.AXIOMS[axiom_name].keys()
	for feature_pattern in axioms_features:
		match = feature_pattern.match(feature)
		if match:
			return global_context.AXIOMS[axiom_name][feature_pattern], match.groups()

	error_msg = "#ERROR:find_axiom_with_feature: can not find %s with %s in %s" %(feature, axiom_name, global_context.FEATURE_LIST)
	raise Exception(error_msg)


def add_effects(e_tuple):
	global_context.EFFECTS.append(e_tuple)


def get_effects():
	return global_context.EFFECTS

	

