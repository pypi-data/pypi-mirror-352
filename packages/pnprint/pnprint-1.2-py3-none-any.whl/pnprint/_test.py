from . import *

def test_nformat():
	opts = dict(width=100)
	assert nformat([[1000,2324,30],[40000,5000,6342342]], **opts) == '[[1000, 2324, 30], [40000, 5000, 6342342]]'
	assert nformat(repr({
		'name': 'mydict',
		'comment': 'this is a dictionnary',
		'field': (5, 6),
		'long one': [12324232, 53445645645, 'truc', 345345345345345356, (456,45), 'bla bla bla', 'blo blo blo', 'things and so'],
		'some text': '/!\\  even content of strings is formated:\n  {345, 23, 17, [2,1]}  as you see\n',
		}), **opts) == "{\n\t'name': 'mydict',\n\t'comment': 'this is a dictionnary',\n\t'field': (5, 6),\n\t'long one': [\n\t\t12324232,\n\t\t53445645645,\n\t\t'truc',\n\t\t345345345345345356,\n\t\t(456, 45),\n\t\t'bla bla bla',\n\t\t'blo blo blo',\n\t\t'things and so'],\n\t'some text': '/!\\\\  even content of strings is formated:\\n  {345, 23, 17, [2,1]}  as you see\\n'}"

def test_deformat():
	input = '''
	P2 = vec3(0.08182,1.184e-08,-0.09931)
	P3 = vec3(-0.0431,1.258e-08,-0.1056)
P4 = vec3(-0.1593,-1.199e-08,0.1006)
line = [
	Segment(P4, P0),
	Segment(P0, P1 ),
	ArcThrough(P1, vec3(0.09681,-1.713e-09,0.01437), P2
		),
	Segment(P2,P3),
	ArcThrough(P3,vec3(-0.06933,-1.117e-09,0.009369),P4),
	]
axis = Axis(
	vec3(-0.1952,	4.918e-08,	-0.4126),
	vec3(1,	0,	0))
	'''
	output = 'P2 = vec3(0.08182,1.184e-08,-0.09931)\nP3 = vec3(-0.0431,1.258e-08,-0.1056)\nP4 = vec3(-0.1593,-1.199e-08,0.1006)\nline = [Segment(P4, P0), Segment(P0, P1), ArcThrough(P1, vec3(0.09681,-1.713e-09,0.01437), P2), Segment(P2,P3), ArcThrough(P3,vec3(-0.06933,-1.117e-09,0.009369),P4), ]\naxis = Axis(vec3(-0.1952, 4.918e-08, -0.4126), vec3(1, 0, 0))\n'
	assert deformat(input) == output
	
def test_ncolor():
	# for object dumping with string representation
	nprint(repr(dir()))
	
	# for common print use
	nprint('here is a list:', [[1000,2324,30],[40000,5000,6342342]], '\nhere is a type:', int, '\nhere is a Name in CamelCase and one in AVeryLongStringAndSoWhat')
	
	# for string and data output
	nprint('hello everyone, 100 is a decimal number and (0x27a) is an hexadecimal one between parentheses. (did you noticed the automatic line shift ?)')
	
	# complex structures
	data = {
		'name': 'mydict',
		'comment': 'this is a dictionnary',
		'field': (5, 6),
		'long one': [12324232, 53445645645, 'truc', 345345345345345356, (456,45), 'bla bla bla', 'blo blo blo', 'things and so'],
		'some text': '/!\\  even content of strings is formated:\n  {345, 23, 17, [2,1]}  as you see\n',
		}

	nprint('data structure: ', data)

def test_ccolor():
	from textwrap import dedent
	cprint(dedent("""\
def parcimonize(cache: dict, scope: str, args: list, code: Iterable[AST], previous: dict, filter:callable=None) -> Iterable[AST]:
	''' make a code lazily executable by reusing as much previous results as possible '''
	assigned = Counter()
	changed = set()
	memo = dict()
	
	homogenize(code)
	
	# new ast body
	yield from _scope_init(scope, args)
	for node in code:
		# find inputs and outputs of this statement
		deps = list(set(dependencies(node)))
		provided = sorted(set(results(node)), reverse=True)
		
		if not provided: 
			yield node
			continue
		
		# update the number of assignments to provided variables
		assigned.update(provided)
		# cache key for this statement
		key = '{}{}'.format(provided[0], assigned[provided[0]])
		# check if the node code or dependencies has changed
		if scope not in previous:
			previous[scope] = {}
		previous = previous[scope]
		
		if not equal(previous.get(key), node) or any(dep in changed  for dep in deps):
			# count all depending variables as changed
			changed.update(provided)
			# void cache of changed statements
			if scope in cache:
				for backups in cache[scope].values():
					backups.discard(key)
				if not cache[scope]:
					cache.pop(scope)
					
		previous[key] = deepcopy(node, memo)
		
		# functions are caching in separate scopes
		if isinstance(node, FunctionDef):
			yield _parcimonize_func(cache, scope, node, key, previous)
			
		# TODO: use a proper filter instead
		elif not filter(node):
			yield node
		
		# an expression assigned is assumed to not modify its arguments
		elif isinstance(node, Assign):
			yield from _parcimonize_assign(key, node)
		
		# an expression without result is assumed to be an inplace modification
		# a block cannot be splitted because its bodies may be executed multiple times or not at all
		elif isinstance(node, (Expr, For, While, Try, With, If, Match)):
			yield from _parcimonize_block(key, provided or deps, node)
			
		# an expression returned is assumed to not modify its arguments
		elif isinstance(node, Return):
			yield from _parcimonize_return(key, node)
			
		# TODO: decide what to do when the target is a subscript
		# TODO: add filter function to avoid parcimonizing every single statement
		
		else:
			yield node
		"""))

