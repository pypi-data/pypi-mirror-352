# Import packages
import re
from .data import config
from string import ascii_letters

# Main class
class ProfanityFilter:
	def __init__(self, censor_symbol = "*"):
		# Define variables
		self.__censor_symbol = censor_symbol
		self.__words = config.words
		self.__regexes = []

		self.__make_regexes()
	
	# Create regexes from words
	def __make_regexes(self):
		self.__regexes.clear()

		for i in self.__words:
			reg = ""

			for j in range(len(i)):
				reg += rf"(?:{i[j]}\s*)+" if j != len(i)-1 else i[j] + r"+"

			self.__regexes.append("(?:" + reg + ")+")

		def sortby(e):
			return len(e)

		# Sort by biggest length
		# This is used to prevent detecting of already detected words
		self.__regexes.sort(key=sortby, reverse=True)
		self.__words.sort(key=sortby, reverse=True)

	# Replace characters in a string
	def __replace_letter_symbols(self, txt: str):
		for symbol in config.to_replace_with:
			txt = txt.replace(symbol[0], symbol[1])

		return txt

	# Full profanity detector
	def __detector(self, txt):
		# Filtered text (replaced symbols)
		filter_txt = self.__replace_letter_symbols(txt)

		# Remove unreplaced symbols
		index = -1
		for letter in filter_txt:
			index += 1
			
			if letter not in ascii_letters + " 0123456789":
				filter_txt = filter_txt[:index] + " " + filter_txt[index+1:]

		# Index for every symbol
		symbol_indexes = [x for x in range(len(txt)) if txt[x] not in ascii_letters + " 0123456789"]

		# Found profanity [match_in_string, start_index, end_index, found_word]
		all_matches = []

		# This list will be returned
		final_all_matches = []

		# Indexes which are parts of profanity
		matches_indexes = []

		# Look for each profanity
		for regex in self.__regexes:
			matches = re.finditer(regex, filter_txt)
			
			for _match in matches:
				obj = [txt[_match.start():_match.end()], _match.start(), _match.end() - 1, self.__words[self.__regexes.index(regex)]]

				# If this match's indexes weren't already found, mark as found match
				if obj[1] not in matches_indexes or obj[2] not in matches_indexes:
					matches_indexes += [x for x in range(obj[1], obj[2]+1) if x not in matches_indexes]
					all_matches.append(obj)

		def sortby(e):
			return e[1]

		# Sort by start index for better manipulation
		all_matches.sort(key=sortby)

		# For each found match
		for _match in all_matches:
			# Validate this match
			if (_match[1] == 0 or filter_txt[_match[1]-1] == " " or _match[1]-1 in matches_indexes or _match[1]-1 in symbol_indexes) and (_match[2] == len(txt)-1 or filter_txt[_match[2]+1] == " " or _match[2]+1 in matches_indexes or _match[2]+1 in symbol_indexes):
				final_all_matches.append(_match)

			else:
				# If invalid, remove it completely
				for i in range(obj[1], obj[2]+1):
					try:
						matches_indexes.remove(i)
					except:
						pass
		
		# Return final sorted list
		return final_all_matches

	# Add custom words
	def add_custom_words(self, words: list) -> None:
		self.__words += [x.replace(" ", "") for x in words]
		self.__make_regexes()

	# Set censor symbol (used in censor_text())
	def set_censor_symbol(self, censor_symbol: str) -> None:
		self.__censor_symbol = censor_symbol

	"""

		This function checks for profanity in a string.
		Returns True, if profanity was found, otherwise it returns False.

	"""

	def is_profanity(self, txt: str) -> bool:
		return self.__detector(txt) != []

	"""

		This function censors profanity in a string.
		Returns the censored string.

	"""

	def censor_text(self, txt: str, censor_symbol: str = None) -> str:
		censor_symbol = censor_symbol if censor_symbol else self.__censor_symbol
		matches = self.__detector(txt)

		for _match in matches:
			txt = txt[:_match[1]] + censor_symbol * (_match[2]-_match[1]+1) + txt[_match[2]+1:]

		return txt
	
	"""

		This function makes full profanity detection in a string.
		Returns the censored string.

	"""

	def full_detection(self, txt) -> list:
		return self.__detector(txt)
