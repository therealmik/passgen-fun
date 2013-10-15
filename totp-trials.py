#!/usr/bin/python3

"""
Basic proof of concept for attacks on HOTP/TOTP systems
-------------------------------------------------------
Public Domain 2013, Michael Samuel

From the perspective of a spammer (or service provider), it doesn't matter which
account is compromised - you just need at-least one to start a spam run.

So, armed with a whole bunch of "first factors" (eg. email address + password for
another site), how long does it take to break the TOTP system as specified in
RFC6238?

This program simulates this scenario in a variety of ways.  Please read the
source.
"""

import numpy
import os
import time
import hashlib
import hmac
from multiprocessing import Pool

NUM_TRIALS=64
NUM_KEYS=1000000

def DT(value):
	"""Use the last byte % 16 to determine which 4 bytes
	   will be converted to a 31-bit integer, and return it"""
	offset = value[-1] & 15
	return ((value[offset] & 0x7f) << 24) | ((value[offset+1] & 0xff) << 16) | ((value[offset+2] & 0xff) << 8) | (value[offset+3] & 0xff)

def hotp(k, c):
	"""x := HMAC-k(c) ; return DT(x) mod 1000000"""
	mac = hmac.new(k, c.to_bytes(8, "big"), digestmod=hashlib.sha1)
	return DT(mac.digest()) % 1000000

def validate_simple(KEYS, c, i, n):
	"""Just see if the HOTP matches"""
	return n == hotp(KEYS[i], c)

def validate_drift(KEYS, c, i, n):
	"""Accept c-1 and c-2 too"""
	if n == hotp(KEYS[i], c):
		return True
	elif n == hotp(KEYS[i], c):
		return True
	elif n == hotp(KEYS[i], c):
		return True
	else:
		return False

def get_c():
	"""Return a counter value"""
	return int(time.time()) // 30

def attack_simple(KEYS):
	"""Try guessing a random value for 1m accounts"""
	n = 123456
	breaks = 0

	c = get_c()
	for i in range(NUM_KEYS):
		if validate_simple(KEYS, c, i, n):
			breaks += 1
	return breaks
	

def attack_drift(KEYS):
	"""Try guessing a random value for 1m accounts on a server that accounts for drift"""
	n = 123456
	breaks = 0

	c = get_c()
	for i in range(NUM_KEYS):
		if validate_drift(KEYS, c, i, n):
			breaks += 1
	return breaks

def attack_3_guesses(KEYS):
	"""Same as attack_drift, but have 3 guesses"""
	N = [ 123456, 234567, 3456 ]
	breaks = 0

	c = get_c()
	for i in range(NUM_KEYS):
		for n in N:
			if validate_drift(KEYS, c, i, n):
				breaks += 1
				break
	return breaks

def attack_over_time(KEYS, num_users=1):
	"""See how many tries before we get into 1 account - 1 try per time interval.
	   We change n each time to benefit from the drift check"""
	i = 0
	tries = 0
	N = numpy.random.randint(0, 483647, num_users)
	c = get_c()
	while True:
		tries += 1
		for n in N:
			if validate_drift(KEYS, c, i, n):
				break
		c += 1
		N = (N + 1) % 483647
	return tries

def make_keys():
	return [ os.urandom(16) for _ in range(NUM_KEYS) ]

def run_attack(i):
	KEYS = make_keys()
	results = [ attack_simple(KEYS), attack_drift(KEYS), attack_3_guesses(KEYS), attack_over_time(KEYS, 1), attack_over_time(KEYS, 10) ]
	results.append(numpy.sum(numpy.arange(results[3]) * 5))
	results.append(numpy.sum(numpy.arange(results[4]) * 5))
	return (i, results)

if __name__ == "__main__":
	results = numpy.empty((NUM_TRIALS, 7), dtype=numpy.uint64)
	p = Pool()

	for i, result in p.map(run_attack, range(NUM_TRIALS)):
		for j in range(7):
			results[i, j] = result[j]
	numpy.savetxt("totp-trials.csv", results, fmt="%d", delimiter=",")

