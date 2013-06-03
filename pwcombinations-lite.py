#!/usr/bin/python3

"""Calculate the total number of passwords that can be generated
This tool displays the total number of combinations of possible passwords
that a random password generator can create, taking into account
password rules (eg. requiring one of each class)."""

# 26 uppers, 26 lowers, 10 numbers, 32 symbols
PROBS = [ 26, 26, 10, 32 ]
PW_LENGTH=12 # Don't set this too high, it'll eat all your ram
ENFORCE_RULES=True # Whether to enforce password rules.  If set to false, the resulting number will be sum(PROBS) ** PW_LENGTH

# Pre-calculating these to avoid runtime overhead
FLAGS = [ 1 << i for i in range(len(PROBS)) ]
VALID = (1 << len(PROBS)) - 1

def gen(combinations=1, length=PW_LENGTH, flags=0):
	if length == 0:
		if ENFORCE_RULES and flags != VALID:
			yield 0
		else:
			yield combinations
		return

	for i in range(len(PROBS)):
		yield sum(gen(PROBS[i], length-1, flags | FLAGS[i])) * combinations

if __name__ == "__main__":
	import sys

	print(sum(gen()))

