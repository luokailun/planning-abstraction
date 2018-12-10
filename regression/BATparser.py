#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-12-14 20:56:19
# @Author  : Kailun Luo (luokl3@mail2.sysu.edu.cn)
# @Link    : https://sdcs.sysu.edu.cn
# @Version : $Id$

 
import os
import re
from operator import itemgetter #itemgetter用来去dict中的key，省去了使用lambda函数
from itertools import groupby #itertool还包含有其他很多函数，比如将多个list联合起来。。

import Util
import context_operator

import  mylog as logging
logger = logging.getLogger(__name__)
#print rename(s)

######################
## Input:
## Output:
## Description:
##


  
const_pattern_str = r"(?:[a-z\d][\w]*)"    
var_pattern_str = r"(?:[A-Z][A-Z\d]*)"
name_pattern_str = r"\s*(?P<name>"+ const_pattern_str+"|"+var_pattern_str+")"
name_pattern = re.compile(name_pattern_str)
var_pattern= re.compile(var_pattern_str)

addsort_pattern_str = r"(?P<head>(?:forall|exists))\((?P<var>[\w\:\s\d,]+?)\)(?P<body>\[[^\[\]]+\])"
addsort_pattern  = re.compile(addsort_pattern_str)

    
def isVar(mstr):
	match = var_pattern.match(mstr)
	return True if match else False

######################
###### NOTICE
######################
#f(X) =Y , X,Y can be variable or constant 
#f(X) = k(Y) can be changed, for example:
#contains(P) = volunn(P), take(P',P) <=> contains(P)+ contains(P')> volunn(P) can be rewirte as
#contains(P) = Y, take(P',P) <=> Y=volunn(P) and  contains(P)+ contains(P')> volunn(P)

def __parse_Basic(*tuples):
	logger.info(tuples)

def __parse_Win(*tuples):
	for mtuple in tuples:
	#'numStone=Y, take(P,X)' -> [numStone=Y, take(P,X)]
		formula = mtuple[2]
		name_list, feature_list, var_list = __get_features_vars(mtuple[1])
		#print name_list, feature_list, var_list
		feature = __generate_feature_pattern(feature_list, var_list)
		context_operator.set_axiom("win",feature, var_list, formula)
		#print feature

	logger.info(tuples)


def __parse_End(*tuples):
	logger.info(tuples)
	for mtuple in tuples:
		formula = mtuple[2]
		context_operator.set_axiom("end","",[], formula)


def __parse_Init(*tuples):
	logger.info(tuples)
	formulas = list()
	for mtuple in tuples:
		formulas.append(mtuple[2])
	context_operator.set_axiom("init", "" , [], " and ".join(formulas))


def __parse_Poss(*tuples): #(('Poss', 'take(P,X)', ' num_stone>=X and (X=1 or X=2 or X=3)       and turn(P)    '),)
	logger.info(tuples)
	for mtuple in tuples:
		#'numStone=Y, take(P,X)' -> [numStone=Y, take(P,X)]
		formula = mtuple[2]
		#print '----',mtuple[1]
		name_list, feature_list, var_list = __get_features_vars(mtuple[1])
		feature = __generate_feature_pattern(feature_list, var_list)
		context_operator.add_actions([name for name in name_list if name.strip()!="pi"])
		#print '-------',feature, name_list, feature_list, var_list
		context_operator.set_axiom("poss",feature, var_list, formula)



