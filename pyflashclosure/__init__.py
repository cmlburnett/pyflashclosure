import json
import re

class Datatable:
	"""
	To aide in creating FlashCard closures with many virtual cards from a single card, a Datatable can be used to consolidate that data.
	"""

	def __init__(self):
		self._makecardsrow = []
		self._data = []

	# ================================================================================
	# Serialization

	@classmethod
	def loads(kls, txt):
		return kls.loadobj( json.loads(txt) )
	@classmethod
	def loadobj(kls, o):
		pass

	def dumps(kls):
		return json.dumps(self.dumpobj)
	def dumpobj(kls):
		ret = []
		ret += self._makecardsrow
		ret += self._data
		return ret

	# ================================================================================
	# MakeCards row

	@property
	def MakeCardsRow(self):
		return self._makecardsrow

	def SetMakeCardsColumn(self, idx, val):
		if idx < 0:
			raise IndexError("Column index (%d) must be non-negative" % idx)
		if idx >= self.NumberColumns:
			raise IndexError("Column index %d (zero-based) exceeds number of columns %d" % (idx, self.NumberColumns))

		self._makecardsrow[idx] = val

	# ================================================================================
	# Basic data properties

	@property
	def NumberRows(self):
		"""Returns the number of rows in the datatable."""
		return len(self._data)

	@property
	def NumberColumns(self):
		"""Returns the number of columns in the datatable. If no rows then zero."""

		if len(self._data) == 0:
			return 0
		else:
			return len(self._data[0])

	def AddDataRow(self, *items):
		"""
		Adds a row of data. The numbers of columns must match.
		"""
		if self.NumberRows != 0 and self.NumberColumns != len(items):
			raise ValueError('Has %d columns and trying to add %d columns, they must match' % (self.NumberColumns, len(items)))

		self._data += [list(items)]

		if self.NumberRows == 1:
			self._makecardsrow = [True] * self.NumberColumns

	def GetRow(self, idx):
		"""Gets a rows of data. @idx is zero based"""

		if idx < 0:
			raise IndexError("Row %d cannot be negative" % idx)
		if idx >= self.NumberRows:
			raise IndexError("Row %d (zero-based) exceeds number of rows %d" % (idx, self.NumberRows))

		# Copy data
		return list(self._data[idx])

	# ================================================================================
	# Processing functions

	@property
	def GetEffectiveColumns(self):
		return sum([int(_) for _ in self._makecardsrow])

	def GetIndexedCell(self, idx):
		"""
		Get datarow cell content by raster index (so scans columns for each row).
		For example GetIndexedCell(0) is [0][0] and GetIndexedCell(1) is [0][1].
		This ignores the MakeCardsRow information; see GetEffectiveIndexedCell for ignoring those columns.
		"""
		if self.NumberColumns == 0:
			raise IndexError("No columns, cannot get by index")
		if idx < 0:
			raise IndexError("Index %d cannot be negative" % idx)

		numc = self.NumberColumns
		numr = self.NumberRows

		col = idx % numc
		row = int(idx / numc)

		if row >= numr:
			raise IndexError("Cell index %d exceeds available data" % idx)

		return self._data[row][col]

	def GetEffectiveIndexedCell(self, idx):
		"""
		Get datarow cell content by raster index (so scans columns for each row) while ignoring MakeCardsRow columns
		For example GetIndexedCell(0) is [0][0] and GetIndexedCell(1) is [0][2] assuming the second column is ignored.
		"""
		if self.NumberColumns == 0:
			raise IndexError("No columns, cannot get by index")
		if idx < 0:
			raise IndexError("Index %d cannot be negative" % idx)

		# Number of columns that are hidden (ie, number of Falses in MakeCardsRow
		numhidden = sum([int(not _) for _ in self.MakeCardsRow])

		# Do these once
		numc = self.NumberColumns
		numceff = numc - numhidden
		numr = self.NumberRows

		# Ensure there's something to get
		if numceff == 0:
			raise ValueError("All columns are hidden, cannot get data")

		# Skip over columns where MakeCardsRow[...] is False
		# so use a map from effective column to actual column in _data
		colmap = {}
		z = 0
		for i in range(numc):
			if self.MakeCardsRow[i]:
				colmap[z] = i
				z += 1
			else:
				# don't map this column so z is unchanged
				pass

		# column and row in the effective table when columns are ignored
		col = idx % numceff
		row = int(idx / numceff)

		if row >= numr:
			raise IndexError("Cell index %d exceeds available data" % idx)

		# Use the column map to get the right column
		return self._data[row][ colmap[col] ]

