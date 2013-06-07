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

class CharsetItem(tuple):
	def __new__(cls, c, flags):
		return tuple.__new__(cls, (c, flags))

	c = property(operator.itemgetter(0))
	flags = property(operator.itemgetter(1))
	
charset = [
	CharsetItem("a", VOWEL),
	CharsetItem("ae", VOWEL | DIPTHONG),
	CharsetItem("ah", VOWEL | DIPTHONG),
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
	CharsetItem("oh", VOWEL | DIPTHONG),
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
	def __init__(self, flags, weight, next_state, upper=False):
		self.flags = flags
		self.items = [ item for item in charset if item.flags == self.flags ]
		self.weight = numpy.float128(weight)
		self.itemWeight = self.weight / len(self.items)
		self.next_state = next_state
		self.upper = upper

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

def merge_and_sort(iterators):
	ilist = []
	for it in iterators:
		try:
			ilist.append((next(it), it))
		except StopIteration:
			pass

	while len(ilist) > 0:
		ilist.sort(key=operator.itemgetter(0))
		(item, it) = ilist.pop(-1)
		yield item
		try:
			ilist.append((next(it), it))
		except StopIteration:
			pass

def uniqify(iterators):
	it = merge_and_sort(iterators)

	lastItem = next(it)

	for item in it:
		if item.password == lastItem.password:
			lastItem += item
		else:
			yield lastItem
			lastItem = item
	yield lastItem

class Result(tuple):
	def __new__(cls, password, probability):
		return tuple.__new__(cls, (password, probability))

	password = property(operator.itemgetter(0))
	probability = property(operator.itemgetter(1))

	def __add__(self, other):
		assert(self.password == other.password)
		return self.__class__(self.password, self.probability + other.probability)

class State(object):
	def generate(self, sofar="", probability=1.0, generated_upper=False, generated_number=False):
		if len(sofar) == PASSWORD_LENGTH:
			if generated_upper and generated_number:
				yield Result(sofar, probability)
			return
		if len(sofar) > PASSWORD_LENGTH:
			return

		for pg in self.possibilities:
			children = [	possibility.next_state().generate(
						sofar+c,
						probability * weight,
						(generated_upper or possibility.upper),
						(generated_number or flags == NUMBER)
					)
				for possibility in pg
				for (c, flags, weight) in iter(possibility)
			]
			yield from uniqify(children)

	def combinations(self, combinations=1, length=0, haveUpper=False, haveNumber=False):
		if length == PASSWORD_LENGTH:
			if haveUpper and haveNumber:
				yield combinations
			else:
				yield 0
			return
		elif length > PASSWORD_LENGTH:
			yield 0
			return

		for pg in self.possibilities:
			for p in pg:
				c = len(list(iter(p)))
				s = p.next_state()
				yield sum(s.combinations(c, length + p.numchars, haveUpper or p.upper, haveNumber or p.flags == NUMBER)) * combinations
			

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
	[
		Possibility(VOWEL|DIPTHONG,	joint_weight(VOWEL|DIPTHONG, VOWEL) * 0.5 * 0.75, s_after_double_vowel),
		Possibility(VOWEL,		joint_weight(VOWEL, VOWEL|DIPTHONG) * 0.5 * 0.75, s_after_vowel),
	],
	[
		Possibility(VOWEL|DIPTHONG,	joint_weight(VOWEL|DIPTHONG, VOWEL) * 0.5 * 0.25, s_after_double_vowel, True),
		Possibility(VOWEL,		joint_weight(VOWEL, VOWEL|DIPTHONG) * 0.5 * 0.25, s_after_vowel, True),
	],
	[
		Possibility(CONSONANT|DIPTHONG,	joint_weight(CONSONANT|DIPTHONG, CONSONANT) * 0.5 * 0.75, s_after_consonant),
		Possibility(CONSONANT,		joint_weight(CONSONANT, CONSONANT|DIPTHONG) * 0.5 * 0.75, s_after_consonant),
	],
	[
		Possibility(CONSONANT|DIPTHONG,	joint_weight(CONSONANT|DIPTHONG, CONSONANT) * 0.5 * 0.25, s_after_consonant, True),
		Possibility(CONSONANT,		joint_weight(CONSONANT, CONSONANT|DIPTHONG) * 0.5 * 0.25, s_after_consonant, True),
	],
]

