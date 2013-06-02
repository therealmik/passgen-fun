#!/usr/bin/python3

"""
Generate all possible pwgen phonemes (the default mode)

This is a recursive generator function that tries to generate all
possible pwgen phonemes, along with their probabilities.

FIXME: The probabilities are almost certainly wrong (eg. won't add up to 1)
TODO: Merge duplicate branches

A full run with 6 chars produced 1532036600 possibilities

Some are still missing that shouldn't be:
Aa4Yah
ley9Ao
Au5hoo
Oi9UR0
goa2Eu
eiH5Iu
Uav5ie
eiL5Ao
Uun2Fe
Eu1zae
hah1Oa
Iokai3
Uacah0
""" 

import operator

PASSWORD_LENGTH=6

CONSONANT = 1
VOWEL = 2
DIPTHONG = 4
NOT_FIRST = 8

UPPER=1
NUMBER=2
SYMBOL=4

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
]

def generate_first(sofar="", probability=1.0, generated_upper=False, generated_number=False):
	"""Generate a first char.  This means either the first char, or after a number."""
	### BOILERPLATE ###
	if len(sofar) == PASSWORD_LENGTH:
		if generated_upper and generated_number:
			yield (sofar, probability)
		return
	if len(sofar) > PASSWORD_LENGTH:
		return

	next_level = []
	### END BOILERPLATE ###

	for(x, flags, p) in charset:
		if flags & NOT_FIRST != 0:
			continue

		if flags & CONSONANT != 0:
			next_level.append([probability*p,	generate_vowel(sofar + x, flags, probability*p, generated_upper, generated_number)])
			next_level.append([probability*p*0.25,	generate_vowel(sofar + x.capitalize(), flags, probability*p*0.25, True, generated_number)])
		else: # flags & VOWEL != 0:
			next_level.append([probability*p*0.25,	generate_consonant(sofar+x.capitalize(), flags, probability*p*0.25, True, generated_number)])
			if flags & DIPTHONG != 0:
				next_level.append([probability*p,	generate_consonant(sofar+x, flags, probability*p, generated_upper, generated_number)])
			else:
				next_level.append([probability*p,	generate_vowel(sofar+x, flags, probability*p, generated_upper, generated_number)])
				next_level.append([probability*p*0.5,	generate_consonant(sofar+x, flags, probability*p*0.5, generated_upper, generated_number)])

	### BOILERPLATE ###
	next_level.sort(key=operator.itemgetter(0), reverse=True)
	for _, gen in next_level:
		for y in gen:
			yield y
	### END BOILERPLATE ###

def generate_consonant(sofar, prev, probability, generated_upper, generated_number):
	### BOILERPLATE ###
	if len(sofar) == PASSWORD_LENGTH:
		if generated_upper and generated_number:
			yield (sofar, probability)
		return
	if len(sofar) > PASSWORD_LENGTH:
		return

	next_level = []
	### END BOILERPLATE ###

	for(x, flags, p) in charset:
		if flags & CONSONANT == 0:
			continue
		next_level.append([probability*p,	generate_vowel(sofar + x, flags, probability*p, generated_upper, generated_number)])
		next_level.append([probability*p*0.25,	generate_vowel(sofar + x.capitalize(), flags, probability*p*0.25, True, generated_number)])

	for x, p in [(str(x), 2.0/16) for x in range(0, 6)] + [(str(x), 1.0/16) for x in range(6, 10)]:
		next_level.append([probability*p*0.375,	generate_first(sofar+x, probability*p*0.375, generated_upper, True)])

	### BOILERPLATE ###
	next_level.sort(key=operator.itemgetter(0), reverse=True)
	for _, gen in next_level:
		for y in gen:
			yield y
	### END BOILERPLATE ###

def generate_vowel(sofar, prev, probability, generated_upper, generated_number):
	### BOILERPLATE ###
	if len(sofar) == PASSWORD_LENGTH:
		if generated_upper and generated_number:
			yield (sofar, probability)
		return
	if len(sofar) > PASSWORD_LENGTH:
		return

	next_level = []
	### END BOILERPLATE ###

	for(x, flags, p) in charset:
		if flags & VOWEL == 0:
			continue
		if prev & VOWEL != 0 or flags & DIPTHONG != 0:
			next_level.append([probability*p,	generate_consonant(sofar + x, flags, probability*p, generated_upper, generated_number)])
		else:
			next_level.append([probability*p,	generate_vowel(sofar + x, flags, probability*p, generated_upper, generated_number)])
			next_level.append([probability*p*0.5,	generate_consonant(sofar + x, flags, probability*p*0.5, generated_upper, generated_number)])

	for x, p in [(str(x), 2.0/16) for x in range(0, 6)] + [(str(x), 1.0/16) for x in range(6, 10)]:
		next_level.append([probability*p*0.375,	generate_first(sofar+x, probability*p*0.375, generated_upper, True)])

	### BOILERPLATE ###
	next_level.sort(key=operator.itemgetter(0), reverse=True)
	for _, gen in next_level:
		for y in gen:
			yield y
	### END BOILERPLATE ###

def generate_pwgen(sofar="", first=True, should_be=VOWEL|CONSONANT, prev=0, probability=1.0, generated_upper=False, generated_number=False):
	"""Original generator func - don't use"""
	if len(sofar) == PASSWORD_LENGTH:
		if generated_upper and generated_number:
			yield (sofar, probability)
		return
	if len(sofar) > PASSWORD_LENGTH:
		return

	next_level = []

	for(x, flags, p) in charset:
		if flags & should_be == 0:
			continue
		if first and flags & NOT_FIRST != 0:
			continue
		if prev & VOWEL != 0 and flags & VOWEL != 0 and flags & DIPTHONG != 0:
			continue

		if flags & CONSONANT != 0:
			next_level.append((sofar+x, False, VOWEL, flags, probability*p, generated_upper, generated_number))
			next_level.append((sofar+x.capitalize(), False, VOWEL, flags, probability*p*0.25, True, generated_number))
		else:
			if first:
				next_level.append((sofar+x.capitalize(), False, CONSONANT, flags, probability*p*0.25, True, generated_number))
			if prev & VOWEL != 0 or flags & DIPTHONG != 0:
				next_level.append((sofar+x, False, CONSONANT, flags, probability*p, generated_upper, generated_number))
			else:
				next_level.append((sofar+x, False, VOWEL, flags, probability*p, generated_upper, generated_number))
				next_level.append((sofar+x, False, CONSONANT, flags, probability*p*0.5, generated_upper, generated_number))

	if not first:
		for x, p in [(str(x), 2.0/16) for x in range(0, 6)] + [(str(x), 1.0/16) for x in range(6, 10)]:
			next_level.append((sofar+x, True, VOWEL|CONSONANT, 0, probability*p*0.375, generated_upper, True))

	next_level.sort(key=operator.itemgetter(4), reverse=True)
	for args in next_level:
		for y in generate_pwgen(*args):
			yield y

if __name__ == "__main__":
	import sys

	count = 0
	for (x, probability) in generate_first():
		count += 1
		print(x) # + "\t" + str(probability))
		if count % 10000000 == 0:
			print("Generated {0:d}...".format(count), file=sys.stderr)
			sys.stderr.flush()
	print("Completed, total={0:d}...".format(count), file=sys.stderr)
	sys.stderr.flush()