def __parse_SSA(*tuples):
	logger.info(tuples)
	'''
	divide_pattern_str = r"(?P<fun>[\w]+)(?P<para>(?:\(.*?\))?)\s*(?:=\s*(?P<value>(?:"+var_pattern_str+"|"+const_pattern_str+")))?"# (?:" + const_pattern_str +"|"+ var_pattern_str+ "))?,"
	divide_pattern = re.compile(divide_pattern_str)
	for mtuple in tuples:
		match = re.match(divide_pattern,mtuple[2])
		print match
	'''
	#generate ssa[key]
	for mtuple in tuples:
		#'numStone=Y, take(P,X)' -> [numStone=Y, take(P,X)]

		formula = mtuple[2]
		'''
		for function in functions:
			if function.split('=')[0].find('(')==-1: # it's f = X or f or f = g(Y) where f is zero-para function
				matched = name_pattern.match(function)
				if matched.group():
					context_operator.add_zero_fluent(matched.group())     #add to const set()
					function = function.replace(matched.group(),matched.group()+"()",1) # change f -> f()
				else:
					print "#EOROR(__parse_SSA|Poss): name eror when parsing function: ",function
			fun_name, fun_para, fun_value = Util.parse_function(function)
			#get vars from para and values
			var_list+= [mvar.strip() for mvar in Util.get_paras_from_str(fun_para)+[fun_value] if isVar(mvar.strip()) ] 
			#generate feature
			feature_list.append(Util.generate_function_feature(function))
		'''
		#print var_list
		name_list, feature_list, var_list = __get_features_vars(mtuple[1])
		#print name_list, feature_list, var_list
		feature_pattern = __generate_feature_pattern(feature_list, var_list)
		actions = [name for e, name in enumerate(name_list) if e % 2 ==1  and name.strip()!="pi"]
		fluents = [name for e, name in enumerate(name_list) if e % 2 == 0 ]
		context_operator.add_actions(actions)
		context_operator.add_fluents(fluents)

		__new_add_effects(fluents[0], actions[0])
		#print feature
		context_operator.set_axiom("ssa", feature_pattern, var_list, formula)
		#print formula
		#print context_operator.get_axioms()['ssa'][feature](['b','c','d'])


def __get_features_vars(m_str):
	#print '1111',m_str
	feature_list = list()
	var_list = list()
	names_list = list()
	functions = Util.get_paras_from_str(m_str)
	for function in functions:
		fun_name, fun_para, fun_value = Util.parse_function(function)
		var_list+= [mvar.strip() for mvar in Util.get_paras_from_str(fun_para)+[fun_value] if isVar(mvar.strip()) ] 
		feature_list.append(Util.generate_function_feature(function))
		names_list.append(fun_name)
	return names_list, feature_list, var_list


def __generate_feature_pattern(feature_list, var_list):
	#print feature_list, var_list
	feature = '_'.join(feature_list)
	replace_pattern_list = ['_'+mvar+'_' for mvar in var_list]
	#print replace_pattern_list
	replace_pattern_list = zip(replace_pattern_list, ['_(.+?)_']*(len(replace_pattern_list)))
	#print replace_pattern_list
	feature = Util.repeat_do_function(Util.replace_lambda_exp, replace_pattern_list, feature).replace("pi_","")
	#print "--feature for pattern--",feature,feature.replace("pi_","")
	context_operator.add_feature(feature)
	return re.compile(feature)  #handle pi(A) which means A is variable

		

m = (('SSA', 'numStone(m) =Y , take(P,X)', '     Y = numStone -X    '),)
#__parse_SSA(m)
#print __parse

#################################################################################################################

#####################
# input:  <>|<action>|<fluent,action>
# output:   a list of constant_functions,  a list of variables
# description:  constant_functions occur in input, and variables in input
#

def __pre_parse_functions(functions_str):
	#print functions_str
	if functions_str.strip() =="":
		return [],[]
	#print 'functions_str----',functions_str
	functions = Util.get_paras_from_str(functions_str)
	#print 'paras: ----', functions
	zero_fluents = list()
	var_list = list()
	#function_names = list()
	for function in functions:
		if function.split('=')[0].find('(')==-1: # it's f = X or f or f = g(Y) where f is zero-para function
			matched = name_pattern.match(function)
			if matched:
				#context_operator.add_zero_fluent(matched.group())     #add to const set()
				zero_fluents.append(matched.group().strip())
				function = function.replace(matched.group(),matched.group()+"()",1) # change f -> f()
			else:
				logger.info("#EOROR(__parse_SSA|Poss): name error when parsing function: %s"%function)
		fun_name, fun_para, fun_value = Util.parse_function(function)
		#get vars from para and values
		var_list+= [mvar.strip() for mvar in Util.get_paras_from_str(fun_para)+[fun_value] if isVar(mvar.strip()) ] 
		#function_names.append(fun_name)
	#print 'zeorfun---',zero_fluents,var_list
	return zero_fluents, var_list


######################
## Input: a list of rule tuple (axiom_name, <>|<action>|<fluent,action>, formula )
## Output: a list of rule tuple (axiom_name, <>|<action>|<fluent,action>, formula )
## Description: (1) constant functions/relation will be complemented, e.g., fun -> fun()
##				
##			    
	
