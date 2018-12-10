

import program_handler
from regression import regress

'''
def exec(my_object, formula, keyword, recall_fun):
	#print(keyword,my_object)
	#print('\n')
	if keyword == 'non_deterministric':
		return "(%s)"%' or '.join([ recall_fun(program, formula, fun) for program in my_object])

	elif keyword == 'sequential':

		for program in my_object:
			formula = recall_fun(program, formula, fun)

		return ' and '.join([ recall_fun(program, formula, fun) for program in my_object])

	elif keyword == 'pi_action':
		return 'exists(%s)'%(','.join(my_object))

	elif keyword == 'single':
		if my_object.find('?')==-1:
			return "(%s)"%regress.poss(my_object)
		else: 
			return "(%s)"%my_object.strip().strip('?')
'''


def A_regression(my_object, formula, keyword, recall_fun):

	if keyword == 'non_deterministric':
		program_list = my_object
		return ' and '.join([ recall_fun(program, formula, A_regression) for program in program_list])

	elif keyword == 'sequential':
		program_list = my_object
		program_list.reverse()
		for program in program_list:
			formula = recall_fun(program, formula, A_regression)
		return formula

	elif keyword == 'pi_action':
		variable_list = my_object 
		return 'forall(%s)'%(','.join(variable_list))

	elif keyword == 'single':
		action = my_object.strip()
		if action.find('?') ==-1:
			regress_formula =regress.regress(formula, action)
			#logger.info("formula: %s, action: %s , regress result: %s"%(formula, action, regress_formula))
			return "(%s => %s)" % (regress.poss_or_ssa(action),regress_formula )
		else:
			return "(%s => %s)" % (action.strip('?'), formula)



def E_regression(my_object, formula, keyword, recall_fun):

	#print(keyword,my_object)
	#print('\n')
	if keyword == 'non_deterministric':
		return "(%s)"%' or '.join([ recall_fun(program, formula, E_regression) for program in my_object])

	elif keyword == 'sequential':
		program_list = my_object
		program_list.reverse()
		for program in program_list:
			formula = recall_fun(program, formula, E_regression)
		return formula

	elif keyword == 'pi_action':
		variable_list = my_object 
		return 'exists(%s)'%(','.join(variable_list))

	elif keyword == 'single':
		action = my_object.strip()
		if action.find('?') ==-1:
			regress_formula =regress.regress(formula, action)
			#logger.info("formula: %s, action: %s , regress result: %s"%(formula, action, regress_formula))
			return "(%s) and (%s)" % (regress.poss_or_ssa(action), regress_formula)
		else:
			return "(%s) and (%s)" % (action.strip('?'), formula)


def E_star_regression(my_object, formula, keyword, recall_fun):

	#print(keyword,my_object)
	#print('\n')
	if keyword == 'non_deterministric':
		return "(%s)"%' or '.join([ recall_fun(program, formula, E_star_regression) for program in my_object])

	elif keyword == 'sequential':
		program_list = my_object
		program_list.reverse()
		for program in program_list:
			formula = recall_fun(program, formula, E_star_regression)
		return formula

	elif keyword == 'pi_action':
		variable_list = my_object 
		return 'exists(%s)'%(','.join(variable_list))

	elif keyword == 'single':
		action = my_object.strip()
		if action.find('?') ==-1:
			regress_formula =regress.regress(formula, action)
			#logger.info("formula: %s, action: %s , regress result: %s"%(formula, action, regress_formula))
			return "(%s)" % (regress_formula)
		else:
			return "(%s) and (%s)" % (action.strip('?'), formula)


def generate_executable(program):
	poss_axiom =  program_handler.handle_program(program, 'True', E_regression)
	print('------get---poss axiom: %s'%poss_axiom)
	return poss_axiom


def generate_ssa(formula, program):
	ssa_axiom = program_handler.handle_program(program, formula, A_regression)
	print('------get---ssa axiom: %s'%ssa_axiom)
	return ssa_axiom

