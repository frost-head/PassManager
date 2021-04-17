import random
import string


def get_pass(length):
    letters_and_digits = string.ascii_letters + string.digits
    result = ''.join((random.choice(letters_and_digits)
                      for i in range(length)))
    return result
