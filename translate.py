import re

name = r'[a-z][a-z\d\-_]*'
var = r'\?' + name

namePattern = re.compile(name)
varPattern = re.compile(var)
actionPattern = re.compile(r':action ({})'.format(name))
parametersPattern = re.compile(r':parameters')
preconditionPattern = re.compile(r':precondition')
effectPattern = re.compile(r':effect')

def nextParen(s):
	'''return the content within the next parenthesis
	non-generator version of the function nextFormula'''
	np = 0
	start = []
	for i in range(len(s)):
		c = s[i]
		if c == '(':
			np += 1
			start.append(i+1)
		elif c == ')':
			np -= 1
			if np == 0:
				return s[start[0]:i]

def parse_formula(s):
	headObj = namePattern.search(s)
	if(headObj == None):
		return 'True'
	head = s[headObj.start():headObj.end()]
	body = s[headObj.end():]
	if head == 'and':
		return parse_and(body)
	elif head == 'or':
		return parse_or(body)
	elif head == 'not':
		return parse_not(body)
	elif head == 'imply':
		return parse_imply(body)
	elif head == 'exists':
		return parse_exists(body)
	elif head == 'forall':
		return parse_forall(body)
	else:
		return parse_atom(head, body)

def parse_atom(predicate, s):
	arguments = processVar(s)
	if len(arguments) > 0:
		return f'{predicate}(' + ','.join(arguments) + ')'
	else:
		return predicate

def parse_not(s):
	s = re.sub(r'[\(\)]', '', s)
	return f'!{parse_formula(s)}'

def parse_and(s):
	result = []
	for formula in nextFormula(s):
		result.append(parse_formula(formula))
		formula = nextFormula(s)
	return ' and '.join(result)

def parse_or(s):
	result = []
	for formula in nextFormula(s):
		result.append(parse_formula(formula))
		formula = nextFormula(s)
	return '(' + ' or '.join(result) + ')'

def parse_imply(s):
	p = []
	for formula in nextFormula(s):
		p.append(formula)
	return f'{parse_formula(p[0])} => {parse_formula(p[1])}'

def parse_forall(s):
	p = []
	for formula in nextFormula(s):
		p.append(formula)
	return 'forall(' + ','.join(processVar(p[0])) + f')[{parse_formula(p[1])}]'

def parse_exists(s):
	p = []
	for formula in nextFormula(s):
		p.append(formula)
	return 'exists(' + ','.join(processVar(p[0])) + f')[{parse_formula(p[1])}]'

def nextFormula(s):
	'''generator for next subformula in s'''
	np = 0
	start = []
	for i in range(len(s)):
		c = s[i]
		if c == '(':
			np += 1
			start.append(i+1)
		elif c == ')':
			np -= 1
			if np == 0:
				yield s[start[0]:i]
				np = 0
				start = []

def processVar(s):
	'''transform variables in pddl to suitalbe forms
	for regression part'''
	return re.sub(r'\?', '', re.sub(r'-\s*'+name, '' ,s)).upper().split()

