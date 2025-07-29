# textstats.py

import re

def word_count(text: str) -> int:
    """Return the number of words in the text."""
    words = re.findall(r'\b\w+\b', text)
    return len(words)

def sentence_count(text: str) -> int:
    """Return the number of sentences in the text."""
    sentences = re.split(r'[.!?]+', text)
    # Filter empty strings
    return len([s for s in sentences if s.strip()])

def average_word_length(text: str) -> float:
    """Return average length of words in the text."""
    words = re.findall(r'\b\w+\b', text)
    if not words:
        return 0
    return sum(len(word) for word in words) / len(words)

def reading_time(text: str, wpm: int = 200) -> float:
    """Estimate reading time in minutes based on words per minute."""
    total_words = word_count(text)
    return total_words / wpm
