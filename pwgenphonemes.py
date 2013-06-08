#!/usr/bin/python3

"""
Generate all possible pwgen phonemes (the default mode)

This is a recursive generator function that tries to generate all
possible pwgen phonemes, along with their probabilities.

FIXME: The probabilities are almost certainly wrong (eg. won't add up to 1)
TODO: Merge duplicate branches

A full run with 6 chars produced 1124226450 possibilities
""" 

from __future__ import print_function
from __future__ import division

import operator
import numpy
import sys
import itertools
import heapq

PASSWORD_LENGTH=8

CONSONANT = 1
VOWEL = 2
DIPTHONG = 4
NOT_FIRST = 8
NUMBER=16
CONSTNEXT=32

class CharsetItem(tuple):
	def __new__(cls, c, flags):
		return tuple.__new__(cls, (c, flags))

	c = property(operator.itemgetter(0))
	flags = property(operator.itemgetter(1))
	
charset = [
	CharsetItem("a", VOWEL),
	CharsetItem("ae", VOWEL | DIPTHONG),
	CharsetItem("ah", VOWEL | DIPTHONG | CONSTNEXT),
	CharsetItem("ai", VOWEL | DIPTHONG),
	CharsetItem("b", CONSONANT),
	CharsetItem("c", CONSONANT),
	CharsetItem("ch", CONSONANT | DIPTHONG),
	CharsetItem("d", CONSONANT),
	CharsetItem("e", VOWEL),
	CharsetItem("ee", VOWEL | DIPTHONG),
	CharsetItem("ei", VOWEL | DIPTHONG),
	CharsetItem("f", CONSONANT),
	CharsetItem("g", CONSONANT),
	CharsetItem("gh", CONSONANT | DIPTHONG | NOT_FIRST),
	CharsetItem("h", CONSONANT),
	CharsetItem("i", VOWEL),
	CharsetItem("ie", VOWEL | DIPTHONG),
	CharsetItem("j", CONSONANT),
	CharsetItem("k", CONSONANT),
	CharsetItem("l", CONSONANT),
	CharsetItem("m", CONSONANT),
	CharsetItem("n", CONSONANT),
	CharsetItem("ng", CONSONANT | DIPTHONG | NOT_FIRST),
	CharsetItem("o", VOWEL),
	CharsetItem("oh", VOWEL | DIPTHONG | CONSTNEXT),
	CharsetItem("oo", VOWEL | DIPTHONG),
	CharsetItem("p", CONSONANT),
	CharsetItem("ph", CONSONANT | DIPTHONG),
	CharsetItem("qu", CONSONANT | DIPTHONG),
	CharsetItem("r", CONSONANT),
	CharsetItem("s", CONSONANT),
	CharsetItem("sh", CONSONANT | DIPTHONG),
	CharsetItem("t", CONSONANT),
	CharsetItem("th", CONSONANT | DIPTHONG),
	CharsetItem("u", VOWEL),
	CharsetItem("v", CONSONANT),
	CharsetItem("w", CONSONANT),
	CharsetItem("x", CONSONANT),
	CharsetItem("y", CONSONANT),
	CharsetItem("z", CONSONANT),
]
charset.extend([CharsetItem(str(x), NUMBER) for x in range(0, 10)])

class Possibility(object):
	def __init__(self, flags, weight, next_state, upper=False, dipthong_weight=None):
		self.flags = flags
		self.items = [ item for item in charset if item.flags == self.flags ]
		self.weight = numpy.float128(weight)
		self.itemWeight = self.weight / len(self.items)
		self.next_state = next_state
		self.upper = upper
		self.dipthong_weight = dipthong_weight

	def __iter__(self):
		for item in self.items:
			c = item.c
			if self.upper:
				c = c.capitalize()
			yield (c, item.flags, self.itemWeight)
		
	@property
	def numchars(self):
		if self.flags & DIPTHONG != 0:
			return 2
		else:
			return 1

class Result(tuple):
	def __new__(cls, password, probability):
		return tuple.__new__(cls, (password, probability))

	password = property(operator.itemgetter(0))
	probability = property(operator.itemgetter(1))

