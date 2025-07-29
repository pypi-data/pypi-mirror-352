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

def character_count(text: str) -> int:
    """Return number of characters excluding spaces."""
    return len(text.replace(" ", "").replace("\n", "").replace("\t", ""))

def syllable_count(text: str) -> int:
    """Estimate number of syllables in the text."""
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    count = 0
    vowels = "aeiouy"
    
    for word in words:
        word_syllables = 0
        if len(word) == 0:
            continue
        if word[0] in vowels:
            word_syllables += 1
        for i in range(1, len(word)):
            if word[i] in vowels and word[i-1] not in vowels:
                word_syllables += 1
        # Remove silent 'e'
        if word.endswith("e"):
            word_syllables -= 1
        if word_syllables == 0:
            word_syllables = 1
        count += word_syllables
    return count

def flesch_reading_ease(text: str) -> float:
    """Calculate the Flesch Reading Ease score for the text."""
    words = word_count(text)
    sentences = sentence_count(text)
    syllables = syllable_count(text)
    
    if words == 0 or sentences == 0:
        return 0
    score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    return round(score, 2)

def flesch_kincaid_grade(text: str) -> float:
    """Calculate the Flesch-Kincaid Grade Level for the text."""
    words = word_count(text)
    sentences = sentence_count(text)
    syllables = syllable_count(text)
    
    if words == 0 or sentences == 0:
        return 0
    grade = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
    return round(grade, 2)
