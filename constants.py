class ProfileConstants:
    education_level_choices = (
        ('ssc', 'Secondary'),
        ('hsc', 'Higher Secondary'),
        ('ug', 'Undergraduate'),
        ('pg', 'Postgraduate'),
        ('phd', 'PhD'),
    )

    college_education_choices = (
        ('bachelor', 'Bachelors'),
        ('master', 'Masters'),
        ('phd', 'PhD')
    )


class SearchConstants:

    """
    Constant value that acts as a threshold for which a string is considered
    an abbreviation. For example, if the value is 4, then a string with 4
    characters or less is considered an abbreviation.
    """
    abbr_char_limit = 4

    """
    Constant value that acts as a threshold for when a query contains only
    1 word. If the word length is less than or equal to this value, then it is
    considered an abbreviation.
    """
    abbr_single_word_str_threshold = 5