class State(object):
	def generate(self, gen_length, sofar="", probability=1.0, generated_upper=False, generated_number=False, dipthong_boost=None):
		"""Recursively generate all possibly passwords that are gen_length long"""

		if len(sofar) == gen_length:
			if generated_upper and generated_number:
				yield Result(sofar, probability)
			return
		if len(sofar) > gen_length:
			return

		for possibility in self.possibilities:
			next_dipthong_boost = None
			if possibility.dipthong_weight is not None:
				next_dipthong_boost = probability * possibility.dipthong_weight
			for (c, flags, weight) in iter(possibility):
				p = probability * weight
				if dipthong_boost is not None:
					dipthong_candidate = sofar[-1].lower() + c
					matches = [ csi for csi in charset if csi.c == dipthong_candidate and flags & CONSTNEXT == 0 ]
					if len(matches) > 0:
						p += dipthong_boost
				yield from possibility.next_state().generate(
					gen_length,
					sofar+c,
					probability * weight,
					(generated_upper or possibility.upper),
					(generated_number or flags == NUMBER),
					next_dipthong_boost
				)

	def combinations(self, length, combinations=1, haveUpper=False, haveNumber=False):
		"""Calculate the total number of possible passwords that can be generated."""

		if length == 0:
			if haveUpper and haveNumber:
				yield combinations
			else:
				yield 0
			return
		elif length < 0:
			yield 0
			return

		yield from (
			combinations * sum(
				p.next_state().combinations(
					length - p.numchars,
					len(list(iter(p))),
					haveUpper or p.upper,
					haveNumber or p.flags == NUMBER
				)
			)
			for p in self.possibilities
		)

def joint_weight(flag, *others):
	total_matches = 0.0
	flag_matches = 0.0

	for c in charset:
		if c.flags == flag or c.flags in others:
			total_matches += 1.0
		if c.flags == flag:
			flag_matches += 1.0
	return numpy.float128(flag_matches / total_matches)

class s_first(State):
	pass

class s_after_consonant(State):
	pass

class s_after_vowel(State):
	pass

class s_after_double_vowel(State):
	pass

s_first.possibilities = [
	Possibility(VOWEL|DIPTHONG|CONSTNEXT,	joint_weight(VOWEL|DIPTHONG|CONSTNEXT, VOWEL|DIPTHONG, VOWEL) * 0.5 * 0.75, s_after_double_vowel),
	Possibility(VOWEL,		joint_weight(VOWEL, VOWEL|DIPTHONG, VOWEL|DIPTHONG|CONSTNEXT) * 0.5 * 0.80, s_after_vowel, dipthong_weight=joint_weight(VOWEL|DIPTHONG, VOWEL, VOWEL|DIPTHONG|CONSTNEXT)),
	Possibility(VOWEL|DIPTHONG|CONSTNEXT,	joint_weight(VOWEL|DIPTHONG|CONSTNEXT, VOWEL|DIPTHONG, VOWEL) * 0.5 * 0.75, s_after_double_vowel, True),
	Possibility(VOWEL,		joint_weight(VOWEL, VOWEL|DIPTHONG, VOWEL|DIPTHONG|CONSTNEXT) * 0.5 * 0.80, s_after_vowel, True, dipthong_weight=joint_weight(VOWEL|DIPTHONG, VOWEL, VOWEL|DIPTHONG|CONSTNEXT)),
	Possibility(CONSONANT|DIPTHONG,	joint_weight(CONSONANT|DIPTHONG, CONSONANT) * 0.5 * 0.80, s_after_consonant),
	Possibility(CONSONANT,		joint_weight(CONSONANT, CONSONANT|DIPTHONG) * 0.5 * 0.80, s_after_consonant),
	Possibility(CONSONANT|DIPTHONG,	joint_weight(CONSONANT|DIPTHONG, CONSONANT) * 0.5 * 0.20, s_after_consonant, True),
	Possibility(CONSONANT,		joint_weight(CONSONANT, CONSONANT|DIPTHONG) * 0.5 * 0.20, s_after_consonant, True),
]

s_after_consonant.possibilities = [
	Possibility(NUMBER,		0.3, s_first),
	Possibility(VOWEL|DIPTHONG|CONSTNEXT,	joint_weight(VOWEL|DIPTHONG|CONSTNEXT, VOWEL, VOWEL|DIPTHONG) * 0.625, s_after_double_vowel),
	Possibility(VOWEL,		joint_weight(VOWEL, VOWEL|DIPTHONG, VOWEL|DIPTHONG|CONSTNEXT) * 0.7, s_after_vowel, dipthong_weight=joint_weight(VOWEL|DIPTHONG, VOWEL, VOWEL|DIPTHONG|CONSTNEXT)),
]

