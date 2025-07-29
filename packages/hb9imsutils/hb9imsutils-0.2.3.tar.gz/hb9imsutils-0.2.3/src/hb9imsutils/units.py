import numpy as np


def unitprint_block(value, /, unit=None, power=None):
	"""
	Format a number to engineering units and prefixes.
	Special padding for cell-like output
	"""

	if unit is None:
		unit = " "
	original_value = value
	sign = " "
	log1000 = 0
	if value != 0:
		if value < 0:
			sign = "-"
			value *= -1
		log1000 = np.log10(value) // (3 * (power if power is not None else 1))
		value *= 1000 ** (-log1000 * (power if power is not None else 1))

	if abs(log1000) > 10:
		return f"{sign}{f'{abs(original_value):.3e}': >7}{unit}"

	prefix = {0: "",
			  -1: "m", -2: "µ", -3: "n", -4: "p", -5: "f",
			  -6: "a", -7: "z", -8: "y", -9: "r", -10: "q",
			  1: "k", 2: "M", 3: "G", 4: "T", 5: "P",
			  6: "E", 7: "Z", 8: "Y", 9: "R", 10: "Q",
			  }[log1000]

	return f"{sign}{f'{value:.3f}': >7} {prefix or ' '}{unit}" \
		   f"{(f'^{power}' if power is not None else '')}"


def unitprint(value, /, unit=None, power=None):
	"""
	Format a number to engineering units and prefixes.
	"""

	if unit is None:
		unit = " "
	original_value = value
	sign = " "
	log1000 = 0
	if value != 0:
		if value < 0:
			sign = "-"
			value *= -1
		log1000 = np.log10(value) // (3 * (power if power is not None else 1))
		value *= 1000 ** (-log1000 * (power if power is not None else 1))

	if abs(log1000) > 10:
		return f"{sign}{f'{abs(original_value):.3e}': >7}{unit}"

	prefix = {0: "",
			  -1: "m", -2: "µ", -3: "n", -4: "p", -5: "f",
			  -6: "a", -7: "z", -8: "y", -9: "r", -10: "q",
			  1: "k", 2: "M", 3: "G", 4: "T", 5: "P",
			  6: "E", 7: "Z", 8: "Y", 9: "R", 10: "Q",
			  }[log1000]

	return f"{value:.3f} {prefix}{unit}" \
		   f"{(f'^{power}' if power is not None else '')}"


def unitprint2(value, /, unit=None):
	"""
	Format a number to engineering units and prefixes, base2
	Does not support exponents < 0 and values < 1, except for 0
	"""

	if unit is None:
		unit = " "
	original_value = value
	sign = " "
	log1024 = 0
	if value != 0:
		if value < 0:
			raise ValueError(
				"Negative base2 units are not supported "
				"(it doesn't make sense to have negative bytes)"
				)
		log1024 = max(np.log2(value), 0) // 10
		value *= 1024 ** (-log1024)

	if log1024 > 10:
		b = np.floor(np.log2(value))
		a = value / 2**b
		return f"{a:.4f}{b}"

	prefix = {0: "",
			  1: "ki", 2: "Mi", 3: "Gi", 4: "Ti", 5: "Pi",
			  6: "Ei", 7: "Zi", 8: "Yi", 9: "Ri", 10: "Qi",
			  }[log1024]

	if prefix == "":
		return f"{np.ceil(value):0.0f} {unit}"

	return f"{value:.3f} {prefix}{unit}"


def unitprint2_block(value, /, unit=None):
	"""
	Format a number to engineering units and prefixes, base2
	Does not support exponents < 0 and values < 1, except for 0
	"""

	if unit is None:
		unit = " "
	original_value = value
	sign = " "
	log1024 = 0
	if value != 0:
		if value < 0:
			raise ValueError(
				"Negative base2 units are not supported "
				"(it doesn't make sense to have negative bytes)"
				)
		log1024 = max(np.log2(value), 0) // 10
		value *= 1024 ** (-log1024)

	if log1024 > 10:
		b = np.floor(np.log2(value))
		a = value / 2**b
		return f"{a:.4f}{b}"

	prefix = {0: "",
			  1: "ki", 2: "Mi", 3: "Gi", 4: "Ti", 5: "Pi",
			  6: "Ei", 7: "Zi", 8: "Yi", 9: "Ri", 10: "Qi",
			  }[log1024]

	if prefix == "":
		return f"{ceil(value):0.0f}   {unit or ' '}"

	return f"{value:3.3f} {prefix}{unit or ' '}"


def number_converter(strin: str, /, power=1, _avoid_recursion_again=False):
	"""Returns a float from a number like 5k6 -> 5.6e3"""

	letters = {-1: "m", -2: "u", -3: "n", -4: "p", -5: "f", -6: "a",
			   1: "k",  2: "meg",  3: "gig",  4: "ter",  5: "pet",  6: "ex"}
	result_letter = "."
	result_exponent = 0
	for exponent, letter in letters.items():
		if letter in strin:
			result_letter = letter
			result_exponent = exponent
			break
	if result_exponent == 0:
		split_strings = strin.split(".", 1)
		if len(split_strings) == 1:
			split_strings.append('')
		if (strin.count(".") <= 1 
			and "".join(split_strings).replace("e", "", 1).isnumeric()
			and "e" not in split_strings[0]
			and split_strings[1].count("e") <= 1
		):
			return float(strin)
		else:
			return None

	if not "".join(strin.split(result_letter)).isnumeric():
		# Heck me recursion
		if not _avoid_recursion_again and (res := number_converter(
			    strin
			    .replace(result_letter, "", 1)
			    .replace(".", result_letter),
			    _avoid_recursion_again=True
			)) is not None:
			return res
		return None

	return float(".".join(strin.split(result_letter))) \
		* 1000**(result_exponent*power)
