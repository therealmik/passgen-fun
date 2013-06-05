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
	def __new__(cls, c, flags, weight):
		return tuple.__new__(cls, (c, flags, numpy.float128(weight)))

	c = property(operator.itemgetter(0))
	flags = property(operator.itemgetter(1))
	weight = property(operator.itemgetter(2))
	
charset = [
	CharsetItem("a", VOWEL, 2.0/64),
	CharsetItem("ae", VOWEL | DIPTHONG, 2.0/64),
	CharsetItem("ah", VOWEL | DIPTHONG, 2.0/64),
	CharsetItem("ai", VOWEL | DIPTHONG, 2.0/64),
	CharsetItem("b", CONSONANT, 2.0/64),
	CharsetItem("c", CONSONANT, 2.0/64),
	CharsetItem("ch", CONSONANT | DIPTHONG, 2.0/64),
	CharsetItem("d", CONSONANT, 2.0/64),
	CharsetItem("e", VOWEL, 2.0/64),
	CharsetItem("ee", VOWEL | DIPTHONG, 2.0/64),
	CharsetItem("ei", VOWEL | DIPTHONG, 2.0/64),
	CharsetItem("f", CONSONANT, 2.0/64),
	CharsetItem("g", CONSONANT, 2.0/64),
	CharsetItem("gh", CONSONANT | DIPTHONG | NOT_FIRST, 2.0/64),
	CharsetItem("h", CONSONANT, 2.0/64),
	CharsetItem("i", VOWEL, 2.0/64),
	CharsetItem("ie", VOWEL | DIPTHONG, 2.0/64),
	CharsetItem("j", CONSONANT, 2.0/64),
	CharsetItem("k", CONSONANT, 2.0/64),
	CharsetItem("l", CONSONANT, 2.0/64),
	CharsetItem("m", CONSONANT, 2.0/64),
	CharsetItem("n", CONSONANT, 2.0/64),
	CharsetItem("ng", CONSONANT | DIPTHONG | NOT_FIRST, 2.0/64),
	CharsetItem("o", VOWEL, 2.0/64),
	CharsetItem("oh", VOWEL | DIPTHONG, 1.0/64),
	CharsetItem("oo", VOWEL | DIPTHONG, 1.0/64),
	CharsetItem("p", CONSONANT, 1.0/64),
	CharsetItem("ph", CONSONANT | DIPTHONG, 1.0/64),
	CharsetItem("qu", CONSONANT | DIPTHONG, 1.0/64),
	CharsetItem("r", CONSONANT, 1.0/64),
	CharsetItem("s", CONSONANT, 1.0/64),
	CharsetItem("sh", CONSONANT | DIPTHONG, 1.0/64),
	CharsetItem("t", CONSONANT, 1.0/64),
	CharsetItem("th", CONSONANT | DIPTHONG, 1.0/64),
	CharsetItem("u", VOWEL, 1.0/64),
	CharsetItem("v", CONSONANT, 1.0/64),
	CharsetItem("w", CONSONANT, 1.0/64),
	CharsetItem("x", CONSONANT, 1.0/64),
	CharsetItem("y", CONSONANT, 1.0/64),
	CharsetItem("z", CONSONANT, 1.0/64),
]
charset.extend([CharsetItem(str(x), NUMBER, 2.0/16) for x in range(0, 6)])
charset.extend([CharsetItem(str(x), NUMBER, 1.0/16) for x in range(6, 10)])

class Possibility(object):
	def __init__(self, flags, weight, next_state, upper=False):
		self.flags = flags
		self.weight = numpy.float128(weight)
		self.next_state = next_state
		self.upper = upper

	def __iter__(self):
		items = [ item for item in charset if item.flags == self.flags ]
		wFactor = 1.0 / sum([ item.weight for item in items ])
		for item in items:
			c = item.c
			if self.upper:
				c = c.capitalize()
			yield (c, item.flags, item.weight*wFactor*self.weight)
		
	@property
	def numchars(self):
		if self.flags & DIPTHONG != 0:
			return 2
		else:
			return 1

def uniqify(iterators):
	it = heapq.merge(*iterators)

	(lastItem, p) = next(it)

	for item in it:
		if item[0] == lastItem:
			p += item[1]
		else:
			if lastItem is not None:
				yield (lastItem, p)
			lastItem = item[0]
			p = item[1]

class Result(tuple):
	def __new__(cls, password, probability):
		return tuple.__new__(cls, (password, probability))

	password = property(operator.itemgetter(0))
	probability = property(operator.itemgetter(1))

	def __lt__(self, item):
		# FIXME: Make the sort order more awesome
		return self.password < item.password

	def __gt__(self, item):
		# FIXME: Make the sort order more awesome
		return self.password > item.password

	def __eq__(self, item):
		return self.password == item.password

	def __ne__(self, item):
		return self.password != item.password



