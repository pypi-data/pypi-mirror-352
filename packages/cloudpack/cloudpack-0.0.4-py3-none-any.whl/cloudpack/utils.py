import string


def is_password_secure(password: str) -> bool:
    """
    Checks if the given password meets the following criteria:
    - At least 12 characters long
    - Includes uppercase and lowercase letters
    - Contains numbers and symbols
    """
    if len(password) < 12:
        return False

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)

    return all([has_upper, has_lower, has_digit, has_symbol])