def __handle_zero_fluents(rule_list, zero_fluents):
	old_strs = [r'\b'+str(fluent)+r'\b' for fluent in zero_fluents]
	replaces = [fluent+'()' for fluent in zero_fluents]
	#print rule_list, zero_fluents
	for e, rule in enumerate(rule_list):
		#print rule
		functions = Util.repeat_do_function(Util.sub_lambda_exp, zip(zero_fluents,replaces),rule[1])
		formula = Util.repeat_do_function(Util.sub_lambda_exp, zip(zero_fluents,replaces),rule[2])
		rule_list[e] = (rule[0], functions, formula)

	return rule_list 



######################
## Input: a list of rule tuple (axiom_name, <>|<action>|<fluent,action>, formula )
## Output: a list of rule tuple (axiom_name, <>|<action>|<fluent,action>, formula ), a list of constants function/relation
## Description: (1) variables will be renamed
##				(2) a list of constants function/relation will be extracted
##			    
##
##	

def __rename(rule_list):
	#rename free varable
	zerofluent_rename_pair_list = [ __pre_parse_functions(rule[1]) for rule in rule_list]

	zero_fluents = list(set(sum([elem[0] for elem in zerofluent_rename_pair_list],[])))
	rename_vars = [elem[1] for elem in zerofluent_rename_pair_list]
	for e, rename_var_list in enumerate(rename_vars):
		#print "rename##########:", rename_var_list
		new_var_list = [context_operator.get_new_var() for i in rename_var_list]
		#print "new_var#########",new_var_list 
		rename_var_list = [r'\b' + elem + r'\b' for elem in rename_var_list]
		temp_rule =Util.repeat_do_function(Util.sub_lambda_exp, zip(rename_var_list,new_var_list),rule_list[e][1]+"&"+rule_list[e][2])
		#print "temp_rule ~~~~~~~~>:", temp_rule
		#print Util.rename_forall(temp_rule.split('&')[1])
		rule_list[e] = (rule_list[e][0], temp_rule.split('&')[0], Util.rename_forall(temp_rule.split('&')[1]))
	return rule_list, zero_fluents
	




######################
## Input: list of rule tuple (axiom_name, <>|<action>|<fluent,action>, formula )
## Output: list of rule tuple (axiom_name, <>|<action>|<fluent,action>, formula )
## Description: (1) variables will be renamed
##				(2) constant functions/relation will be complemented, e.g., fun -> fun()
##			    (3) constant functions/relations will be stored into global context
##
##	

def __pre_parse(rule_list):
	
	#[context_operator.add_zero_fluent(zero_fluent) for zero_fluent in zero_fluents ]
	#print zero_fluents, rename_vars
	rule_list, zero_fluents = __rename(rule_list)
	
	rule_list = __handle_zero_fluents(rule_list, zero_fluents)
	context_operator.set_zero_fluent(zero_fluents)

	return rule_list


#################################################################################################################



def parser(filename):
	with open(filename,"r") as sc_file:
		full_txt = " ".join(sc_file.readlines()).replace("\n"," ").replace("\t"," ")+";"
		#logger.debug(full_txt)
		pattern_sc_one = re.compile(r"(?<=(Poss\b|Init\b))\((.*?)\)\s*<=>(.+?)(?=Poss\b|SSA\b|Init\b|End\b|Win\b|;|Basic\b)")
		pattern_sc_two = re.compile(r"(?<=(Win\b|SSA\b|End\b))\((.*?)\)\s*<=>(.+?)(?=Poss\b|SSA\b|Init\b|End\b|Win\b|;|Basic\b)")
		pattern_sc_thr = re.compile(r"(?<=(Basic\b))\((.* ?)\)\s*<=>(.+?)(?=Poss\b|SSA\b|Init\b|End\b|Win\b|;|Basic\b)")

		rule_list = pattern_sc_one.findall(full_txt)+pattern_sc_two.findall(full_txt)+pattern_sc_thr.findall(full_txt)
		rule_list = __pre_parse(rule_list)

		for k, g in groupby(sorted(rule_list, key=itemgetter(0)), key=itemgetter(0)):
			m_group = list(g)
		 	#print "-------",k, m_group
			#eval("apply(__parse_" + k + "," + str(m_group) + ")")
			eval("__parse_" + k + "(*" + str(m_group) + ")")


		predicates  = __get_predicates_from_rules(rule_list)
		context_operator.add_predicates(predicates)

		para_num_dict  = __generate_functions_para_num(rule_list)

		#print predicates, context_operator.get_fluents(), predicate_sorts
		fun_fluents = [fluent for fluent in  context_operator.get_fluents() if fluent not in predicates]
		context_operator.add_nregx_function_patterns(__generate_nregx_function_patterns(fun_fluents))
		#print z3_header
		context_operator.set_function_regress_lambda(__generate_fun_regress_lambda(fun_fluents, para_num_dict))
		context_operator.set_predicate_regress_lambda(__generate_pred_regress_lambda(predicates, para_num_dict))

		#print("predicate: %s"%(context_operator.get_predicates()))
		#print("funtional_fluent: %s"%(fun_fluents))
		#print(__generate_fun_regress_lambda(fun_fluents, para_num_dict))
		#exit(0)
    		
