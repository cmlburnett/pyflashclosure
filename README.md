Library that handles flash card "closures". In the Anki world these are "cloze" that I just renamed to be different.

A string includes any number of {{c1::answer::hint}} bits of text where 1 can be any positive integer, though small increasing numbers makes the most sense.
A table of data can be supplied to provided many many virtual cards from a single flash card.

The key class is the FlashClosure that takes the question stem and a serialized datatable string.

Simple install via pip to use pyflashclosure.FlashClosre() class.
