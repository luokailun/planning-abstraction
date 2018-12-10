#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-12-22 21:21:22
# @Author  : Kailun Luo (luokl3@mail2.sysu.edu.cn)
# @Link    : https://sdcs.sysu.edu.cn
# @Version : $Id$
  
import os
import Util
import re
import base64
import context_operator

import mylog as logging
logger = logging.getLogger(__name__)


'''

def context_operator.get_formula_from_local_dict():
	formula_str=' and '.join([str( key )+"="+str(value) for key, value in context_operator.get_local_dict().iteritems()])
	return 'exists('+ ','.join(get_local_dict().values())+ ')[ '+ formula_str+' ]'

def context_operator.use_local_dict():
	global_list.LOCAL_DICT = dict()

def context_operator.get_local_dict():
	return global_list.LOCAL_DICT

def context_operator.get_new_var():
	global_list.VAR_INDEX += 1
	return 'K'+ str(global_list.VAR_INDEX)

def context_operator.get_global_action():
	return global_list.ACTION#'take(1,a,f(x)+3)'
def set_global_action(action):
	global_list.ACTION = action
'''

############
#	regress(formula,action): 
#	(1) replace forall(x)[f(g(x)) > x+1] with  forall(x)[ exist(k,m).k=g(x) and m= f(k) and m >x+1]
#	(2) for each fluent in formula, do regress(fluent, action)
#
#
#
#
#
#
#
#
#

encode_pair_forall = (['[',']'],['{','}'])

forall_pattern_str = r"(?P<head>(?:forall|exists)\([\w\s\d,:]+?\))\[(?P<body>[^\[\]]*)\]"      #depth 0 patter
#s="abc or forall(x,y,z11)[forall(x)[abc] and a+b and exists(y)[abc]] and abc exists(y)[abc]"
forall_pattern =re.compile(forall_pattern_str)

exp_pattern_str = r"(?:(?:\d|[A-Z]|[\+\-\*\|\(\)\s])*)"
const_pattern_str = r"(?:[a-z][a-z\d]*)"    
var_pattern_str = r"(?:[A-Z][A-Z\d]*)"

#important rules: notlogic_pattern_str
notlogic_pattern_str = r"(?:(?:(?<!and)(?<!or).(?!and)(?!or))+)"

#@fluent_pattern_lambda_exp = lambda x: r"(?:"+ "|".join(x)+ ")\s*=\s*"+notlogic_pattern_str  


#s="abc or forall(x,y,z11)[forall(x)[abc] and a+b and exists(y)[abc]] and abc exists(y)[abc] and forall(x)[f(g(x)) > x+1]"
#s = forall_pattern.sub(_mrepl_forall,s)
#print s.replace('\n','')



fluents = {'f':3, 'g': 2,'m':0,'k':1}

# pos !='=' or pre in ['+','-','*','/','|']
s='forall(x)[ f(g(x),g(x-1),g((1+x)*2)) > x+1+ g(x ) and  f(x,y,z) =1+3 and m() = k(x) and and f(x,y,z+1-1) < 5 and 1+f(x,g(y),z) =1 and m() >1+(1-x)]'
#print s
#fluent_pattern_str = r""+'(?P<pre>.)(?P<fun>\s*g\([^\(\)]+\))\s*(?P<pos>.)'
#fluent_pattern = re.compile(fluent_pattern_str)
#@nregxfun_pattern_str_pre = r""+'(?P<pre>.)\s*(?P<fun>' #r""+'\s*(?P<fun>'  
#nregxfun_pattern_str_pre = r""+'(?P<pre>.)\s*(?P<fun>' #r""+'\s*(?P<fun>'  
#nregxfun_pattern_str_pos = '\([^\(\)]+\)|'
#nregxfun_pattern_str_add = ')\s*(?P<pos>.)' #'\([^\(\)]+\))' #\([^\(\)]+\))\s*(?P<pos>.)'
#@nregxfun_pattern_str_pos = '\([^\(\)]*\))\s*(?P<pos>.)' #'\([^\(\)]+\))' #\([^\(\)]+\))\s*(?P<pos>.)'
#@nregxfun_pattern_str_list = [nregxfun_pattern_str_pre+ fun+ nregxfun_pattern_str_pos for fun in fluents.keys()]
#@nreg_fluent_pattern_list = [re.compile(pattern_str) for pattern_str in nregxfun_pattern_str_list ]


