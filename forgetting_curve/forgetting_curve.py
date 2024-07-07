import math
import pandas as pd
from datetime import datetime, timedelta
from database.database import get_session, Word

def forgetting_curve(time_since_review, difficulty, review_count):
    base_rate = 0.1
    time_factor = time_since_review.total_seconds() / (24 * 3600)  # days
    return 1 - math.exp(-base_rate * time_factor / (difficulty * (1 + review_count)))

def select_words(choices: int) -> pd.DataFrame:
    session = get_session()
    now = datetime.now()
    words = session.query(Word).all()
    
    for word in words:
        time_since_review = now - word.last_reviewed
        word.forgetting_score = forgetting_curve(time_since_review, word.difficulty, word.review_count)
        if word.next_review is None:
            word.next_review = now
        word.due_score = max(0, (now - word.next_review).total_seconds() / (24 * 3600))
        word.total_score = word.forgetting_score + word.due_score
    
    words = sorted(words, key=lambda x: x.total_score, reverse=True)[:choices]
    
    # Update the selected words
    for word in words:
        word.last_reviewed = now
        word.review_count += 1
        word.next_review = calculate_next_review(word)
    
    session.commit()
    
    df = pd.DataFrame([(word.id, word.word, word.meaning, word.sentence) for word in words],
                      columns=['id', 'word', 'meaning', 'sentence'])
    session.close()
    return df

def calculate_next_review(word):
    # Implement spaced repetition algorithm
    interval = (1.5 ** word.review_count) * (word.difficulty ** 0.5)
    return datetime.now() + timedelta(days=interval)

def update_word_after_review(word_id, is_correct):
    session = get_session()
    word = session.query(Word).filter(Word.id == int(word_id)).first()
    if is_correct:
        word.correct_count += 1
        word.difficulty = max(0.5, word.difficulty * 0.9)
    else:
        word.incorrect_count += 1
        word.difficulty = min(2.0, word.difficulty * 1.1)
    
    word.review_count += 1
    word.last_reviewed = datetime.now()
    word.next_review = calculate_next_review(word)
    session.commit()
    session.close()
