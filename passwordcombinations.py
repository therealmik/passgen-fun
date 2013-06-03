#!/usr/bin/python3

"""Generate a graph of possible password combinations
This tool displays the combinations of possible passwords
that a random password generator can create, taking into
account password rules (eg. requiring one of each class).

Pipe the output of this program into dot"""

# 26 uppers, 26 lowers, 10 numbers, 32 symbols
PROBS = [ 26, 26, 10, 32 ]
COLOURS = [ '"#FF0000"', '"#00FF00"', '"#0000FF"', '"#FF00FF"' ]
PW_LENGTH=4 # Don't set this too high, it'll eat all your ram
ENFORCE_RULES=True # Whether to enforce password rules.  If set to false, the resulting number will be sum(PROBS) ** PW_LENGTH

# Pre-calculating these to avoid runtime overhead
FLAGS = [ 1 << i for i in range(len(PROBS)) ]
VALID = (1 << len(PROBS)) - 1

class Node(object):
	"""An object representing a node in the graph"""
	NODEID=0

	def __init__(self, charset):
		self.charset = charset
		self.children = []
		self.nodeid = Node.NODEID
		Node.NODEID += 1

	def get_permutations(self):
		if len(self.children) == 0:
			return PROBS[self.charset]
		else:
			return PROBS[self.charset] * sum([ c.get_permutations() for c in self.children])

	def print_graph(self):
		children = [ "n" + str(c.nodeid) for c in self.children ]
		myid = "n" + str(self.nodeid)
		print("\t" + myid + " [label=" + str(PROBS[self.charset]) + " fontcolor=" + COLOURS[self.charset] + "];")
		if len(children) > 0:
			print("\t" + myid + " -> {" + " ".join(children) + "};")
		for c in self.children:
			c.print_graph()
			

class RootNode(Node):
	"""The top of the graph"""

	def __init__(self):
		self.children = []
		self.nodeid = Node.NODEID
		Node.NODEID += 1

	def get_permutations(self):
		if len(self.children) == 0:
			return 0
		else:
			return sum([ c.get_permutations() for c in self.children])

	def print_graph(self):
		print("digraph randompw {")

		children = [ "n" + str(c.nodeid) for c in self.children ]
		myid = "root"
		print("\troot [label=1 fontcolor=black];")
		print("\troot -> {" + " ".join(children) + "};")
		for c in self.children:
			c.print_graph()

		print("}")
	
class Invalid(Exception):
	pass

def gen(node, length=PW_LENGTH, flags=0):
	if length == 0:
		if ENFORCE_RULES and flags != VALID:
			raise Invalid()
		return

	for i in range(len(PROBS)):
		n = Node(i)
		try:
			gen(n, length-1, flags | FLAGS[i])
			node.children.append(n)
		except Invalid:
			pass
	if len(node.children) == 0:
		raise Invalid()

if __name__ == "__main__":
	import sys

	rootNode = RootNode()
	gen(rootNode)
	print(rootNode.get_permutations(), file=sys.stderr)
	rootNode.print_graph()

