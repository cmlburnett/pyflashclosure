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

@pytest.fixture
def singletable():
	return {
		'txt': "Simple {{c1::flash::answer}} card with single closure",
		'datatable': None,
	}

def test_simple(simple):
	c = pyflashclosure.FlashClosure(**simple)
	assert(c.Closure.QuestionNoHintFormat == "[%s]")
	assert(c.Closure.QuestionHintFormat == "[%s] (''%s'')")
	assert(c.Closure.AnswerFormat == "'''%s'''")

	assert(c.Text == simple['txt'])
	assert(not c.HasClosures)
	assert(c.NumberOfCards == 0)
	assert(c.Output(0) is None)

def test_single(single):
	c = pyflashclosure.FlashClosure(**single)
	assert(c.Closure.QuestionNoHintFormat == "[%s]")
	assert(c.Closure.QuestionHintFormat == "[%s] (''%s'')")
	assert(c.Closure.AnswerFormat == "'''%s'''")

	assert(c.Text == single['txt'])
	assert(c.HasClosures)
	assert(c.NumberOfCards == 1)
	assert(c.Output(0) is not None)

	out = c.Output(0)
	assert(out[0] == "Simple [...] (''answer'') card with single closure")
	assert(out[1] == "Simple '''flash''' card with single closure")

@pytest.fixture
def dual():
	return {
		'txt': "Simple {{c1::flash::answer}} card with {{c2::double::hint}} closure",
		'datatable': None,
	}

def test_dual(dual):
	c = pyflashclosure.FlashClosure(**dual)
	assert(c.Closure.QuestionNoHintFormat == "[%s]")
	assert(c.Closure.QuestionHintFormat == "[%s] (''%s'')")
	assert(c.Closure.AnswerFormat == "'''%s'''")

	assert(c.Text == dual['txt'])
	assert(c.HasClosures)
	assert(c.NumberOfCards == 2)
	assert(c.Output(0) is not None)

	out = c.Output(0)
	assert(out[0] == "Simple [...] (''answer'') card with double closure")
	assert(out[1] == "Simple '''flash''' card with double closure")

	out = c.Output(1)
	assert(out[0] == "Simple flash card with [...] (''hint'') closure")
	assert(out[1] == "Simple flash card with '''double''' closure")

@pytest.fixture
def dualtable():
	return {
		'txt': "Simple {{c1::::answer}} card with {{c2::::hint}} closure",
		'datatable': '[[true,true,true], ["A","B","C"], ["D","E","F"], ["I","J","K"]]',
	}

def test_dual(dualtable):
	c = pyflashclosure.FlashClosure(**dualtable)
	assert(c.Closure.QuestionNoHintFormat == "[%s]")
	assert(c.Closure.QuestionHintFormat == "[%s] (''%s'')")
	assert(c.Closure.AnswerFormat == "'''%s'''")
	assert(c.NumberOfCards == 6)

	assert(c.Text == dualtable['txt'])
	assert(c.HasClosures)
	assert(c.Output(0) is not None)

	out = c.Output(0)
	assert(out[0] == "Simple [...] (''answer'') card with B closure")
	assert(out[1] == "Simple '''A''' card with B closure")

	out = c.Output(1)
	assert(out[0] == "Simple A card with [...] (''hint'') closure")
	assert(out[1] == "Simple A card with '''B''' closure")


	out = c.Output(2)
	assert(out[0] == "Simple [...] (''answer'') card with E closure")
	assert(out[1] == "Simple '''D''' card with E closure")

	out = c.Output(3)
	assert(out[0] == "Simple D card with [...] (''hint'') closure")
	assert(out[1] == "Simple D card with '''E''' closure")


	out = c.Output(4)
	assert(out[0] == "Simple [...] (''answer'') card with J closure")
	assert(out[1] == "Simple '''I''' card with J closure")

	out = c.Output(5)
	assert(out[0] == "Simple I card with [...] (''hint'') closure")
	assert(out[1] == "Simple I card with '''J''' closure")

	with pytest.raises(ValueError):
		out = c.Output(-1)
	with pytest.raises(ValueError):
		out = c.Output(6)


def test_cadiojams():
	txt = "{{c1::Male}} is a red flag for syncope: {{c2::true::true or false}}"
	dttxt = '[[false, true, true, true, true], ["Age > 60", "true", "", "", ""], ["Age < 60", "false", "", "", ""], ["Male", "true", "", "", ""], ["Female", "false", "", "", ""], ["Exertional syncope", "true", "", "", ""], ["Syncope upon standing", "false", "", "", ""], ["Syncope while seated", "true", "", "", ""], ["First syncope", "true", "", "", ""], ["20 years of syncope", "false", "", "", ""]]'

	c = pyflashclosure.FlashClosure(txt, dttxt)
	assert(c.Closure.Numbers == [1,2])
	assert(c.Datatable.NumberRows == 9)
	assert(c.Datatable.NumberColumns == 5)
	assert(c.Datatable.NumberEffectiveColumns == 4)
	assert(c.NumberOfCards == 9)
	q,a = c.Output(0)
	assert(q == "Age > 60 is a red flag for syncope: [...] (''true or false'')")