#eval("apply(__parse_Init,[('Init', '', ' numStone >0  '), ('Init', '', ' turn(p1) and !turn(p2)    ')])")
#exit(0)



fluent_pattern_lambda_exp = lambda x: r"(?:"+ "|".join(x)+ ")\s*=\s*"+Util.notlogic_pattern_str 
predicate_pattern_lambda_exp = lambda x: r"(?:"+ "|".join(x)+ ")"


nregxfun_pattern_str_pre = r""+'(?P<pre>.?)\s*(?P<fun>'
nregxfun_pattern_str_pos = '\([^\(\)]*\))\s*(?P<pos>=>|.)' 


def __generate_functions_para_num(rule_list):
	functions_str_list = [Util.get_paras_from_str(rule[1]) for rule in rule_list if rule[0]=="SSA"]
	fluent_str_list = [  functions[0] for functions in functions_str_list]
	name_para_value_list = [Util.parse_function(function) for function in fluent_str_list]
	return {name:len([ elem for elem in para.split(',') if elem.strip()!="" ]) for name, para, value in name_para_value_list}


def __get_predicates_from_rules(rule_list):
	functions_str_list = [Util.get_paras_from_str(rule[1]) for rule in rule_list if rule[0]=="SSA"]
	fluent_str_list = [  functions[0] for functions in functions_str_list if functions[0]!="" ]

	name_para_value_list = [Util.parse_function(function) for function in fluent_str_list] 
	predicates = [name for name, para, value in name_para_value_list if value == ""]
	return predicates


def __generate_predicates(fluent_list, symbols):
	return [fluent for fluent in fluent_list if fluent not in symbols]


def __generate_nregx_function_patterns(fluents):
	nregxfun_pattern_str_list = [nregxfun_pattern_str_pre+ fun+ nregxfun_pattern_str_pos for fun in fluents]
	#print nregxfun_pattern_str_list
	nreg_fluent_pattern_list = [re.compile(pattern_str) for pattern_str in nregxfun_pattern_str_list ]
	return nreg_fluent_pattern_list

def __generate_fun_regress_lambda(functions, para_num_dict):
	#print [fluent+"\("+','.join(["(.*?)"]*(len(function_sorts[fluent])-1))+"\)" for fluent in functions ]
	if functions!=[]:
		return re.compile(fluent_pattern_lambda_exp([fluent+"\("+','.join(["(.*?)"]*para_num_dict[fluent])+"\)" for fluent in functions ]))
	else:
		return None

def __generate_pred_regress_lambda(predicates, para_num_dict):
	#print [predicate+"\("+','.join(["(.*?)"]*len(function_sorts[predicate]))+"\)" for predicate in predicates ]
	if predicates!=[]:
		return re.compile(predicate_pattern_lambda_exp([predicate+"\("+','.join(["(.*?)"]*para_num_dict[predicate])+"\)" for predicate in predicates ]))
	else:
		return None


def __new_add_effects(fluent, action):
	context_operator.add_effects((fluent.strip(), action.strip()))

#parser("./takeaway.sc")
#print "-----",context_operator.get_axioms()['init']

 #(Poss\(|SSA\(|Init\(|End\(|Win\()

#parser("./planning_domains/1d.sc")

