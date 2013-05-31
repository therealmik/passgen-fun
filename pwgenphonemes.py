#!/usr/bin/python3

"""
Generate all possible pwgen phonemes (the default mode)

This is a recursive generator function that tries to generate all
possible pwgen phonemes, along with their probabilities.

FIXME: The sum of all probabilities is 0.0236533250995308
FIXME: Satoo9 and fohNg5 are not generated!!!
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

def generate_pwgen(sofar="", first=True, should_be=VOWEL|CONSONANT, prev=0, feature_flags=NUMBER|UPPER, pw_flags=NUMBER|UPPER, probability=1.0):
	if len(sofar) == PASSWORD_LENGTH:
		if feature_flags == 0:
			yield (sofar, probability)
		return
	if len(sofar) > PASSWORD_LENGTH:
		return

	next_level = []

	for(x, flags, p) in charset:
		if flags & should_be == 0:
			continue
		if prev & VOWEL != 0 and flags & VOWEL|DIPTHONG != 0:
			continue

		if flags & CONSONANT != 0:
			p *= 0.5
			next_level.append((p, (sofar+x, False, VOWEL, flags, feature_flags, pw_flags)))
			if pw_flags & UPPER != 0:
				next_level.append((p*0.25, (sofar+x.capitalize(), False, VOWEL, flags, feature_flags & (~UPPER), pw_flags)))
		else:
			p *= 0.5
			cp = p # CONSONANT probability

			if first and pw_flags & UPPER != 0:
				next_level.append((p*0.25, (sofar+x.capitalize(), False, CONSONANT, flags, feature_flags & (~UPPER), pw_flags)))
			if prev & VOWEL == 0 and flags & DIPTHONG == 0:
				cp *= 0.5 # or 0.4 without the bias
				next_level.append((p, (sofar+x, False, VOWEL, flags, feature_flags, pw_flags)))
				if first and pw_flags & UPPER != 0:
					next_level.append((p*0.25, (sofar+x.capitalize(), False, VOWEL, flags, feature_flags & (~UPPER), pw_flags)))
			next_level.append((cp, (sofar+x, False, CONSONANT, flags, feature_flags, pw_flags)))

	if pw_flags & NUMBER != 0 and not first:
		for x, p in [(str(x), 2.0/16) for x in range(0, 6)] + [(str(x), 1.0/16) for x in range(6, 10)]:
			next_level.append((p*0.375, (sofar+x, True, VOWEL|CONSONANT, 0, feature_flags & (~NUMBER), pw_flags)))

	next_level.sort(key=operator.itemgetter(0), reverse=True)
	for (p, args) in next_level:
		for y in generate_pwgen(*args, probability=probability*p):
			yield y

if __name__ == "__main__":
	import sys

	count = 0
	print("\copy pwgen from pstdin with delimiter '\t'")
	for (x, probability) in generate_pwgen():
		count += 1
		print(x + "\t" + str(probability))
		if count % 10000000 == 0:
			print("Generated {0:d}...".format(count), file=sys.stderr)
			sys.stderr.flush()
	print("Completed, total={0:d}...".format(count), file=sys.stderr)
	sys.stderr.flush()


