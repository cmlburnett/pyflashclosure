import pytest

import pyflashclosure

@pytest.fixture
def simple():
	return {
		'txt': "Simple flash card with nothing fancy",
		'datatable': None,
	}

@pytest.fixture
def single():
	return {
		'txt': "Simple {{c1::flash::answer}} card with single closure",
		'datatable': None,
	}

def test_simple(simple):
	c = pyflashclosure.FlashClosure(**simple)
	assert(c.Text == simple['txt'])
	assert(not c.HasClsoures)
	assert(c.NumberOfCards == 0)
	assert(c.Output(0) is None)

def test_single(single):
	c = pyflashclosure.FlashClosure(**single)
	assert(c.Text == single['txt'])
	assert(c.HasClsoures)
	assert(c.NumberOfCards == 1)
	assert(c.Output(0) is not None)

	out = c.Output(0)
	assert(out[0] == "Simple [...] (''answer'') card with single closure")
	assert(out[1] == "Simple '''flash''' card with single closure")

