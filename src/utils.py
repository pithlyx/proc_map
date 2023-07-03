import string
import random

def get_random_string(length):
    # Define the pool of characters to choose from
    characters = string.ascii_letters + string.digits
    # Generate a random string of the specified length
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string