#exists(K1,K2,K5,K4,K7,K3,K6)[ g(x)=K1 and g(y)=K2 and f(x,K2,z)=K5 and f(x,y,z+1-1)=K4 and f(K1,K3,K6)=K7 and g(x-1)=K3 and g((1+x)*2)=K6 ] and forall(x)[ K7 > x+1+ K1 and  f(x,y,z) =1+3 and K4 < 5 and 1+ K5 =1 m >1+(1-x)]

#s= Util.repeat_replace_inner_with_pattern(fluent_pattern, mrepl, s)
#print fluent_pattern.findall(s)

def __mrepl_encode(matched):
	match_str=matched.group()
	encoded_str=Util.endecode_string(match_str, Util.encode_pair[0], Util.encode_pair[1])
	return encoded_str


def __equality(symbol):
	if symbol[0] =="=" and len(symbol)==1:
		return True
	else:
		return False


def __mrepl_detect_fluent(matched):
	#print "hello",matched.groups()
	if not __equality(matched.group('pos')) or matched.group('pre') in ['+','-','*','/','|']:
		fluent = matched.group('fun').replace(' ','').replace('[','(').replace(']',')') #decode
		#print 'fluent--', fluent
		if fluent not in context_operator.get_local_dict().keys():
			context_operator.get_local_dict()[fluent] = context_operator.get_new_var()
		#print "replace--",matched.group('pre')+' '+context_operator.get_local_dict()[fluent]+' '+matched.group('pos')
		return matched.group('pre')+' '+context_operator.get_local_dict()[fluent]+' '+matched.group('pos')
	else:
		return matched.group()


def __normalize_fluents(encoded_str):
	encoded_str = " "+encoded_str+" " # in order to detect fun_pre and fun_pos (sometimes fails)
	new_encoded_str = encoded_str
	while True:
		#for nreg_fluent_pattern in nreg_fluent_pattern_list:
		for nreg_fluent_pattern in context_operator.get_nregx_function_patterns():
			new_encoded_str = Util.repeat_replace_inner_with_pattern(nreg_fluent_pattern, __mrepl_detect_fluent, encoded_str)
			encoded_str = new_encoded_str
			#print '---',encoded_str 
		if new_encoded_str == encoded_str:
			new_encoded_str = re.sub(Util.parenth_pattern, __mrepl_encode, encoded_str)
			#print "replace () -> []", new_encoded_str
			if encoded_str == new_encoded_str:
				break
		encoded_str = new_encoded_str
	return Util.endecode_string(encoded_str, Util.encode_pair[1], Util.encode_pair[0]).strip()

# forall(x)[ f(g(x), g(x-1)) > x+1+ g(x)] -> forall(x){ f(g(x),g(x-1),g((1+x)*2)) > x+1+g(x)}
#  f(g(x),g(x-1))=k and k > x+1+ g(x). =>  g(x)=k1 and g(x-1)=k2 and f(k1,k2)=k and k > x+1+ k1

# forall(x){ f(g(x),g(x-1),g((1+x)*2)) > x+1+g(x)}

def __mrepl_handle_forall(matched):
	context_operator.use_local_dict()   # a dict to store { fluent: var}
	encoded_str = Util.endecode_string(matched.group(), encode_pair_forall[0],encode_pair_forall[1])
	body_str = matched.group('body')
	#print "body", body_str
	normal_str = __normalize_fluents(body_str)
	#print "normal", normal_str
	add_formula = context_operator.get_formula_from_local_dict()
	#--(***)---return matched.group('head')+ '{'+ add_formula+' and '+normal_str+ '}' if add_formula!="" else encoded_str
	#print matched.group()
	#exit(0)
	return "%s{ %s and (%s)} }"% (matched.group('head'), add_formula, normal_str) if add_formula!="" else encoded_str



