import pytest

import pyflashclosure

def test_parse():
	txt = "test"

	plain = pyflashclosure.ClosureString(txt)
	assert(plain.Text == txt)
	assert(plain.Numbers == [])
	assert(not plain.HasClosures)


	with pytest.raises(ValueError):
		plain.Output(-1)
	with pytest.raises(ValueError):
		plain.Output(0)
	with pytest.raises(ValueError):
		plain.Output(1)

def test_single():
	txt = "Simple {{c1::flash}} card"

	plain = pyflashclosure.ClosureString(txt)
	assert(plain.Text == txt)
	assert(plain.HasClosures)
	assert(plain.Numbers == [1])

	q,a = plain.Output(0)
	assert(q == "Simple [...] card")
	assert(a == "Simple '''flash''' card")

def test_singlehint():
	txt = "Simple {{c1::flash::answer}} card"

	plain = pyflashclosure.ClosureString(txt)
	assert(plain.Text == txt)
	assert(plain.Numbers == [1])
	assert(plain.HasClosures)

	q,a = plain.Output(0)
	assert(q == "Simple [...] (''answer'') card")
	assert(a == "Simple '''flash''' card")

	with pytest.raises(ValueError):
		q,a = plain.Output(1)

def test_dual():
	txt = "Simple {{c1::flash::hint1}} card {{c3::is fun::hint2}}."

	plain = pyflashclosure.ClosureString(txt)
	assert(plain.Text == txt)
	assert(plain.HasClosures)
	assert(plain.Numbers == [1,3])

	with pytest.raises(ValueError):
		q,a = plain.Output(-1)

	q,a = plain.Output(0)
	assert(q == "Simple [...] (''hint1'') card is fun.")
	assert(a == "Simple '''flash''' card is fun.")

	q,a = plain.Output(1)
	assert(q == "Simple flash card [...] (''hint2'').")
	assert(a == "Simple flash card '''is fun'''.")

	with pytest.raises(ValueError):
		q,a = plain.Output(2)

@pytest.fixture
def simpledt():
	dt = pyflashclosure.Datatable()
	dt.AddDataRow('A','B','C')
	dt.AddDataRow('D','E','F')
	dt.AddDataRow('I','J','K')

	dttxt = dt.dumps()

	txt = "Simple {{c1::::hint1}} card {{c2::::hint2}}."
	return {
		'dt': dttxt,
		'txt': txt,
	}

def test_dt1(simpledt):
	"""Differs from test_dt2 due to {{c2}} instead of {{c3}}."""
	c = pyflashclosure.ClosureString(simpledt['txt'])
	assert(c.Text == simpledt['txt'])
	assert(c.HasClosures)
	assert(c.Numbers == [1,2])

	dt = pyflashclosure.Datatable.loads(simpledt['dt'])
	assert(dt.NumberRows == 3)
	assert(dt.MakeCardsRow == [True,True,True])

	# Row 0 of A,B,C
	q,a = c.Output(0, dt)
	assert(q == "Simple [...] (''hint1'') card B.")
	assert(a == "Simple '''A''' card B.")

	q,a = c.Output(1, dt)
	assert(q == "Simple A card [...] (''hint2'').")
	assert(a == "Simple A card '''B'''.")


	# Row 1 of D,E,F
	q,a = c.Output(2, dt)
	assert(q == "Simple [...] (''hint1'') card E.")
	assert(a == "Simple '''D''' card E.")

	q,a = c.Output(3, dt)
	assert(q == "Simple D card [...] (''hint2'').")
	assert(a == "Simple D card '''E'''.")


	# Row 2 of I,J,K
	q,a = c.Output(4, dt)
	assert(q == "Simple [...] (''hint1'') card J.")
	assert(a == "Simple '''I''' card J.")

	q,a = c.Output(5, dt)
	assert(q == "Simple I card [...] (''hint2'').")
	assert(a == "Simple I card '''J'''.")

def test_dt2(simpledt):
	"""Differs from test_dt1 due to {{c3}} instead of {{c2}}."""

	simpledt['txt'] = simpledt['txt'].replace('{{c2', '{{c3')

	c = pyflashclosure.ClosureString(simpledt['txt'])
	assert(c.Text == simpledt['txt'])
	assert(c.HasClosures)
	assert(c.Numbers == [1,3])

	dt = pyflashclosure.Datatable.loads(simpledt['dt'])
	assert(dt.NumberRows == 3)
	assert(dt.MakeCardsRow == [True,True,True])

	# Row 0 of A,B,C
	q,a = c.Output(0, dt)
	assert(q == "Simple [...] (''hint1'') card C.")
	assert(a == "Simple '''A''' card C.")

	q,a = c.Output(1, dt)
	assert(q == "Simple A card [...] (''hint2'').")
	assert(a == "Simple A card '''C'''.")


	# Row 1 of D,E,F
	q,a = c.Output(2, dt)
	assert(q == "Simple [...] (''hint1'') card F.")
	assert(a == "Simple '''D''' card F.")

	q,a = c.Output(3, dt)
	assert(q == "Simple D card [...] (''hint2'').")
	assert(a == "Simple D card '''F'''.")


	# Row 2 of I,J,K
	q,a = c.Output(4, dt)
	assert(q == "Simple [...] (''hint1'') card K.")
	assert(a == "Simple '''I''' card K.")

	q,a = c.Output(5, dt)
	assert(q == "Simple I card [...] (''hint2'').")
	assert(a == "Simple I card '''K'''.")

def test_dt3(simpledt):
	"""Differs from test_dt1 due to {{c2}} and  {{c3}}."""

	simpledt['txt'] = simpledt['txt'].replace('{{c2', '{{c3')
	simpledt['txt'] = simpledt['txt'].replace('{{c1', '{{c2')

	c = pyflashclosure.ClosureString(simpledt['txt'])
	assert(c.Text == simpledt['txt'])
	assert(c.HasClosures)
	assert(c.Numbers == [2,3])

	dt = pyflashclosure.Datatable.loads(simpledt['dt'])
	assert(dt.NumberRows == 3)
	assert(dt.MakeCardsRow == [True,True,True])

	# Row 0 of A,B,C
	q,a = c.Output(0, dt)
	assert(q == "Simple [...] (''hint1'') card C.")
	assert(a == "Simple '''B''' card C.")

	q,a = c.Output(1, dt)
	assert(q == "Simple B card [...] (''hint2'').")
	assert(a == "Simple B card '''C'''.")


	# Row 1 of D,E,F
	q,a = c.Output(2, dt)
	assert(q == "Simple [...] (''hint1'') card F.")
	assert(a == "Simple '''E''' card F.")

	q,a = c.Output(3, dt)
	assert(q == "Simple E card [...] (''hint2'').")
	assert(a == "Simple E card '''F'''.")


	# Row 2 of I,J,K
	q,a = c.Output(4, dt)
	assert(q == "Simple [...] (''hint1'') card K.")
	assert(a == "Simple '''J''' card K.")

	q,a = c.Output(5, dt)
	assert(q == "Simple J card [...] (''hint2'').")
	assert(a == "Simple J card '''K'''.")

