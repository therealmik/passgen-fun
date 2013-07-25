#!/usr/bin/python3

"""
This was written because I thought that there'd be dupes resulting from
overlapping of the two consonants charsets.

I was (very) wrong - it usually generates more possible passwords than
2^bits, but have fun anyway =P
"""

VOWELS = 'a4AeE3iIoO0uUyY@' # 4 bits
CONSONANTS1 = 'bcdfghjklmnpqrstvwxzBDGHJKLMNPRS' # 5 bits
CONSONANTS2 = 'bcdfghjklmnpqrstvwxzBCDFGHJKLMNPQRSTVWXZ1256789!#$%^&*()-+=[];.,' # 6 bits

def generate_pwmake_state0(bitsleft, sofar=""):
	if bitsleft <= 0:
		yield sofar
		return

	yield from generate_pwmake_vowels(bitsleft-1, sofar)
	for c in CONSONANTS2:
		yield from generate_pwmake_vowels(bitsleft-7, sofar+c)

def generate_pwmake_vowels(bitsleft, sofar):
	if bitsleft < 0:
		yield sofar
		return

	for c in VOWELS:
		yield from generate_pwmake_consonants(bitsleft-4, sofar+c)

def generate_pwmake_consonants(bitsleft, sofar):
	if bitsleft < 0:
		yield sofar
		return

	for c in CONSONANTS1:
		yield from generate_pwmake_state0(bitsleft-5, sofar+c)

if __name__ == "__main__":
	import sys

	if len(sys.argv) != 2:
		print("Usage:", sys.argv[0], "<bits>")
		sys.exit(1)

	for pw in generate_pwmake_state0(int(sys.argv[1])):
		print(pw)

