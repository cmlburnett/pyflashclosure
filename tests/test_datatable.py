import json
import pytest

import pyflashclosure

@pytest.fixture
def simple():
	dt = pyflashclosure.Datatable()
	dt.AddDataRow('A', 'B', 'C')
	dt.AddDataRow('D', 'E', 'F')
	dt.AddDataRow('I', 'J', 'K')
	return {'dt': dt}

def test_build1():
	dt = pyflashclosure.Datatable()
	assert(dt is not None)
	assert(dt.NumberRows == 0)
	assert(dt.NumberColumns == 0)
	assert(dt.NumberCells == 0)
	assert(dt.NumberEffectiveCells == 0)
	assert(dt.MakeCardsRow == [])

	dt.AddDataRow('A', 'B', 'C')
	assert(dt.NumberRows == 1)
	assert(dt.NumberColumns == 3)
	assert(dt.NumberCells == 3)
	assert(dt.NumberEffectiveCells == 3)
	assert(dt.MakeCardsRow == [True, True, True])

	dt.AddDataRow('D', 'E', 'F')
	assert(dt.NumberRows == 2)
	assert(dt.NumberColumns == 3)
	assert(dt.NumberCells == 6)
	assert(dt.NumberEffectiveCells == 6)
	assert(dt.MakeCardsRow == [True, True, True])

	with pytest.raises(ValueError):
		dt.AddDataRow('G', 'H')

	with pytest.raises(ValueError):
		dt.AddDataRow()

	dt.AddDataRow('I', 'J', 'K')
	assert(dt.NumberRows == 3)
	assert(dt.NumberColumns == 3)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 9)
	assert(dt.MakeCardsRow == [True, True, True])

	assert(dt.GetRow(0) == ['A', 'B', 'C'])
	assert(dt.GetRow(1) == ['D', 'E', 'F'])
	assert(dt.GetRow(2) == ['I', 'J', 'K'])

def test_simple_datacorrect(simple):
	dt = simple['dt']

	assert(dt.GetRow(0) == ['A', 'B', 'C'])
	assert(dt.GetRow(1) == ['D', 'E', 'F'])
	assert(dt.GetRow(2) == ['I', 'J', 'K'])
	with pytest.raises(IndexError):
		dt.GetRow(-1)
	with pytest.raises(IndexError):
		dt.GetRow(3)

def test_simple_makecardscorrect(simple):
	dt = simple['dt']

	assert(dt.NumberEffectiveColumns == 3)

	dt.SetMakeCardsColumn(0, False)
	assert(dt.MakeCardsRow == [False, True, True])
	assert(dt.NumberEffectiveColumns== 2)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 6)
	dt.SetMakeCardsColumn(0, True)
	assert(dt.MakeCardsRow == [True, True, True])
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 9)

	dt.SetMakeCardsColumn(1, False)
	assert(dt.MakeCardsRow == [True, False, True])
	assert(dt.NumberEffectiveColumns== 2)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 6)
	dt.SetMakeCardsColumn(1, True)
	assert(dt.MakeCardsRow == [True, True, True])
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 9)

	dt.SetMakeCardsColumn(2, False)
	assert(dt.MakeCardsRow == [True, True, False])
	assert(dt.NumberEffectiveColumns== 2)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 6)
	dt.SetMakeCardsColumn(2, True)
	assert(dt.MakeCardsRow == [True, True, True])
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 9)

	with pytest.raises(IndexError):
		dt.SetMakeCardsColumn(3, True)

	assert(dt.NumberEffectiveColumns == 3)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 9)

	dt.SetMakeCardsColumn(0, False)
	assert(dt.NumberEffectiveColumns == 2)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 6)

	dt.SetMakeCardsColumn(1, False)
	assert(dt.NumberEffectiveColumns == 1)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 3)

	dt.SetMakeCardsColumn(2, False)
	assert(dt.NumberEffectiveColumns == 0)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 0)

