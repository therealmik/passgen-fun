#!/usr/bin/python3

"""
Generate all possible pwgen phonemes (the default mode)

This is a recursive generator function that tries to generate all
possible pwgen phonemes, along with their probabilities.

FIXME: The probabilities are almost certainly wrong (eg. won't add up to 1)
TODO: Merge duplicate branches

A full run with 6 chars produced 1124226450 possibilities
""" 

import operator

PASSWORD_LENGTH=6

CONSONANT = 1
VOWEL = 2
DIPTHONG = 4
NOT_FIRST = 8
NUMBER=16

charset = [
	("a", VOWEL, 2.0/64),
	("ae", VOWEL | DIPTHONG, 2.0/64),
	("ah", VOWEL | DIPTHONG, 2.0/64),
	("ai", VOWEL | DIPTHONG, 2.0/64),
	("b", CONSONANT, 2.0/64),
	("c", CONSONANT, 2.0/64),
	("ch", CONSONANT | DIPTHONG, 2.0/64),
	("d", CONSONANT, 2.0/64),
	("e", VOWEL, 2.0/64),
	("ee", VOWEL | DIPTHONG, 2.0/64),
	("ei", VOWEL | DIPTHONG, 2.0/64),
	("f", CONSONANT, 2.0/64),
	("g", CONSONANT, 2.0/64),
	("gh", CONSONANT | DIPTHONG | NOT_FIRST, 2.0/64),
	("h", CONSONANT, 2.0/64),
	("i", VOWEL, 2.0/64),
	("ie", VOWEL | DIPTHONG, 2.0/64),
	("j", CONSONANT, 2.0/64),
	("k", CONSONANT, 2.0/64),
	("l", CONSONANT, 2.0/64),
	("m", CONSONANT, 2.0/64),
	("n", CONSONANT, 2.0/64),
	("ng", CONSONANT | DIPTHONG | NOT_FIRST, 2.0/64),
	("o", VOWEL, 2.0/64),
	("oh", VOWEL | DIPTHONG, 1.0/64),
	("oo", VOWEL | DIPTHONG, 1.0/64),
	("p", CONSONANT, 1.0/64),
	("ph", CONSONANT | DIPTHONG, 1.0/64),
	("qu", CONSONANT | DIPTHONG, 1.0/64),
	("r", CONSONANT, 1.0/64),
	("s", CONSONANT, 1.0/64),
	("sh", CONSONANT | DIPTHONG, 1.0/64),
	("t", CONSONANT, 1.0/64),
	("th", CONSONANT | DIPTHONG, 1.0/64),
	("u", VOWEL, 1.0/64),
	("v", CONSONANT, 1.0/64),
	("w", CONSONANT, 1.0/64),
	("x", CONSONANT, 1.0/64),
	("y", CONSONANT, 1.0/64),
	("z", CONSONANT, 1.0/64),
] + [(str(x), NUMBER, 2.0/16) for x in range(0, 6)] + [(str(x), NUMBER, 1.0/16) for x in range(6, 10)]

class Possibility(object):
	def __init__(self, flags, probability, next_state, upper=False):
		self.flags = flags
		self.probability = probability
		self.next_state = next_state
		self.upper = upper

	def __iter__(self):
		for (c, f, p) in charset:
			if f == self.flags:
				if self.upper:
					yield (c.capitalize(), f, p*self.probability)
				else:
					yield (c, f, p*self.probability)
		
class State(object):
	def __init__(self, sofar="", probability=1.0, generated_upper=False, generated_number=False):
		self.sofar = sofar
		self.probability = probability
		self.generated_upper = generated_upper
		self.generated_number = generated_number

	def __iter__(self):
		if len(self.sofar) == PASSWORD_LENGTH:
			if self.generated_upper and self.generated_number:
				yield (self.sofar, self.probability)
			return
		if len(self.sofar) > PASSWORD_LENGTH:
			return

		for possibility in self.possibilities:
			for (c, f, p) in sorted(iter(possibility), key=operator.itemgetter(2), reverse=True):
				s = possibility.next_state(self.sofar+c, p, self.generated_upper or possibility.upper, self.generated_number or f == NUMBER)
				yield from iter(s)

class s_first(State):
	pass

class s_after_consonant(State):
	pass

class s_after_vowel(State):
	pass

class s_after_double_vowel(State):
	pass

s_first.possibilities = [
		Possibility(CONSONANT, 0.5, s_after_consonant),
		Possibility(CONSONANT|DIPTHONG, 0.5, s_after_consonant),
		Possibility(VOWEL, 0.5, s_after_vowel),
		Possibility(VOWEL|DIPTHONG, 0.5, s_after_double_vowel),
		Possibility(CONSONANT, 0.5 * 0.25, s_after_consonant, True),
		Possibility(CONSONANT|DIPTHONG, 0.5 * 0.25, s_after_consonant, True),
		Possibility(VOWEL, 0.5 * 0.25, s_after_vowel, True),
		Possibility(VOWEL|DIPTHONG, 0.5 * 0.25, s_after_double_vowel, True),
	]

s_after_consonant.possibilities = [
		Possibility(VOWEL, 0.625, s_after_vowel),
		Possibility(VOWEL|DIPTHONG, 0.625, s_after_double_vowel),
		Possibility(NUMBER, 0.375, s_first),
	]

s_after_vowel.possibilities = [
		Possibility(CONSONANT, 0.25, s_after_consonant),
		Possibility(CONSONANT|DIPTHONG, 0.25, s_after_consonant),
		Possibility(CONSONANT|DIPTHONG|NOT_FIRST, 0.25, s_after_consonant),
		Possibility(CONSONANT, 0.125, s_after_consonant, True),
		Possibility(CONSONANT|DIPTHONG, 0.125, s_after_consonant, True),
		Possibility(CONSONANT|DIPTHONG|NOT_FIRST, 0.125, s_after_consonant, True),
		Possibility(VOWEL, 0.625, s_after_double_vowel),
		Possibility(NUMBER, 0.375, s_first),
	]

s_after_double_vowel.possibilities = [
		Possibility(CONSONANT, 0.25, s_after_consonant),
		Possibility(CONSONANT|DIPTHONG, 0.25, s_after_consonant),
		Possibility(CONSONANT|DIPTHONG|NOT_FIRST, 0.25, s_after_consonant),
		Possibility(CONSONANT, 0.125, s_after_consonant, True),
		Possibility(CONSONANT|DIPTHONG, 0.125, s_after_consonant, True),
		Possibility(CONSONANT|DIPTHONG|NOT_FIRST, 0.125, s_after_consonant, True),
		Possibility(NUMBER, 0.375, s_first),
	]

if __name__ == "__main__":
	import sys

	count = 0
	for (x, probability) in iter(s_first()):
		count += 1
		print(x) # + "\t" + str(probability))
		if count % 10000000 == 0:
			print("Generated {0:d}...".format(count), file=sys.stderr)
	print("Completed, total={0:d}...".format(count), file=sys.stderr)

