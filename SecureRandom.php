<?php

/* SecureRandom wrapper for PHP5
 * Public Domain 2013, Michael Samuel
 *
 * This library is a small wrapper around the available
 * CSPRNG sources available to PHP apps.
 *
 * I have refrained from implementing any custom sources
 * based on builtin functions (such as md5) as it would
 * be vastly lower quality (and probably slower).
 *
 * An environment that lacks all of these entropy sources
 * is very unlikely to be able to achive a reasonable
 * level of security in any case.  Better that they realise
 * that before somebody else does.
 *
 * Basic usage:
 * $rng = secure_random_factory();
 * $number = $rng->rand(5, 10); // Pick a number in the range [5..10]
 * $char = $rng->choose("abcdefg");
 * $item = $rng->choose(array("Dog", "Cat", "Bird", "Rock"));
 */

abstract class SecureRandom {
	abstract public function get_random_bytes($count);
	abstract public static function is_available();

	public static function num_bits($number) {
		$bits = 0;

		while($number > 0)
		{
			$number >>= 1;
			$bits += 1;
		}

		return $bits;
	}

	public function rand($min, $max=0) {
		// Return a number in the range [ $min .. $max ].
		// if only 1 argument is present it is treated
		// as $max, while $min is assumed to be 0.
		if($min > $max) {
			$tmp = $max;
			$max = $min;
			$min = $tmp;
		}

		$real_max = $max - $min;
		$mask = (1 << $this->num_bits($real_max)) - 1;

		do {
			$bytes = $this->get_random_bytes(4);
			$integer = unpack("lnum", $bytes)["num"] & $mask;
		} while ($integer > $real_max);

		return $integer + $min;
	}

	public function choose($arry) {
		if(gettype($arry) == "string") {
			$size = strlen($arry);
		} else {
			$size = count($arry);
		}
		// Choose a random element of an array
		return $arry[$this->rand($size - 1)];
	}
}

class DevURandom extends SecureRandom {
	var $fh;

	public function DevURandom($filename="/dev/urandom")
	{
		$this->fh = fopen("/dev/urandom", "rb");
	}

	public function get_random_bytes($count)
	{
		$output = '';

		do {
			$output .= fread($this->fh, $count - strlen($output));
		} while (strlen($output) < $count);
		return $output;
	}

	public static function is_available()
	{
		if(PHP_OS == "WINNT") {
			return FALSE; // We can't guarantee /dev/urandom is safe to open on Windows
		}
		return @is_readable('/dev/urandom');
	}
}

class WindowsCOMRandom extends SecureRandom {
	var $CAPI;

	public function WindowsCOMRandom()
	{
		$this->$CAPI = new COM('CAPICOM.Utilities.1');
	}

	public function get_random_bytes($count)
	{
		return $this->CAPI->GetRandom($count, 2);
	}

	public static function is_available()
	{
		return @class_exists('COM');
	}
}

class OpenSSLRandom extends SecureRandom {
	public function get_random_bytes($count)
	{
		$strong = FALSE;
		$output = openssl_random_pseudo_bytes($count, $strong);
		assert($strong); // This must be true or your platform is broken
		return $output;
	}

	public static function is_available()
	{
		if(!@function_exists('openssl_random_pseudo_bytes')) {
			return FALSE;
		}
		$strong = FALSE;
		openssl_random_pseudo_bytes(1, $strong);
		return $strong;
	}
}

function secure_random_factory()
{
	// The native PRNG is best and least problematic on Windows platforms
	if(WindowsCOMRandom::is_available()) {
		return new WindowsCOMRandom();
	}

	// /dev/urandom is available on most sane platforms.
	if(DevURandom::is_available()) {
		return new DevURandom();
	}

	// OpenSSL might know how to find some strong entropy
	if(OpenSSLRandom::is_available()) {
		return new OpenSSLRandom();
	}

	// There is zero change of you having a secure webapp if it
	// can't find any entropy.  If you are on a shared hosting
	// provider, you need to find a new one.
	throw new Exception("Unable to find secure entropy source");
}

function secure_random_tests()
{
	$rand = secure_random_factory();
	$results = array(0, 0, 0, 0, 0, 0, 0, 0, 0, 0);

	for($i = 0; $i < 10000000; $i++) {
		$results[$rand->rand(count($results)-1)]++;
	}
	print_r($results);
}
		
/* Statistical tests - Uncomment and run with php5-cli to test your platform

secure_random_tests();

 */

?>
