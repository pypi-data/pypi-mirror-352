import random
import os

def load_quotes():
    base_dir = os.path.dirname(__file__)
    quotes_file = os.path.join(base_dir, "quotes.txt")

    with open(quotes_file, "r", encoding="utf-8") as f:
        quotes = [line.strip() for line in f if line.strip()]
    return quotes

def get_inspiration():
    quotes = load_quotes()
    quote = random.choice(quotes)
    print(f'{quote}')
    return 0