class Parser:
	def __init__(self):
		self.actionName = '' # the name of the current action
		self.action_arguments = [] # arguments of the current action
		self.poss = []
		self.ssa = []
		self.second = '' # the second precondition of current effect fluent
		self.fluents = []
		self.fluent_arguments = []
		self.pos = dict() # store positive second preconditions for different fluents
		self.neg = dict()

	def preprocess(self, filename):
		'''preprocessing'''
		with open(filename, 'r') as f:
			# remove comments(all comments are single-line)
			# and transform all letters into lowercase(not case-sensitive)
			content = re.sub(r';.*$', '', f.read(), flags=re.MULTILINE).lower()
		return content

	def parse_domain(self, filename):
		content = self.preprocess(filename)
		action = actionPattern.search(content)
		while(action != None):
			self.actionName = action.group(1)
			parameters = parametersPattern.search(content, action.end())
			action_arguments = processVar(nextParen(content[parameters.end():]))
			self.action_arguments = action_arguments
			action_arguments_str = ','.join(action_arguments)
			precondition = preconditionPattern.search(content, parameters.end())
			if len(action_arguments) != 0:
				# if the action doesn't have arguments
				action_arguments_str = f'({action_arguments_str})'
			self.poss.append(f'Poss({action.group(1)}{action_arguments_str})' + 
					f' <=> {parse_formula(nextParen(content[precondition.end():]))}')
			effect = effectPattern.search(content, precondition.end())
			self.extract_ssa(nextParen(content[effect.end():]))
			self.generate_ssa()
			self.fluents, self.fluent_arguments, self.pos, self.neg = [], [], dict(), dict()
			action = actionPattern.search(content, effect.end())

	def extract_ssa(self, s):
		headObj = namePattern.search(s)
		if headObj == None:
			return 
		head = s[headObj.start():headObj.end()]
		body = s[headObj.end():]
		if head == 'and':
			for formula in nextFormula(body):
				self.extract_ssa(formula)
		elif head == 'not':
			self.process_not(body)
		elif head == 'when':
			self.process_when(body)
		elif head == 'forall':
			self.process_forall(body)
		else:
			self.process_atom(head, body)

	def process_atom(self, fluent, s):
		fluent_arguments = processVar(s)
		fluent = f'{fluent}('+ ','.join(fluent_arguments) +')'
		if fluent in self.fluents:
			self.pos[self.fluents.index(fluent)].append(self.second)
		else:
			self.pos[len(self.fluents)] = [self.second, ]
			self.neg[len(self.fluents)] = []
			self.fluents.append(fluent)
			self.fluent_arguments.append(fluent_arguments)	

	def process_not(self, s):
		s = re.sub(r'[\(\)]', '', s)
		temp = namePattern.search(s)
		fluent = temp[0]
		fluent_arguments = processVar(s[temp.end():])
		fluent = f'{fluent}('+ ','.join(fluent_arguments) +')'
		if fluent in self.fluents:
			self.neg[self.fluents.index(fluent)].append(self.second)
		else:
			self.pos[len(self.fluents)] = []
			self.neg[len(self.fluents)] = [self.second, ]
			self.fluents.append(fluent)
			self.fluent_arguments.append(fluent_arguments)	

	def process_forall(self, s):
		p = []
		for formula in nextFormula(s):
			p.append(formula)
		self.extract_ssa(p[1])

	def process_when(self, s):
		p = []
		for formula in nextFormula(s):
			p.append(formula)
		self.second = parse_formula(p[0])
		self.extract_ssa(p[1])
		self.second = ''

	def generate_ssa(self):
		'''generate ssa for each action'''
		for i, fluent in enumerate(self.fluents):
			# rename common action arguments
			common = set(self.fluent_arguments[i]).intersection(
				set(self.action_arguments))
			action_arguments = list(self.action_arguments)
			fluent_arguments = ','.join(self.fluent_arguments[i])
			rename = []
			num = 0 
			for j,a in enumerate(self.action_arguments):
				if a in common:
					num += 1
					action_arguments[j] = f'TEMP{num}'
					rename.append(f'TEMP{num}={a}')
			
			action_arguments_str = ','.join(action_arguments)
			if len(action_arguments) != 0:
				action_arguments_str = f'({action_arguments_str})'

			fp, fn = 0, 0
			if self.pos[i] != []:
				fp = 1  # there are positive effects
			if self.neg[i] != []:
				fn = 1  # there are negative effects
			pospart = ' or '.join(self.pos[i])
			negpart = ' or '.join(self.neg[i])
			rename = ' and '.join(rename)
			if len(rename) > 0:
				negrename = f'!({rename})'
			else:
				negrename = ''

			if len(pospart) > 0 and len(rename) > 0:
				pospart = f'({pospart}) and {rename}'
			elif fp and len(rename) > 0:
				pospart = rename
			if len(pospart) > 0:
				pospart = f'{pospart} or '
			elif fp == 1:
				pospart = 'True'
			else:
				pospart = 'False'

			if len(negpart) > 0 and len(negrename) > 0:
				negpart = f'(!({negpart}) or {negrename})'
			elif fn and len(negrename) > 0:
				negpart = negrename
			if len(negpart) > 0:
				negpart = f'{fluent} and {negpart}'
			elif fn == 1:
				negpart = 'False'
			else:
				negpart = f'{fluent}'
			# pos and neg part won't be false simultaneously
			if pospart == 'True':
				result = 'True' 
			elif pospart == 'False':
				result = negpart
			elif negpart == 'False':
				result = pospart
			else:
				result = f'{pospart}{negpart}'
			self.ssa.append(f'SSA({fluent},' + 
				f'{self.actionName}{action_arguments_str}) <=> ' + result)

if(__name__ == '__main__'):
	import sys
	parser = Parser()
	domainFileName = sys.argv[1]
	parser.parse_domain(domainFileName)
	with open(sys.argv[2], 'w') as f:
		for p in parser.poss:
			f.write(p + '\n')
		for p in parser.ssa:
			f.write(p + '\n')