#forall(x)[f(g(x)) > x+1  ->  forall(x)[ exist(k,m).k=g(x) and m= f(k) and m >x+1]

#s = "1<=len() and (forall(G0:Int)[!(1<G0)] and forall(G0:Int,G0:Int)[!(row(G0)<G0)] and forall(G0:Int)[G0<=2] and forall(G0:Int)[G0<=len()])" 
def __normalize_formula(formula):
	encoded_normal_str = Util.repeat_replace_inner_with_pattern(forall_pattern, __mrepl_handle_forall, formula)
	context_operator.use_local_dict() 
	encoded_normal_str = __normalize_fluents(encoded_normal_str)
	
	add_formula = context_operator.get_formula_from_local_dict()
	#add_formula = Util.endecode_string(add_formula, Util.encode_pair[1], Util.encode_pair[0])
	#--(***)---
	encoded_normal_str = add_formula+ " and ( " + encoded_normal_str + ")}" if add_formula!="" else encoded_normal_str

	normal_str = Util.endecode_string(encoded_normal_str,encode_pair_forall[1],encode_pair_forall[0])
	return normal_str



#exit(0)




#fluents = {'f':3, 'g': 2}
#fluents = ["g\(.*?\)","f\(.*?,.*?,.*?\)","m\(.*?\)"]
#fluent_set = set(f:3)
# 'f\(.+?,.+?,.+?\)\s*=\s*'+exp
#my_s = "exists(K1,K2,K5,K4,K7,K3,K6)[ g(x)=abc(1) and g(y) = K2+1 and f(x,K2,z)= K5 and m() = (N + 3) and f(x,y,z+1-1)=K4 and (f(K1,K3,K6)=K7 and g(x-1)=K3 and g((1+x)*2)=K6+(2*2)) ] and forall(x)[ K7 > x+(1+ K1) and  f(x,y,z) =1+3 and K4 < 5 and 1+ K5 =1 ]"
#fluent_pattern_lambda_exp = lambda x: r"(?:"+ "|".join(x)+ ")\s*=\s*(?:"+const_pattern_str+"|"+exp_pattern_str+")"      
    
#['g(x)=abc', 'g(y)=K2', 'g(x-1)=K3', 'g((1+x)*2)=K6']


def encode_handle_fluent(matched_str):
	bytesString = matched_str.encode(encoding="utf-8")
	return '@'+base64.encodestring(bytesString).decode()+'@'


def __mrepl_decode_fluent(matched):
	bytesString = matched.group('code').encode(encoding="utf-8")
	return base64.decodestring(bytesString).decode()


def decode_handle_fluent(m_str):
	m_str = m_str.replace('\n','')
	return re.sub(r"@(?P<code>.+?)@", __mrepl_decode_fluent, m_str) 


def poss_or_ssa(action_str, fluent=None, model=None):
	#print("aaaaa",action_str)
	'''
	#take(1,X,fun(1,2)) -> take   1,X,fun(1,2)
	action_name, action_args_str, nothing= parse_function(action_str)
	#print action_name, action_args_str
	# 1,X,fun(1,2) ->  1,X,fun[1_2] -> ['1', 'X', 'fun[1_2]'] -> ['1', 'X', 'fun[1_2]'] -> ['1','X','fun(1,2)']
	para_list = get_paras_from_str(action_args_str)
	#['1','X','fun(1,2)'] -> take_1_X_fun(1,2)
	action_feature = action_name + '_' + '_'.join(para_list)
	action_feature = re.sub(r'\s+', '', action_feature)
	print action_feature
	'''
	#print 'action_str,fluent', action_str, fluent
	axiom_name = "poss"
	feature =  Util.generate_function_feature(action_str)
	#take_1_X_fun(1,2) -> function to handle this function, parameters ['X', 'fun(1,2)']
	#print('feature', feature)
	#print('fluent', fluent)
	if fluent:
		feature = Util.generate_function_feature(fluent)+'_'+feature
		axiom_name = "ssa"
	#print feature
	lambda_function, para_selected_list= context_operator.find_axiom_with_feature(axiom_name, feature)
	#print '----', lambda_function, para_selected_list
	formula = lambda_function if  isinstance(lambda_function, str) else lambda_function(para_selected_list)
	if model:
		#ground_formula = __grounding_forall(formula)
		#print ground_formula
		#print __replace_model(ground_formula, model)
		return model_sat_formula(model, formula)#eval(__replace_model(ground_formula, model))
	else:
		return formula


