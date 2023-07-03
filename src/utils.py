import string
import random

def get_random_string(length):
    # Define the pool of characters to choose from
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))