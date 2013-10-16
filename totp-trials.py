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
import sys
from multiprocessing import Pool

NUM_TRIALS=16
NUM_USERS=[ 1, 10, 100, 1000, 5000, 10000, 15000, 20000 ]

def DT(value):
	"""Use the last byte % 16 to determine which 4 bytes
	   will be converted to a 31-bit integer, and return it"""
	offset = value[-1] & 15
	return ((value[offset] & 0x7f) << 24) | ((value[offset+1] & 0xff) << 16) | ((value[offset+2] & 0xff) << 8) | (value[offset+3] & 0xff)

def hotp(k, c):
	"""x := HMAC-k(c) ; return DT(x) mod 1000000"""
	mac = k.copy()
	mac.update(c.to_bytes(8, "big"))
	return DT(mac.digest()) % 1000000

def validate_simple(user, c, n):
	"""Just see if the HOTP matches"""
	return n == hotp(user, c)

def validate_drift(user, c, n):
	"""Accept c-1 and c-2 too"""
	if n == hotp(user, c):
		return True
	elif n == hotp(user, c-1):
		return True
	elif n == hotp(user, c-2):
		return True
	else:
		return False

def get_c():
	"""Return a counter value"""
	return int(time.time()) // 30

def make_keys(num_users):
	return [ hmac.new(os.urandom(16), digestmod=hashlib.sha1) for _ in range(num_users) ]

def attack_simple(users):
	"""Try guessing a random value for 1m accounts"""
	n = 123456
	breaks = 0

	c = get_c()
	for user in users:
		if validate_simple(user, c, n):
			breaks += 1
	return breaks
	

def attack_drift(users):
	"""Try guessing a random value for 1m accounts on a server that accounts for drift"""
	n = 123456
	breaks = 0

	c = get_c()
	for user in users:
		if validate_drift(user, c, n):
			breaks += 1
	return breaks

def attack_until_win(users):
	"""See how many tries before we get into 1 account, taking into account
	   the recommended backoffs in RFC4226"""
	i = 0
	tries = 0
	n = 123456
	c = get_c()

	while True:
		tries += 1
		for user in users:
			if validate_drift(user, c, n):
				return tries
		c += (tries * 5) // 30
		n = (n + 1) % 483647 # Change n to benefit from drift

def run_attack(_x):
	return [ attack_until_win(make_keys(num_users)) for num_users in NUM_USERS ]

if __name__ == "__main__":
	results = numpy.empty((NUM_TRIALS, len(NUM_USERS)), dtype=numpy.uint64)
	p = Pool()

	for i, result in enumerate(p.map(run_attack, range(NUM_TRIALS))):
		for j in range(len(result)):
			results[i,j] = result[j]
	numpy.savetxt("totp-trials.csv", results.T, fmt="%d", delimiter=",")

