# author:	Jimy Byerley (jimy.byerley@gmail.com)
# license:	GNU-LGPLv3

""" Intends to replace the well known pprint, to format python objects on output
	
	nprint()      the pprint replacement: it works as print() but works on strings instead of working 
	              on already known objects split too long lines into indented blocks by syntax markers 
	              (such as {}()[], etc)
	              be careful:  as print(), nprint use the string conversion str(obj) to convert an object 
	                           passed, if you want to use the string representation, then you'll have to 
	                           pass repr(obj) to nprint or nformat
	nformat()     split a text into indented lines
	ncolor()      add terminal color markups to nested structures
	deformat()    remove formatting of all marker-enclosed text
	cprint()      print arguments with python syntaxic coloration
	ccolor()      add terminal color markups to python syntax
"""

from itertools import chain
from types import SimpleNamespace
import os, io, re



# default themes
# blue-green colors
blue_green = SimpleNamespace(
	normal = '\x1b[0m',
	marker =	'\x1b[38;5;46m',
	number =	'\x1b[38;5;33m',
	# nested structs coloration
	encloser =	'\x1b[38;5;42m',
	specials =	'\x1b[38;5;33m',
	camel =		'\x1b[1;34;40m',
	# code coloration
	keyword = '\x1b[38;5;42m',
	private = '\x1b[38;5;250m',
	comment = '\x1b[38;5;245m',
	)

# red-orange colors
red_orange = SimpleNamespace(
	normal = '\x1b[0m',
	marker =	'\x1b[38;5;214m',
	number =	'\x1b[38;5;202m',
	# nested struct coloration
	encloser =	'\x1b[38;5;196m',
	specials =	'\x1b[38;5;202m',
	camel =		'\x1b[1;34;40m',
	# code coloration
	keyword = '\x1b[38;5;42m',
	private = '\x1b[38;5;250m',
	comment = '\x1b[38;5;245m',
	)

# settings
# enable automatic coloration if supported
enable_color = True
line_width = 100
colors = blue_green




def nformat(text:str, indent=0, width=None) -> str:
	''' output text, splited into indented blocks, newlines are kept '''
	if type(text) != str:	text = str(text)
	out = io.StringIO()
	seek = 0
	if not width:	width = os.environ.get('COLUMNS', line_width)
	
	while seek < len(text):
		if text[seek] in _begin_marker:
			term = _next_terminator(text, seek+1)
			if term - seek > width or '\n' in text[seek:term]:	# develop enclosement if its length is over that width
				indent += 1
				out.write(text[seek])
				if _next_separator(text, seek+1) < term: 	# no return if there is only one element in the enclosement
					out.write( '\n'+'\t'*indent )
					seek = _next_word(text, seek+1)-1
			else:
				out.write(text[seek:term+1])
				seek = term
		elif text[seek] in _separators:
			out.write(text[seek] + '\n'+'\t'*indent)
			seek = _next_word(text, seek+1)-1
		elif text[seek] in _end_marker:
			indent -= 1
			out.write(text[seek])
		else:
			out.write(text[seek])
		
		seek += 1
	
	return out.getvalue()

_separators = ',;'
_begin_marker = '{(['
_end_marker = '})]'
_symbols = ':*/+-<>'
_specials = '\\'
_spaces = ' \t\n'

def _next_separator(text, seek):
	counter = 0
	i = seek
	for i in range(seek, len(text)):
		if text[i] in _begin_marker:	counter += 1
		elif text[i] in _end_marker:	counter -= 1
		if counter < 0 or (counter == 0 and text[i] in _separators):	break
	return i

def _next_terminator(text, seek):
	counter = 0
	i = seek
	for i in range(seek, len(text)):
		if text[i] in _begin_marker:	counter += 1
		elif text[i] in _end_marker:	counter -= 1
		if counter < 0:		break
	return i
	
def _next_word(text, seek):
	while seek < len(text) and text[seek] in _spaces:
		seek += 1
	return seek

def deformat(text):
	''' remove formatting from text, leving only indentation and line breaks for lines not ended by a continuation character (,-+*/) '''
	seek = _next_word(text, 0)
	out = io.StringIO()
	
	while seek < len(text):
		if text[seek] in _spaces:
			jump = _next_word(text, seek)
			if text[seek-1] in ',+-*/':
				out.write(' ')
			elif text[seek-1] in _begin_marker or jump < len(text) and text[jump] in _end_marker:
				pass
			elif '\n' in text[seek:jump]:
				out.write('\n')
			else:
				out.write(' ')
			seek = jump
		else:
			out.write(text[seek])
			seek += 1
	return out.getvalue()
		

