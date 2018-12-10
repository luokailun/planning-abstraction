
import json
from regression import BATparser
from regression import context_operator
import constructor
import pattern_match
import re



def load_mapping_from_file(filename):
	with open(filename,"r") as fp_mp:
		mapping = json.load(fp_mp)
		 #dict(hello)['starting_state']\
		return mapping



def __has_effect(program, formula):
	#print(program, formula)

	effect_pairs = context_operator.get_effects()
	fluents = context_operator.get_fluents()
	actions = context_operator.get_actions()
	reg_fluents = [r'\b' + elem + r'\b' for elem in fluents]
	reg_actions = [r'\b' + elem + r'\b' for elem in actions]

	in_fluents = [f for e, f in enumerate(fluents) if re.search(reg_fluents[e], program) or re.search(reg_fluents[e], formula)]
	in_actions = [a for e, a in enumerate(actions) if re.search(reg_actions[e], program)]

	#print(in_fluents, in_actions)
	#print(effect_pairs)
	elems = [ (f, a) for a in in_actions for f in in_fluents]
	for elem in elems:
		if elem in effect_pairs:
			return True
	return False


def __get_high_level_poss_from_mapping(action_mapping):
	return [ (action, constructor.generate_executable(program)) for action, program in action_mapping.items()]


def __get_high_level_ssa_from_mapping(action_mapping, fluent_mapping):
	rename_pairs = [ pattern_match.rename(fluent,formula) for fluent, formula in fluent_mapping.items()]
	fluent_mapping = { fluent: formula for fluent, formula in rename_pairs}
	#print("\n\n\n")
	effected_pairs = [ (action, program, fluent, formula) for action, program in action_mapping.items() for fluent, formula in fluent_mapping.items() if __has_effect(program, formula) ]
	
	#print(fluent_mapping)
	#print(effected_pairs)
	#exit(0)

	return [ (fluent, action, constructor.generate_ssa(formula, program)) for action, program, fluent, formula in effected_pairs ]


def construct_high_level_theory_from_mapping(m_mapping):

	action_mapping = m_mapping['action']
	fluent_mapping = m_mapping['fluent']

	new_poss_axioms = __get_high_level_poss_from_mapping(action_mapping)
	new_ssa_axioms = __get_high_level_ssa_from_mapping(action_mapping, fluent_mapping)


	poss_axioms = [ "Poss(%s)<=>%s"%(action, poss) for action, poss in new_poss_axioms]
   	ssa_axioms = [  "SSA(%s,%s)<=>%s"%(fluent, action, ssa) for fluent, action, ssa  in new_ssa_axioms]
	return poss_axioms+ssa_axioms




#def construct_high_level_theory(domain_name):





#construct_high_level_theory("chomp2N", 'hello.txt')


