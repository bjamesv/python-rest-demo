"""
Module providing API authentication helper functions
"""

from passlib.hash import argon2

def check_password(user_password, pw_hash):
    """
    Returns True if password matches secure hash, False if not

    Keyword Parameters:
      user_password  -- (String) plain-text password supplied by user
      pw_hash  -- (String) secure hash, retrieved from User datastore

    >>> argon2_example = '$argon2i$v=19$m=102400,t=2,p=8$712rlRJiTInxvhdCaG1trQ$QJmh4Q6Q82t+3sgUexBfrQ'
    >>> check_password('greatsecret', argon2_example)
    True
    >>> check_password('otherpassw', argon2_example)
    False
    """
    # check if hash matches the provided password
    return argon2.verify(user_password, pw_hash)