def test_index_retrieval1(simple):
	dt = simple['dt']

	with pytest.raises(IndexError):
		dt.GetIndexedCell(-1)
	assert(dt.GetIndexedCell(0) == 'A')
	assert(dt.GetIndexedCell(1) == 'B')
	assert(dt.GetIndexedCell(2) == 'C')
	assert(dt.GetIndexedCell(3) == 'D')
	assert(dt.GetIndexedCell(4) == 'E')
	assert(dt.GetIndexedCell(5) == 'F')
	assert(dt.GetIndexedCell(6) == 'I')
	assert(dt.GetIndexedCell(7) == 'J')
	assert(dt.GetIndexedCell(8) == 'K')
	with pytest.raises(IndexError):
		dt.GetIndexedCell(9)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 9)



	# Skip first column but shouldn't check getting the cell
	dt.SetMakeCardsColumn(0, False)

	with pytest.raises(IndexError):
		dt.GetIndexedCell(-1)
	assert(dt.GetIndexedCell(0) == 'A')
	assert(dt.GetIndexedCell(1) == 'B')
	assert(dt.GetIndexedCell(2) == 'C')
	assert(dt.GetIndexedCell(3) == 'D')
	assert(dt.GetIndexedCell(4) == 'E')
	assert(dt.GetIndexedCell(5) == 'F')
	assert(dt.GetIndexedCell(6) == 'I')
	assert(dt.GetIndexedCell(7) == 'J')
	assert(dt.GetIndexedCell(8) == 'K')
	with pytest.raises(IndexError):
		dt.GetIndexedCell(9)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 6)



	# Skip second column but shouldn't check getting the cell
	dt.SetMakeCardsColumn(0, False)

	with pytest.raises(IndexError):
		dt.GetIndexedCell(-1)
	assert(dt.GetIndexedCell(0) == 'A')
	assert(dt.GetIndexedCell(1) == 'B')
	assert(dt.GetIndexedCell(2) == 'C')
	assert(dt.GetIndexedCell(3) == 'D')
	assert(dt.GetIndexedCell(4) == 'E')
	assert(dt.GetIndexedCell(5) == 'F')
	assert(dt.GetIndexedCell(6) == 'I')
	assert(dt.GetIndexedCell(7) == 'J')
	assert(dt.GetIndexedCell(8) == 'K')
	with pytest.raises(IndexError):
		dt.GetIndexedCell(9)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 6)



	# Skip third column but shouldn't check getting the cell
	dt.SetMakeCardsColumn(0, False)

	with pytest.raises(IndexError):
		dt.GetIndexedCell(-1)
	assert(dt.GetIndexedCell(0) == 'A')
	assert(dt.GetIndexedCell(1) == 'B')
	assert(dt.GetIndexedCell(2) == 'C')
	assert(dt.GetIndexedCell(3) == 'D')
	assert(dt.GetIndexedCell(4) == 'E')
	assert(dt.GetIndexedCell(5) == 'F')
	assert(dt.GetIndexedCell(6) == 'I')
	assert(dt.GetIndexedCell(7) == 'J')
	assert(dt.GetIndexedCell(8) == 'K')
	with pytest.raises(IndexError):
		dt.GetIndexedCell(9)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 6)