class FlashClosure:
	"""
	For a flash card, a closure is a sort of "fill in the blank" style of cards.
	This is indicated in the card text with {{c1::answer::hint}} where 1 is any integer.
	The question slide will show "[...] (hint)" if it's the active closure otherwise it will just show "ansewr" for other closures.
	Thus, if a card has c1, c2, and c3 then it will create three cards where c1 is being studied while c2 and c3 are shown as answers.

	Additionally, a datatable can be provided that allows permutting the cards through each row of the table.
	For example, if a card has {{c1}} and {{c2}} and 4 rows in the table then this one card will produce 8 studyable cards.

	The output is in wiki and so must be ran through the wiki.wikitohtml() function to convert that wiki to HTML.
	"""

	# This matches {{c1::answer}} and {{c1::answer::hint}}
	REGEX = re.compile('\{\{[cC](\d+)::((?:(?!::|\}\}).)+)(?:::((?:(?!\}\}).)+))?\}\}')
	# This matches {{c1::::hint}}
	REGEX_NOANSWER = re.compile('\{\{[cC](\d+)::(?:::((?:(?!\}\}).)+))?\}\}')
	# This matches {{c1}}
	REGEX_HOLDER = re.compile('\{\{[cC](\d+)\}\}')

	def __init__(self, txt, datatable):
		# The wiki text to process
		self._text = txt

		# Process the text for all the closure statements
		self.parts = self.Process(txt)

		# Check if a datatable was provided
		if datatable:
			self.datatable = datatable
		else:
			self.datatable = None

		# Now go through and find all the closure numbers used
		self.numbers = []
		for part in self.parts:
			if type(part) is str: continue
			# Get all the available closure numbers
			if part[0] not in self.numbers:
				self.numbers.append(part[0])

		# Sort this so that [0] is the lowest closure number
		self.numbers.sort()

	@property
	def Text(self):
		"""
		The supplied text to parse for closures.
		Check HasClsoures property to determine if this text has any closures in it.
		"""
		return self._text

	@property
	def HasClsoures(self):
		"""
		If the text has no closures then this returns False, otherwise if it does then True.
		"""
		return len(self.numbers) != 0

	@property
	def QuestionHintFormat(self):
		"""
		Format of the question with a hint. Default is to use a pybasicwiki formatting which is simple and compatible with MediaWiki formatting.
		"""
		return "[%s] (''%s'')"
	@property
	def QuestionNoHintFormat(self):
		"""
		Format of the question without a hint. Default is to use a pybasicwiki formatting which is simple and compatible with MediaWiki formatting.
		"""
		return "[%s]"
	@property
	def AnswerFormat(self):
		"""
		Format of the answer. Default is to use a pybasicwiki formatting which is simple and compatible with MediaWiki formatting.
		"""
		return "'''%s'''"

	@property
	def NumberOfCards(self):
		"""
		Get the number of cards based on the available number of closures present and scale it by the number of rows in the datatable if one is present.
		"""

		if self.datatable:
			# Data table present then the number of unique cards is the number of closure numbers * the number of data rows (exclude first row)
			# For a self.numbers of (1,2) and datatable with two columns and 3 rows
			#  num == 0: (self.numbers[0], self.datatable[1][0])
			#  num == 1: (self.numbers[0], self.datatable[1][1])
			#  num == 2: (self.numbers[1], self.datatable[2][0])
			#  num == 3: (self.numbers[1], self.datatable[2][1])
			#  num == 4: (self.numbers[2], self.datatable[3][0])
			#  num == 5: (self.numbers[2], self.datatable[3][1])

			# Exclude columns if the the "Make {{c1}} Cards" was unchecked
			columns = 0
			if 1 in self.numbers and self.datatable[0][0]: columns += 1
			if 2 in self.numbers and self.datatable[0][1]: columns += 1
			if 3 in self.numbers and self.datatable[0][2]: columns += 1
			if 4 in self.numbers and self.datatable[0][3]: columns += 1
			if 5 in self.numbers and self.datatable[0][4]: columns += 1

			return columns * (len(self.datatable)-1)
		else:
			return len(self.numbers)

	@classmethod
	def Process(kls, txt):
		"""
		Process the text @txt for closures.
		"""

		#r = re.compile('\{\{c([0-9]+)::(.+)(?::.+)?\}\}')
		#r = re.compile('\{\{c(\d+)::([^:{}]+)(?:::([^:{}]+))?\}\}')

		# Match the closure number
		# Match the answer that may contain a single colon or curly brace
		# Match the optional hint that may contain a single colon or curly brace

		ret = []

		index = 0
		while True:
			# Check all three regexes and go with the first one
			# Could optimize by using a single regex but this works and it's not that taxing and strings are usually fairly short.
			m1 = kls.REGEX.search(txt[index:])
			m2 = kls.REGEX_NOANSWER.search(txt[index:])
			m3 = kls.REGEX_HOLDER.search(txt[index:])

			if m1 is None and m2 is None and m3 is None:
				# No more matches, remainder is plain text
				ret.append( txt[index:] )
				break

			else:
				# At least one is present
				mn = min([_.start() for _ in (m1, m2, m3) if _ is not None])
				if m1 is not None and mn == m1.start():
					m = m1

					# Leading plain text
					ret.append( txt[index:index+m.start()] )

					# Format is (idx,answer) or (idx,answer,hint)
					grps = m.groups()
					if grps[2] is not None:
						ret.append( (int(grps[0]), grps[1], grps[2]) )
					else:
						ret.append( (int(grps[0]), grps[1]) )

				elif m2 is not None and mn == m2.start():
					m = m2

					# Leading plain text
					ret.append( txt[index:index+m.start()] )

					# Format is (idx,hint)
					grps = m.groups()
					ret.append( (int(grps[0]), None, grps[1]) )

				elif m3 is not None and mn == m3.start():
					m = m3
					# Leading plain text
					ret.append( txt[index:index+m.start()] )

					# Format is (idx,)
					grps = m.groups()
					ret.append( (int(grps[0]), None, None) )

				else:
					raise NotImplementedError("Shouldn't reach this point %s" % str([index, mn]))

			# Move the starting index for next search
			index += m.end()

		# Clear out empty strings
		ret = [_ for _ in ret if (type(_) is str and len(_)>0) or type(_) is not str]
		return ret

	def Output(self, num):
		"""
		Gets card output to display as a two tuple of (question, answer) text.
		Provided is the card number @num from zero to self.NumberOfCards
		"""
		question = []
		answer = []

		if not self.HasClsoures:
			return None

		closureidx = closurenum = rownum = None

		# Typically, the closures should benumbers from 1, 2, 3, ... but not necessary
		# @num is zero-based
		if self.datatable:
			# Numbering starts with first closure number then the data row then second closure number and second data row
			# For a self.numbers of (1,2) and datatable with two columns and 3 rows
			#  num == 0: (self.numbers[0], self.datatable[1][0]) closure number = (0 / 2)+1 == 1 and row number = 0 % 2 == 0
			#  num == 1: (self.numbers[0], self.datatable[1][1]) closure number = (1 / 2)+1 == 1 and row number = 1 % 2 == 1
			#  num == 2: (self.numbers[1], self.datatable[2][0]) closure number = (2 / 2)+1 == 2 and row number = 2 % 2 == 0
			#  num == 3: (self.numbers[1], self.datatable[2][1]) closure number = (3 / 2)+1 == 2 and row number = 3 % 2 == 1
			#  num == 4: (self.numbers[2], self.datatable[3][0]) closure number = (4 / 2)+1 == 3 and row number = 4 % 2 == 0
			#  num == 5: (self.numbers[2], self.datatable[3][1]) closure number = (5 / 2)+1 == 3 and row number = 5 % 2 == 1

			# Exclude columns if the the "Make {{c1}} Cards" was unchecked
			columns = 0
			if 1 in self.numbers and self.datatable[0][0]: columns += 1
			if 2 in self.numbers and self.datatable[0][1]: columns += 1
			if 3 in self.numbers and self.datatable[0][2]: columns += 1
			if 4 in self.numbers and self.datatable[0][3]: columns += 1
			if 5 in self.numbers and self.datatable[0][4]: columns += 1

			closureidx = num % columns
			closurenum = self.numbers[ closureidx ]
			rownum = int(num / columns)+1
		else:
			# No data table so it's just the closure number
			closurenum = self.numbers[num]
			rownum = None

		# Now with (closurenum,rownum) find the answer
		for part in self.parts:
			if type(part) is str:
				question.append(part)
				answer.append(part)
			else:
				# part[0] is the closure number (eg, "{{c1::x::h}}" is 1)
				if part[0] == closurenum:
						if len(part) == 2:
							question.append(self.QuestionNoHintFormat % "...")

							if rownum is not None:
								# Use the answer from the datatable
								answer.append(self.AnswerFormat % self.datatable[rownum][closureidx])
							else:
								# Use the answer from the closure definition {{c1::answer}}
								answer.append(self.AnswerFormat % part[1])
						else:
							question.append(self.QuestionHintFormat % ("...", part[2]))

							if rownum is not None:
								# Use the answer from the datatable
								answer.append(self.AnswerFormat % self.dattable[rownum][closureidx])
							else:
								# Use the answer from the closure definition {{c1::answer}}
								answer.append(self.AnswerFormat % (part[1] or ""))
				else:
					# Not the active closure, so just put the answer in
					if rownum is None:
						question.append(part[1])
						answer.append(part[1])
					else:
						otherclosureidx = self.numbers.index(part[0])
						question.append( self.datatable[rownum][otherclosureidx] )
						answer.append( self.datatable[rownum][otherclosureidx] )

		try:
			return ("".join(question), "".join(answer))
		except Exception as e:
			raise ValueError([num, question, answer, str(e), [closureidx, closurenum, rownum], self.datatable])

