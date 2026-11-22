"""
Library that hands flash card "closures". In the Anki world these are "cloze" that I just renamed to be different.

A string includes any number of {{c1::answer::hint}} bits of text where 1 can be any positive integer, though small increasing numbers makes the most sense.
A table of data can be supplied to provided many many virtual cards from a single flash card.

The key class is the FlashClosure that takes the question stem and a serialized datatable string.
"""

import json
import re

class Datatable:
	"""
	To aide in creating FlashCard closures with many virtual cards from a single card, a Datatable can be used to consolidate that data.
	"""

	def __init__(self):
		self._makecardsrow = []
		self._data = []

	def __eq__(self, other):
		"""Compare two data tables for equality with same columns and number of rows, and content of all is equal."""

		if other is None: return False
		if self.NumberColumns != other.NumberColumns: return False
		if self.NumberRows != other.NumberRows: return False

		if self._makecardsrow != other._makecardsrow: return False
		if self._data != other._data: return False

		return True

	# ================================================================================
	# Serialization

	@classmethod
	def loads(kls, txt):
		"""Creates Datatable object from the json dumps() output."""
		return kls.loadobj( json.loads(txt) )
	@classmethod
	def loadobj(kls, o):
		"""Creates python native object from the dumpobj() output."""
		if type(o) != list:
			raise TypeError("Cannot load from anything but a list, got %s" % str(type(o)))

		# Empty table
		if len(o) == 0:
			return kls()

		for i,row in enumerate(o):
			if type(row) != list:
				raise TypeError("Row %d is not a list, got %s" % (i, type(row)))

		for i,x in enumerate(o[0]):
			if type(x) != bool:
				raise TypeError("MakeCardsRow index %d is not bool, got %s" % (i,type(x)))
		for i,row in enumerate(o[1:]):
			for j,col in enumerate(row):
				if type(col) != str:
					raise TypeError("Data[%d][%d] is not str, got %s" % (i,j,type(col)))

			if len(o[0]) != len(row):
				raise ValueError("Columns mismtach with first row %d columns and row %d with %d columns" % (len(o[0]), i, len(row)))

		ret = kls()
		ret._makecardsrow = o[0]
		ret._data = o[1:]
		return ret

	def dumps(self):
		"""Dumps this Datatable to a json string."""
		return json.dumps(self.dumpobj())
	def dumpobj(self):
		"""Dumps this Datatable to a native python object fed to json.dumps."""
		ret = []
		ret.append(self._makecardsrow)
		ret += self._data
		return ret

	# ================================================================================
	# MakeCards row

	@property
	def MakeCardsRow(self):
		"""Get the row of bool flags indicating if row should be included in making cards, or ignored if False."""
		return self._makecardsrow

	def SetMakeCardsColumn(self, idx, val):
		"""
		Set the flag indicating if the column @idx (zero-based) should be ignored when making cards.
		Default is True.
		"""
		if idx < 0:
			raise IndexError("Column index (%d) must be non-negative" % idx)
		if idx >= self.NumberColumns:
			raise IndexError("Column index %d (zero-based) exceeds number of columns %d" % (idx, self.NumberColumns))
		if type(val) != bool:
			raise TypeError("Column index %d (zero-based) cannot be anything but bool, got %s" % (idx, str(type(val))))

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

	@property
	def NumberEffectiveColumns(self):
		"""Accounting for MakeCardsRow, returns number of columns actually used to generate cards."""
		return sum([int(_) for _ in self.MakeCardsRow])

	@property
	def NumberCells(self):
		"""
		Returns the total number of cells present and ignores the hidden columns.
		This has no idea what the ClosureString has in it as not all closures may be used.
		So very possible this is larger than the number of possible closure combination.s
		"""
		return self.NumberColumns * self.NumberRows

	@property
	def NumberEffectiveCells(self):
		"""
		Returns the total number of cells present with ignoring the hidden columns.
		This has no idea what the ClosureString has in it as not all closures may be used.
		So very possible this is larger than the number of possible closure combination.s
		"""
		numhidden = sum([int(not _) for _ in self.MakeCardsRow])
		return self.NumberEffectiveColumns * self.NumberRows

	def AddDataRow(self, *items):
		"""
		Adds a row of data. The numbers of columns must match.
		"""
		if self.NumberRows != 0 and self.NumberColumns != len(items):
			raise ValueError('Has %d columns and trying to add %d columns, they must match' % (self.NumberColumns, len(items)))

		for item in items:
			if type(item) != str:
				raise TypeError("Cannot add non-str items")

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

	def GetEffectiveClosureNum(self, idx):
		"""
		Gets the closure number (eg, 3 in {{c3}}) for whatever effective column @idx points at.
		"""
		if self.NumberColumns == 0:
			raise IndexError("No columns, cannot get by index")
		if idx < 0:
			raise IndexError("Index %d cannot be negative" % idx)

		# Number of columns that are hidden (ie, number of Falses in MakeCardsRow
		numceff = self.NumberEffectiveColumns
		numc = self.NumberColumns

		newidx = idx % numceff
		# XXX; right now datatable is limited to a fixed c1, c2, c3, c4, c5 in that order
		# so the column index (zero-based) is the closure number (one-based) conversion
		return [idx for idx,val in enumerate(self.MakeCardsRow) if val == True][newidx] + 1

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
			raise ValueError("Cell index %d exceeds available data" % idx)

		# Use the column map to get the right column
		return self._data[row][ colmap[col] ]