s_after_vowel.possibilities = [
	Possibility(VOWEL, 0.7 * 0.4, s_after_double_vowel),
	Possibility(NUMBER, 0.3, s_first),
	Possibility(CONSONANT|DIPTHONG, 		joint_weight(CONSONANT|DIPTHONG, CONSONANT, CONSONANT|DIPTHONG|NOT_FIRST) * 0.7 * 0.6 * 0.80, s_after_consonant),
	Possibility(CONSONANT,				joint_weight(CONSONANT, CONSONANT|DIPTHONG, CONSONANT|DIPTHONG|NOT_FIRST) * 0.7 * 0.6 * 0.80, s_after_consonant),
	Possibility(CONSONANT|DIPTHONG|NOT_FIRST, 	joint_weight(CONSONANT|DIPTHONG|NOT_FIRST, CONSONANT|DIPTHONG, CONSONANT) * 0.7 * 0.6 * 0.80, s_after_consonant),
	Possibility(CONSONANT|DIPTHONG, 		joint_weight(CONSONANT|DIPTHONG, CONSONANT, CONSONANT|DIPTHONG|NOT_FIRST) * 0.7 * 0.6 * 0.20, s_after_consonant, True),
	Possibility(CONSONANT,				joint_weight(CONSONANT, CONSONANT|DIPTHONG, CONSONANT|DIPTHONG|NOT_FIRST) * 0.7 * 0.6 * 0.20, s_after_consonant, True),
	Possibility(CONSONANT|DIPTHONG|NOT_FIRST, 	joint_weight(CONSONANT|DIPTHONG|NOT_FIRST, CONSONANT|DIPTHONG, CONSONANT) * 0.7 * 0.6 * 0.20, s_after_consonant, True),
]

s_after_double_vowel.possibilities = [
	Possibility(NUMBER, 0.3, s_first),
	Possibility(CONSONANT,				joint_weight(CONSONANT, CONSONANT|DIPTHONG, CONSONANT|DIPTHONG|NOT_FIRST) * 0.7 * 0.80, s_after_consonant),
	Possibility(CONSONANT|DIPTHONG,			joint_weight(CONSONANT|DIPTHONG, CONSONANT, CONSONANT|DIPTHONG|NOT_FIRST) * 0.7 * 0.80, s_after_consonant),
	Possibility(CONSONANT|DIPTHONG|NOT_FIRST,	joint_weight(CONSONANT|DIPTHONG|NOT_FIRST, CONSONANT, CONSONANT|DIPTHONG) * 0.7 * 0.80, s_after_consonant),
	Possibility(CONSONANT,				joint_weight(CONSONANT, CONSONANT|DIPTHONG, CONSONANT|DIPTHONG|NOT_FIRST) * 0.7 * 0.20, s_after_consonant, True),
	Possibility(CONSONANT|DIPTHONG,			joint_weight(CONSONANT|DIPTHONG, CONSONANT, CONSONANT|DIPTHONG|NOT_FIRST) * 0.7 * 0.20, s_after_consonant, True),
	Possibility(CONSONANT|DIPTHONG|NOT_FIRST,	joint_weight(CONSONANT|DIPTHONG|NOT_FIRST, CONSONANT, CONSONANT|DIPTHONG) * 0.7 * 0.20, s_after_consonant, True),
]

## Check that no easily-spotted mistakes were made in probabilities
#for s in (s_first, s_after_consonant, s_after_vowel, s_after_double_vowel):
	#total_weight = numpy.array([p.weight for p in s.possibilities], dtype=numpy.float128).sum()
	# print(s.__name__ + ": " + str(total_weight), file=sys.stderr)
	#assert(str(total_weight) == "1.0")
	
def generate_all():
	total = sum(s_first().combinations(PASSWORD_LENGTH))
	pct = total // 100

	print("Generating {0:d} phonemes".format(total), file=sys.stderr)

	count = 0
	maxProb = numpy.float128(0)

	try:
		for result in s_first().generate(PASSWORD_LENGTH):
			count += 1
			maxProb = max(maxProb, result.probability)
			print(result.password + "\t" + str(numpy.uint64(numpy.reciprocal(result.probability).round())))
			if count % pct == 0:
				print("Generated {0:d} ({1:d}%) - Max prob: {2:d}...".format(count, count // pct, int(numpy.reciprocal(maxProb).round())), file=sys.stderr)
		print("Completed, total={0:d}.".format(count), file=sys.stderr)
	except KeyboardInterrupt:
		print("Cancelled, total={0:d}.".format(count), file=sys.stderr)

if __name__ == "__main__":
	generate_all()