def test_index_retrieval2(simple):
	dt = simple['dt']

	with pytest.raises(IndexError):
		dt.GetIndexedCell(-1)
	assert(dt.GetEffectiveIndexedCell(0) == 'A')
	assert(dt.GetEffectiveIndexedCell(1) == 'B')
	assert(dt.GetEffectiveIndexedCell(2) == 'C')
	assert(dt.GetEffectiveIndexedCell(3) == 'D')
	assert(dt.GetEffectiveIndexedCell(4) == 'E')
	assert(dt.GetEffectiveIndexedCell(5) == 'F')
	assert(dt.GetEffectiveIndexedCell(6) == 'I')
	assert(dt.GetEffectiveIndexedCell(7) == 'J')
	assert(dt.GetEffectiveIndexedCell(8) == 'K')
	with pytest.raises(IndexError):
		dt.GetIndexedCell(9)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 9)



	# Skip first column
	dt.SetMakeCardsColumn(0, False)

	with pytest.raises(IndexError):
		dt.GetIndexedCell(-1)
	assert(dt.GetEffectiveIndexedCell(0) == 'B')
	assert(dt.GetEffectiveIndexedCell(1) == 'C')
	assert(dt.GetEffectiveIndexedCell(2) == 'E')
	assert(dt.GetEffectiveIndexedCell(3) == 'F')
	assert(dt.GetEffectiveIndexedCell(4) == 'J')
	assert(dt.GetEffectiveIndexedCell(5) == 'K')
	with pytest.raises(IndexError):
		dt.GetIndexedCell(9)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 6)



	# Skip second column
	dt.SetMakeCardsColumn(0, False)
	dt.SetMakeCardsColumn(1, False)
	dt.SetMakeCardsColumn(2, True)

	with pytest.raises(IndexError):
		dt.GetIndexedCell(-1)
	assert(dt.GetEffectiveIndexedCell(0) == 'C')
	assert(dt.GetEffectiveIndexedCell(1) == 'F')
	assert(dt.GetEffectiveIndexedCell(2) == 'K')
	with pytest.raises(IndexError):
		dt.GetIndexedCell(9)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 3)



	# Skip third column
	dt.SetMakeCardsColumn(0, False)
	dt.SetMakeCardsColumn(1, True)
	dt.SetMakeCardsColumn(2, False)

	with pytest.raises(IndexError):
		dt.GetIndexedCell(-1)
	assert(dt.GetEffectiveIndexedCell(0) == 'B')
	assert(dt.GetEffectiveIndexedCell(1) == 'E')
	assert(dt.GetEffectiveIndexedCell(2) == 'J')
	with pytest.raises(IndexError):
		dt.GetIndexedCell(9)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 3)



	# Skip all
	dt.SetMakeCardsColumn(0, False)
	dt.SetMakeCardsColumn(1, False)
	dt.SetMakeCardsColumn(2, False)

	with pytest.raises(ValueError):
		dt.GetEffectiveIndexedCell(0)
	assert(dt.NumberCells == 9)
	assert(dt.NumberEffectiveCells == 0)

def test_index_serdes(simple):
	dt = simple['dt']
	s = dt.dumps()

	assert(dt.dumpobj() == [[True,True,True],['A','B','C'],['D','E','F'],['I','J','K']])
	assert(s == json.dumps([[True,True,True],['A','B','C'],['D','E','F'],['I','J','K']]))

	dt2 = pyflashclosure.Datatable.loads(s)
	assert(dt2 == dt)

	with pytest.raises(TypeError):
		pyflashclosure.Datatable.loadobj({})

	# Empty, should succeed
	assert(pyflashclosure.Datatable.loadobj([]) is not None)

	# These are all malformed object
	with pytest.raises(TypeError):
		pyflashclosure.Datatable.loadobj([ [True,0,False], ['A','B','C'], ['D', 'E', 'F'] ])
	with pytest.raises(TypeError):
		pyflashclosure.Datatable.loadobj([ [True,True,False], ['A',0,'C'], ['D', 'E', 'F'] ])
	with pytest.raises(TypeError):
		pyflashclosure.Datatable.loadobj([ [True,True,False], ['A',[],'C'], ['D', 'E', 'F'] ])
	with pytest.raises(TypeError):
		pyflashclosure.Datatable.loadobj([ [True,True,False], ['A',{},'C'], ['D', 'E', 'F'] ])
	with pytest.raises(TypeError):
		pyflashclosure.Datatable.loadobj([ [True,True,False], ['A','B','C'], {} ])
	with pytest.raises(TypeError):
		pyflashclosure.Datatable.loadobj([ [True,True,False], ['A','B','C'], ['D', 'E', lambda _:_] ])
	with pytest.raises(ValueError):
		pyflashclosure.Datatable.loadobj([ [True,True,False], ['A','B','C'], ['D', 'E'] ])

