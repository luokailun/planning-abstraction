
import re
import pattern_match


def __find_non_determin_not_in_priority(program):
	new_program = pattern_match.encode_or_in_parathesis(program)
	new_program = pattern_match.encode_or_in_bracket(new_program)
	if new_program.find('|')==-1:
		return False
	else:
		return True

def __find_seq_not_in_priority(program):
	new_program = pattern_match.encode_and_in_parathesis(program)
	new_program = pattern_match.encode_and_in_bracket(new_program)
	if new_program.find(';')==-1:
		return False
	else:
		return True


def match_nondertm_action(program):
	if program.find('|')==-1:
		return False
	elif __find_non_determin_not_in_priority(program) is True:
		return True
	else:
		return False



def match_seq_action(program):
	if program.find(';') ==-1:
		return False
	elif __find_seq_not_in_priority(program) is True:
		return True
	else:
		return False



def match_parenthesis(program):
	mstr = program.strip()
	if mstr[0]=='(':
		return True
	else:
		return False


def match_pi_action(program):
	mstr = program.strip()
	if mstr[0]=='p' and mstr[1]=='i' and mstr[2]=='(':
		return True
	else:
		return False

#     a ; b ; (c | d) |  d; e
# test whether | exits
# find | not in ()




def handle_nondertm_action(program, formula, fun, recall_fun):
	new_program = pattern_match.encode_or_in_parathesis(program)
	new_program = pattern_match.encode_or_in_bracket(new_program)
	sub_programs = pattern_match.parse_non_deterministic(new_program)
	#first_part, remain_part = first_part.replace('@','|'), remain_part.replace('@', '|')
	return fun(sub_programs, formula,  'non_deterministric', recall_fun)



def handle_seq_action(program, formula, fun, recall_fun):
	new_program = pattern_match.encode_and_in_parathesis(program)
	new_program = pattern_match.encode_and_in_bracket(new_program)
	sub_programs = pattern_match.parse_sequential(new_program)
	#first_part, remain_part = first_part.replace('@','|'), remain_part.replace('@', '|')
	return fun(sub_programs, formula, 'sequential', recall_fun)



def handle_paranthesis(program, formula, fun, recall_fun):
	 strip_context = pattern_match.parse_parenthesis(program)
	 strip_context = pattern_match.decode_and_or(strip_context)
	 return "(%s)"%handle_program(strip_context, formula, fun)



def handle_pi_action(program, formula, fun, recall_fun):
	variables, body  = pattern_match.parse_pi_action(program)
	body = pattern_match.decode_and_or(body)
	return "%s[ %s ]"%(fun(variables.split(','), formula, 'pi_action', recall_fun), handle_program(body, formula, fun))



def handle_single_action(action, formula, fun, recall_fun):
	return fun(action, formula, 'single', recall_fun)




def handle_program(program, formula, fun):

	if match_nondertm_action(program) is True:
		#print('1\n')
		return handle_nondertm_action(program, formula, fun, handle_program)

	elif match_seq_action(program) is True:
		#print('2\n')
		return handle_seq_action(program, formula, fun, handle_program)

	elif match_parenthesis is True: 
		#print('3\n')
		return handle_parenthesis(program, formula, fun, handle_program)

	elif match_pi_action(program) is True:
		#print('4\n')
		return handle_pi_action(program, formula, fun, handle_program)
	else:
		return handle_single_action(program, formula, fun, handle_program)


'''
def fun(my_object, formula, keyword, recall_fun):
	#print(keyword,my_object)
	#print('\n')
	if keyword == 'non_deterministric':
		return ' or '.join([ recall_fun(program, formula, fun) for program in my_object])
	elif keyword == 'sequential':
		return ' and '.join([ recall_fun(program, formula, fun) for program in my_object])
	elif keyword == 'pi_action':
		return 'forall(%s)'%(','.join(my_object))
	elif keyword == 'single':
		#print(my_object)
		#print('end--')
		return my_object
'''


#p = "pi(T1,T2)[R=rtA and cnroad(rtA,O,D)?;takeroad(X,T1,O,loc1); takeroad(X,T2,loc1,D)] | pi(T1,T2)[R=rtB and cnroad(rtB,O,D)?;takeroad(X,T1,O,loc3); takeroad(X,T2,loc3,D)] | pi(T1,T2)[R=rtA and cnroad(rtA,O,D)?;takeroad(X,T1,O,loc4); takeroad(X,T2,loc4,D)] "
#handle_program(p, "", fun)