s_after_consonant.possibilities = [
	[	Possibility(NUMBER,		0.375, s_first), ],
	[
		Possibility(VOWEL|DIPTHONG,	joint_weight(VOWEL|DIPTHONG, VOWEL) * 0.625, s_after_double_vowel),
		Possibility(VOWEL,		joint_weight(VOWEL, VOWEL|DIPTHONG) * 0.625, s_after_vowel),
	],
]

s_after_vowel.possibilities = [
	[	Possibility(VOWEL, 0.625 * 0.25, s_after_double_vowel), ],
	[	Possibility(NUMBER, 0.375, s_first), ],
	[
		Possibility(CONSONANT|DIPTHONG, 		joint_weight(CONSONANT|DIPTHONG, CONSONANT, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.75 * 0.75, s_after_consonant),
		Possibility(CONSONANT,				joint_weight(CONSONANT, CONSONANT|DIPTHONG, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.75 * 0.75, s_after_consonant),
		Possibility(CONSONANT|DIPTHONG|NOT_FIRST, 	joint_weight(CONSONANT|DIPTHONG|NOT_FIRST, CONSONANT|DIPTHONG, CONSONANT) * 0.625 * 0.75 * 0.75, s_after_consonant),
	],
	[
		Possibility(CONSONANT|DIPTHONG, 		joint_weight(CONSONANT|DIPTHONG, CONSONANT, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.75 * 0.25, s_after_consonant, True),
		Possibility(CONSONANT,				joint_weight(CONSONANT, CONSONANT|DIPTHONG, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.75 * 0.25, s_after_consonant, True),
		Possibility(CONSONANT|DIPTHONG|NOT_FIRST, 	joint_weight(CONSONANT|DIPTHONG|NOT_FIRST, CONSONANT|DIPTHONG, CONSONANT) * 0.625 * 0.75 * 0.25, s_after_consonant, True),
	],
]

s_after_double_vowel.possibilities = [
	[	Possibility(NUMBER, 0.375, s_first), ],
	[
		Possibility(CONSONANT,				joint_weight(CONSONANT, CONSONANT|DIPTHONG, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.75, s_after_consonant),
		Possibility(CONSONANT|DIPTHONG,			joint_weight(CONSONANT|DIPTHONG, CONSONANT, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.75, s_after_consonant),
		Possibility(CONSONANT|DIPTHONG|NOT_FIRST,	joint_weight(CONSONANT|DIPTHONG|NOT_FIRST, CONSONANT, CONSONANT|DIPTHONG) * 0.625 * 0.75, s_after_consonant),
	],
	[
		Possibility(CONSONANT,				joint_weight(CONSONANT, CONSONANT|DIPTHONG, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.25, s_after_consonant, True),
		Possibility(CONSONANT|DIPTHONG,			joint_weight(CONSONANT|DIPTHONG, CONSONANT, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.25, s_after_consonant, True),
		Possibility(CONSONANT|DIPTHONG|NOT_FIRST,	joint_weight(CONSONANT|DIPTHONG|NOT_FIRST, CONSONANT, CONSONANT|DIPTHONG) * 0.625 * 0.25, s_after_consonant, True),
	],
]

## Check that no easily-spotted mistakes were made in probabilities
for s in (s_first, s_after_consonant, s_after_vowel, s_after_double_vowel):
	total_weight = numpy.array([p.weight for pg in s.possibilities for p in pg], dtype=numpy.float128).sum()
	# print(s.__name__ + ": " + str(total_weight), file=sys.stderr)
	assert(str(total_weight) == "1.0")
	
def generate_all():
	total = sum(s_first().combinations())
	pct = total // 100

	print("Generating {0:d} phonemes".format(total), file=sys.stderr)

	count = 0
	for result in s_first().generate():
		count += 1
		print(result.password + "\t" + str(numpy.uint64(numpy.reciprocal(result.probability).round())))
		if count % pct == 0:
			print("Generated {0:d} ({1:d}%)...".format(count, count // pct), file=sys.stderr)
	print("Completed, total={0:d}...".format(count), file=sys.stderr)

if __name__ == "__main__":
	generate_all()