def __mrepl_fluent_regress(matched):
	fluent_str =matched.group()
	
	match_fluent_str = Util.eliminate_unmatched(fluent_str).strip()
	
	#handle regression:#########
	action_str = context_operator.get_global_action()

	if __uneffect(match_fluent_str, action_str):
		return matched.group()

	#regress_str = get_ssa(fluent_str,action_str)
	#regress_str = context_operator.get_axioms()['ssa']
	#print action_str, match_fluent_str
	regress_str = poss_or_ssa(action_str, match_fluent_str)
	regress_str = "(%s)"%regress_str
	logger.debug("#regress fluent: %s, after regress %s" %(match_fluent_str,regress_str))
	##########
	encoded_fluent_str = encode_handle_fluent(regress_str)
	new_str =  fluent_str.replace(match_fluent_str, encoded_fluent_str)
	return new_str
#print fluent_pattern_lambda_exp(fluents)

'''
fluent_pattern = re.compile(fluent_pattern_lambda_exp(fluents))
my_s = fluent_pattern.sub(__mrepl_fluent_regress, my_s)
print "---hello---\n",decode_handle_fluent(my_s)
'''

def __regress(formula, action):
	#'take(1,a,f(x)+3)'

	context_operator.set_global_action(action)
	#formula = __normalize_formula(formula)
	#fluent_pattern = re.compile(fluent_pattern_lambda_exp(fluents))
	#predicate_pattern = re.compile(fluent_pattern_lambda_exp(predicates))
	fluent_pattern = context_operator.get_function_regress_lambda()
	#print('pattern', fluent_pattern)
	#print(context_operator.get_fluents())
	predicate_pattern = context_operator.get_predicate_regress_lambda()
	if fluent_pattern:
		formula = fluent_pattern.sub(__mrepl_fluent_regress, formula)
	#logger.debug('#formula after fluent replace: %s' %formula)
	if predicate_pattern:
		formula = predicate_pattern.sub(__mrepl_fluent_regress, formula)
	#logger.debug('#formula after predicate replace: %s' %formula)
	#print "------\n",decode_handle_fluent(formula)
	return decode_handle_fluent(formula)


def regress(formula, action):
	logger.debug("#before normalization, formula: %s, action: %s" %(formula, action))
	formula = __normalize_formula(formula)
	logger.debug("#after normalization formula: %s" %(formula))
	return __regress(formula,action)


##########################################################################################################################################

name_pattern_str = r"[\w\d]+"
name_pattern = re.compile(name_pattern_str)

def __uneffect(fluent_str, action_str):
	fluent_name = name_pattern.match(fluent_str.strip()).group()
	action_name = name_pattern.match(action_str.strip()).group()
	if (fluent_name, action_name) in context_operator.get_effects():
		return False
	else:
		return True

#context_operator.set_global_action("take(1)")
'''
import my_parser
my_parser.parser("takeaway.sc")
#print regress("forall(X)[numStone() > X] or forall(X,Y)[numStone() + X =Y ] and numStone()>0 and turn(p2)","take(p2,3)")
print regress("forall(X:Int)[numStone() > X] or forall(X:Int,Y:Int)[numStone() + X =Y ] and numStone()>0 and turn(p2)","take(p2,3)")
'''

#l= ['X','Y']
#print context_operator.get_symbol_sorts_dict()[('take',l.index("X")+1)]