class ClosureString:
	"""
	Class that parses and formats closures. The Output function accepts a datatable to supply data if desired.

	Supported closures are:
		{{c1}}
		{{c1::answer}}
		{{c1::answer::hint}}
		{{c1::::hint}}
	"""

	# This matches {{c1::answer}} and {{c1::answer::hint}}
	REGEX = re.compile('\{\{[cC](\d+)::((?:(?!::|\}\}).)+)(?:::((?:(?!\}\}).)+))?\}\}')
	# This matches {{c1::::hint}}
	REGEX_NOANSWER = re.compile('\{\{[cC](\d+)::(?:::((?:(?!\}\}).)+))?\}\}')
	# This matches {{c1}}
	REGEX_HOLDER = re.compile('\{\{[cC](\d+)\}\}')

	def __init__(self, txt):
		self._text = txt
		self._parts = self.Parse(txt)

		# Now go through and find all the closure numbers used
		self._numbers = []
		for part in self._parts:
			if type(part) is str: continue
			# Get all the available closure numbers
			if part[0] not in self._numbers:
				self._numbers.append(part[0])

		# Sort this so that [0] is the lowest closure number
		self._numbers.sort()

		self.QuestionHintFormat = "[%s] (''%s'')"
		self.QuestionNoHintFormat = "[%s]"
		self.AnswerFormat = "'''%s'''"

	@classmethod
	def Parse(kls, txt):
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

	@property
	def Text(self):
		"""Gets the original unparsed text."""
		return self._text

	@property
	def Numbers(self):
		"""Closure numbers found in this text."""
		return self._numbers

	@property
	def HasClosures(self):
		"""If the text has no closures then this returns False, otherwise if it does then True."""
		return len(self._numbers) != 0

	@property
	def QuestionHintFormat(self):
		"""
		Format of the question with a hint. Default is to use a pybasicwiki formatting which is simple and compatible with MediaWiki formatting.
		"""
		return self._question_hint_format
	@QuestionHintFormat.setter
	def QuestionHintFormat(self, v):
		self._question_hint_format = v

	@property
	def QuestionNoHintFormat(self):
		"""
		Format of the question without a hint. Default is to use a pybasicwiki formatting which is simple and compatible with MediaWiki formatting.
		"""
		return self._question_nohint_format
	@QuestionNoHintFormat.setter
	def QuestionNoHintFormat(self, v):
		self._question_nohint_format = v

	@property
	def AnswerFormat(self):
		"""
		Format of the answer. Default is to use a pybasicwiki formatting which is simple and compatible with MediaWiki formatting.
		"""
		return self._answer_format
	@AnswerFormat.setter
	def AnswerFormat(self, v):
		self._answer_format = v

	def Output(self, num, dt=None):
		"""
		Returns a tuple of (question, answer) text for the card number @num and optional Datatable @dt.
		"""
		if dt is None or dt.NumberCells == 0:
			return self._output_nodatatable(num)
		else:
			return self._output_datatable(num, dt)

	def _output_nodatatable(self, num):
		"""Internal function to output without a Datatable."""
		question = []
		answer = []

		if num < 0:
			raise ValueError("Card %d cannot be negative" % num)
		if num >= len(self._numbers):
			raise ValueError("Card %d exceeds closures available %d" % (num, len(self._numbers)))

		if not self.HasClosures: return self.Text

		for part in self._parts:
			if type(part) == str:
				question.append(part)
				answer.append(part)
				continue

			if part[0] == self._numbers[num]:
				if len(part) == 2:
					question.append(self.QuestionNoHintFormat % "...")
					answer.append(self.AnswerFormat % part[1])
				else:
					question.append(self.QuestionHintFormat % ("...", part[2]))
					answer.append(self.AnswerFormat % part[1])
			else:
				question.append(part[1])
				answer.append(part[1])

		return ("".join(question), "".join(answer))

	def _output_datatable(self, num, dt):
		"""Internal function to output with a Datatable."""
		question = []
		answer = []

		if num < 0:
			raise ValueError("Card %d cannot be negative" % num)

		if not self.HasClosures: return self.Text

		# Need to ignore columns without closures
		# Scenario is that the datatable contains 5 colums for c1, c2, c3, c4, c5
		# but only c1 and c3 are used, thus c2, c4, c5 should be hidden so they aren't rendered
		for i in range(0,dt.NumberColumns):
			if i+1 not in self.Numbers:
				dt.SetMakeCardsColumn(i, False)

		# This doesn't change (this is the quizzed closure number and the answer
		cellclosure = dt.GetEffectiveClosureNum(num)
		cell = dt.GetEffectiveIndexedCell(num)

		# Iterate over either str or tuples of (closure num, answer) or (closure num, answer, hint) or (closure num, None, hint)
		for part in self._parts:
			if type(part) == str:
				question.append(part)
				answer.append(part)
				continue

			# Reached a closure, if the closure number machtes cell is @cellclosure then it's the question/answer pari
			# otherwise it's whatever the answer is
			if part[0] == cellclosure:
				if len(part) == 3:
					question.append(self.QuestionHintFormat % ("...", part[2]))
					answer.append(self.AnswerFormat % cell)
				else:
					question.append(self.QuestionNoHintFormat % "...")
					answer.append(self.AnswerFormat % cell)
			else:
				# Closure numbers part[0] and cellclosure need to be related in the Numbers index
				# to determine the effective offset from @num
				a = self.Numbers.index(part[0])
				b = self.Numbers.index(cellclosure)

				# For example, if part[0] is 3 and cellclosure is 1 (so {{c3}} and {{c1}})
				# and Numbers is [1,3] and so EffectiveIndex needs to be one higher from num
				# so num + 1-0 is num+1
				ans = dt.GetEffectiveIndexedCell(num + a-b)
				question.append(ans)
				answer.append(ans)

		return ("".join(question), "".join(answer))

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

	def __init__(self, txt, datatable):
		# The wiki text to process
		self._text = ClosureString(txt)

		# Check if a datatable was provided
		if type(datatable) == str:
			self._datatable = Datatable.loads(datatable)
		elif isinstance(datatable, Datatable):
			self._datatable = datatable
		elif datatable is None:
			# Blank
			self._datatable = Datatable()
		else:
			raise TypeError("Unknown datatable type: %s" % str(type(datatable)))

	@property
	def Closure(self):
		"""
		The ClosureString object.
		"""
		return self._text

	@property
	def Text(self):
		"""
		The supplied text to parse for closures.
		Check HasClosures property to determine if this text has any closures in it.
		"""
		return self._text.Text

	@property
	def Datatable(self):
		"""
		Datatable if used.
		"""
		return self._datatable

	@property
	def HasClosures(self):
		"""If the text has no closures then this returns False, otherwise if it does then True."""
		return self._text.HasClosures

	@property
	def NumberOfCards(self):
		"""
		Get the number of cards based on the available number of closures present and scale it by the number of rows in the datatable if one is present.
		"""

		if self.HasClosures:
			if self._datatable.NumberRows:
				# Effective cells not total cells
				return self._datatable.NumberRows * len(self.Closure.Numbers)
			else:
				return len(self.Closure.Numbers)
		else:
			return len(self._text.Numbers)

	def Output(self, num):
		"""
		Gets card output to display as a two tuple of (question, answer) text.
		Provided is the card number @num from zero to self.NumberOfCards
		"""
		question = []
		answer = []

		if not self.HasClosures:
			return None

		return self._text.Output(num, self._datatable)

		# Now with (closurenum,rownum) find the answer
		for part in self.parts:
			if type(part) is str:
				question.append(part)
				answer.append(part)
				continue

			kk
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

