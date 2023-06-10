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
    abbr_char_limit = 4
    abbr_single_word_str_threshold = 5