def ncolor(text:str, colors=None, detect_camelcase=False) -> str:
	''' generates a string with the content of the text passed, with terminal color makers to highlight some syntax elements '''
	if colors is None:
		colors = globals()['colors']
	# list of colors to apply
	coloration = []
	# look for special _symbols
	for symbol in chain(_separators, _begin_marker, _end_marker, _symbols, _specials):
		start = text.find(symbol, 0)
		while start != -1:
			end = start + len(symbol)
			color = colors.encloser
			
			if symbol == '<':
				after_name = text.find(' ', end)
				if text[end:after_name].isidentifier():	
					end = after_name
				color = colors.marker
			elif symbol == '>':			color = colors.marker
			elif symbol in _specials:	color = colors.specials
			
			coloration.insert(
				_bisect(coloration, start, lambda x:x[1]), 
				(color, start, end-1)
				)
			start = text.find(symbol, end)
	
	# look for special worlds
	it = iter(text)
	i = 0
	for c in it:
		if c.isalnum():
			# look for numbers
			if c.isdigit():
				for j,c in enumerate(it):
					if not c.isalnum():	
						j -= 1
						break
				j += 1
				coloration.insert(
					_bisect(coloration, i, lambda x:x[1]), 
					(colors.number, i, i+j)
					)
				i += j+1
			# look for CamelCase names
			if c.isupper() and detect_camelcase:
				for j,c in enumerate(it):
					if not c.isalnum():	
						j -= 1
						break
				j += 1
				coloration.insert(
					_bisect(coloration, i, lambda x:x[1]), 
					(colors.camel, i, i+j)
					)
				i += j+1
		i += 1
	
	out = ''
	last = 0
	for color,start,end in coloration:
		end +=1
		out += text[last:start] + color + text[start:end] + colors.normal
		last = end
	out += text[last:]
	return out

def _bisect(l, index, key=lambda x:x):
	''' simple bisection over an array '''
	start,end = 0, len(l)
	while start < end:
		mid = (start+end)//2
		val = key(l[mid])
		if val < index:		start =	mid+1
		elif val > index:	end =	mid
		else:	return mid
	return start


def nprint(*args, indent=0, color=None, end='\n'):
	""" write the arguments passed to the standard output, using nformat and ncolor """
	if color is None:
		color = enable_color
	color = color and 'COLORTERM' in os.environ
	text = '\t'*indent + nformat(' '.join((str(arg) for arg in args)), indent)
	print(ncolor(text) if color else text, end=end)


_keywords = {'pass', 'and', 'or', 'if', 'elif', 'else', 'match', 'case', 'for', 'while', 'break', 'continue', 'is', 'in', 'not', 'def', 'lambda', 'class', 'yield', 'async', 'await', 'with', 'try', 'except', 'finally', 'raise', 'from', 'import', 'as', 'with', 'return', 'assert'}
_constants = {'None', 'True', 'False', 'Ellipsis'}
_private_start = '_'
_word_pattern = re.compile(r'([a-zA-Z_]\w*)')
_call_pattern = re.compile(r'([a-zA-Z]\w*)\(')
_number_pattern = re.compile(r'[+-]?\d+\.?\d*(e[+-]\d+)?')
_operator_pattern = re.compile(r'[+\-\*/@<>=!~&\|]+')
_string_pattern = re.compile(r'[\'\"][^\'\"]*[\'\"]')
_comment_pattern = re.compile(r'#.*')

def ccolor(code:str, colors=None) -> str:
	''' colorize the given code by adding unix terminal codes for character coloration '''
	if colors is None:
		colors = globals()['colors']
	
	position = 0
	result = io.StringIO()
	while position < len(code):
		if match := _call_pattern.match(code, position):
			result.write(colors.marker)
			result.write(code[match.start():match.end()-1])
			result.write(colors.normal)
			position = match.end()-1
		elif match := _number_pattern.match(code, position):
			result.write(colors.number)
			result.write(match.group())
			result.write(colors.normal)
			position = match.end()
		elif match := _string_pattern.match(code, position):
			result.write(colors.number)
			result.write(match.group())
			result.write(colors.normal)
			position = match.end()
		elif match := _comment_pattern.match(code, position):
			result.write(colors.comment)
			result.write(match.group())
			result.write(colors.normal)
			position = match.end()
		elif match := _word_pattern.match(code, position):
			word = match.group()
			if word in _keywords:
				result.write(colors.keyword)
				result.write(word)
				result.write(colors.normal)
			elif word in _constants:
				result.write(colors.number)
				result.write(word)
				result.write(colors.normal)
			elif word.startswith(_private_start):
				result.write(colors.private)
				result.write(word)
				result.write(colors.normal)
			else:
				result.write(word)
			position = match.end()
		else:
			result.write(code[position])
			position += 1
	return result.getvalue()
	
def cprint(*code):
	''' print the given blocks of code with syntex coloration '''
	for block in code:
		print(ccolor(block))