class State(object):
	def __init__(self, sofar="", probability=1.0, generated_upper=False, generated_number=False):
		self.sofar = sofar
		self.probability = numpy.float128(probability)
		self.generated_upper = generated_upper
		self.generated_number = generated_number

	def __iter__(self):
		if len(self.sofar) == PASSWORD_LENGTH:
			if self.generated_upper and self.generated_number:
				yield Result(self.sofar, self.probability)
			return
		if len(self.sofar) > PASSWORD_LENGTH:
			return

		for possibility in self.possibilities:
			children = []
			children = [ iter(possibility.next_state(self.sofar+c, self.probability * weight, (self.generated_upper or possibility.upper), (self.generated_number or flags == NUMBER))) for (c, flags, weight) in iter(possibility) ]
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

		for p in self.possibilities:
			c = len(list(iter(p)))
			s = p.next_state("x" * length)
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
	Possibility(VOWEL|DIPTHONG,	joint_weight(VOWEL|DIPTHONG, VOWEL) * 0.5 * 0.75, s_after_double_vowel),
	Possibility(VOWEL,		joint_weight(VOWEL, VOWEL|DIPTHONG) * 0.5 * 0.75, s_after_vowel),
	Possibility(VOWEL|DIPTHONG,	joint_weight(VOWEL|DIPTHONG, VOWEL) * 0.5 * 0.25, s_after_double_vowel, True),
	Possibility(VOWEL,		joint_weight(VOWEL, VOWEL|DIPTHONG) * 0.5 * 0.25, s_after_vowel, True),
	Possibility(CONSONANT|DIPTHONG,	joint_weight(CONSONANT|DIPTHONG, CONSONANT) * 0.5 * 0.75, s_after_consonant),
	Possibility(CONSONANT,		joint_weight(CONSONANT, CONSONANT|DIPTHONG) * 0.5 * 0.75, s_after_consonant),
	Possibility(CONSONANT|DIPTHONG,	joint_weight(CONSONANT|DIPTHONG, CONSONANT) * 0.5 * 0.25, s_after_consonant, True),
	Possibility(CONSONANT,		joint_weight(CONSONANT, CONSONANT|DIPTHONG) * 0.5 * 0.25, s_after_consonant, True),
]

s_after_consonant.possibilities = [
	Possibility(VOWEL|DIPTHONG,	joint_weight(VOWEL|DIPTHONG, VOWEL) * 0.625, s_after_double_vowel),
	Possibility(VOWEL,		joint_weight(VOWEL, VOWEL|DIPTHONG) * 0.625, s_after_vowel),
	Possibility(NUMBER,		0.375, s_first),
]

s_after_vowel.possibilities = [
	Possibility(VOWEL, 0.625 * 0.25, s_after_double_vowel),
	Possibility(NUMBER, 0.375, s_first),
	Possibility(CONSONANT|DIPTHONG, 		joint_weight(CONSONANT|DIPTHONG, CONSONANT, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.75 * 0.75, s_after_consonant),
	Possibility(CONSONANT,				joint_weight(CONSONANT, CONSONANT|DIPTHONG, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.75 * 0.75, s_after_consonant),
	Possibility(CONSONANT|DIPTHONG|NOT_FIRST, 	joint_weight(CONSONANT|DIPTHONG|NOT_FIRST, CONSONANT|DIPTHONG, CONSONANT) * 0.625 * 0.75 * 0.75, s_after_consonant),
	Possibility(CONSONANT|DIPTHONG, 		joint_weight(CONSONANT|DIPTHONG, CONSONANT, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.75 * 0.25, s_after_consonant, True),
	Possibility(CONSONANT,				joint_weight(CONSONANT, CONSONANT|DIPTHONG, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.75 * 0.25, s_after_consonant, True),
	Possibility(CONSONANT|DIPTHONG|NOT_FIRST, 	joint_weight(CONSONANT|DIPTHONG|NOT_FIRST, CONSONANT|DIPTHONG, CONSONANT) * 0.625 * 0.75 * 0.25, s_after_consonant, True),
]

s_after_double_vowel.possibilities = [
	Possibility(NUMBER, 0.375, s_first),
	Possibility(CONSONANT,				joint_weight(CONSONANT, CONSONANT|DIPTHONG, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.75, s_after_consonant),
	Possibility(CONSONANT|DIPTHONG,			joint_weight(CONSONANT|DIPTHONG, CONSONANT, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.75, s_after_consonant),
	Possibility(CONSONANT|DIPTHONG|NOT_FIRST,	joint_weight(CONSONANT|DIPTHONG|NOT_FIRST, CONSONANT, CONSONANT|DIPTHONG) * 0.625 * 0.75, s_after_consonant),
	Possibility(CONSONANT,				joint_weight(CONSONANT, CONSONANT|DIPTHONG, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.25, s_after_consonant, True),
	Possibility(CONSONANT|DIPTHONG,			joint_weight(CONSONANT|DIPTHONG, CONSONANT, CONSONANT|DIPTHONG|NOT_FIRST) * 0.625 * 0.25, s_after_consonant, True),
	Possibility(CONSONANT|DIPTHONG|NOT_FIRST,	joint_weight(CONSONANT|DIPTHONG|NOT_FIRST, CONSONANT, CONSONANT|DIPTHONG) * 0.625 * 0.25, s_after_consonant, True),
]

for s in (s_first, s_after_consonant, s_after_vowel, s_after_double_vowel):
	assert(str(numpy.array([p.weight for p in s.possibilities], dtype=numpy.float128).sum()) == "1.0")
	
if __name__ == "__main__":
	import sys

	total = sum(s_first().combinations())
	pct = total // 100

	print("Generating {0:d} phonemes".format(total), file=sys.stderr)

	maxProb = numpy.float128(0.0)
	count = 0
	for (x, probability) in iter(s_first()):
		count += 1
		if probability >= maxProb:
			print(x + "\t" + str(numpy.uint64((1.0/probability).round())))
			maxProb = probability
		if count % pct == 0:
			print("Generated {0:d} ({1:d}%)...".format(count, count // pct), file=sys.stderr)
	print("Completed, total={0:d}...".format(count), file=sys.stderr)

