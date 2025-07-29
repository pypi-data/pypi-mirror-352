# Python Text Stats

A simple Python module to analyze text and provide various statistics such as word count, sentence count, average word length, estimated reading time, character count, syllable count, and readability scores.

## Features

- Count words
- Count sentences
- Average word length
- Estimated reading time (default 200 WPM)
- Character count (excluding spaces)
- Estimate syllable count
- Calculate Flesch Reading Ease score
- Calculate Flesch-Kincaid Grade Level

## Installation

Simply download or clone the `pythontextstats.py` file into your project.

## Usage

```python
import pythontextstats as pts

text = "This is a simple example sentence. It has multiple words and sentences."

print("Words:", pts.word_count(text))
print("Sentences:", pts.sentence_count(text))
print("Average Word Length:", pts.average_word_length(text))
print("Reading Time (minutes):", pts.reading_time(text))
print("Character Count:", pts.character_count(text))
print("Syllable Count:", pts.syllable_count(text))
print("Flesch Reading Ease:", pts.flesch_reading_ease(text))
print("Flesch-Kincaid Grade Level:", pts.flesch_kincaid_grade(text))
