import pandas as pd
import regex as re
import jaro
import time
from constants import SearchConstants


class AbbrQueryMatcher:

    """
    This function takes in an abbreviation (query) and returns a list of matches that match the abbreviation.
    It first goes through the school names to find the ones that match the school-name part of the string.
    This returns the selected school names and their addresses.
    Then it goes through the school addresses in the selected school to find the ones that match the
    address part of the string.
    """
    def __init__(self):
        self.common_words_set = {'sec', 'st', 'sr', 'the', 'of', 'new', 'no'}

    def abbreviation_search(self,
                            query: str,
                            df: pd.DataFrame) -> list:

        # start_time = time.time()

        selected = []
        query_words_list = query.strip().lower().split(" ")
        full_words = []

        # If the length of the query is bigger than 1, it means that there are more than 1 words in the query.
        # We assume that the first word is the institute name and the rest is the location.
        if len(query_words_list) > 1:

            """
            For each word in list, if that word is in common_words_set or bigger than 4 chars,
            add it to a different list
            """
            query_list_copy = query_words_list.copy()
            for word in query_words_list:
                if word in self.common_words_set or len(word) > SearchConstants.abbr_char_limit:
                    query_list_copy.remove(word)
                    full_words.append(word)

            """
            If the query_list_copy is still bigger than length 1,
            it means there are more than 1 word that are not in common_words_set or smaller than 4 chars.
            So we assume that the first word is the institute name and assign it to query_list_copy
            and the rest is the place.
            Also, we have not appended the full_words list to the place variable in "if" block.
            This is because we use it to form the address regex pattern later in the code anyway.
            """
            if len(query_list_copy) > 1:
                place = " ".join(query_list_copy[1:])
                query_list_copy = query_list_copy[0]
            else:
                place = " ".join(full_words)
            
            # Find the list of letters in the query_list_copy
            list_of_letters = [letter for word in query_list_copy for letter in word]

            # Flatten the list of letters
            list_of_letters = [letter for sublist in list_of_letters for letter in sublist]
            pattern = r"^(\b" + r"[a-z]*\b\s+".join(list_of_letters) + r"[a-z]*\b)"

            simplified_query = "".join(list_of_letters) + " " + " ".join(full_words)
        else:
            # If the length of query is 1, it means that there is only one word in the query.
            # most likely it is the institute name.
            place = ""
            simplified_query = query_words_list[0] # Since there is only one word
            pattern = r"^(\b" + r'[a-z]*\b.*?\b'.join(simplified_query) + r'[a-z]*\b)'

        # If place is equal to full_words, it means that place variable is not required,
        # so we can just use the full_words variable
        if place == " ".join(full_words):
            place = ""

        """
        First we loop through the school names to find the ones that match the name regex,
        then we loop through the selected schools addresses to find the ones that match the address regex.
        Below, we loop over the school names in the dataset to check if the name matches the regex
        """
        if "address" in df.columns:
            for school in zip(df["name"], df["address"], df["name_in_abbr"], df["address_in_abbr"]):
                if re.search(pattern, school[0].strip().lower()):

                    # get the respective abbreviation from the dataframe:
                    full_name_abbr = school[2]

                    """
                    We compare the abbreviation with the query using jaro-winkler metric
                    and then append the school name, address and score to the selected_school list
                    """
                    score = jaro.jaro_winkler_metric(simplified_query, full_name_abbr.strip().lower()) * 100
                    selected.append((
                        school[0].title(),
                        school[1].title(),
                        school[3],
                        round(score, 4)))
                    selected.sort(key=lambda x: x[2], reverse=True)
        else:
            for school in zip(df["name"], df["name_in_abbr"]):
                if re.search(pattern, school[0].strip().lower()):
                    full_name_abbr = school[1]
                    score = jaro.jaro_winkler_metric(simplified_query, full_name_abbr.strip().lower()) * 100
                    selected.append((school[0].title(), round(score, 4)))
                    selected.sort(key=lambda x: x[1], reverse=True)
            
            # Since we are not using the address, we can return the top 10 results from here only
            return selected[:10]

        """
        School names have been selected, now we need to select the top addresses.
        Make a regex for the address.
        """
        if place and full_words:
            pattern = r"(\b" + r"[a-z]*\s+".join(place) + r"[a-z]*\s+\b" + r"[a-z]*\s+".join(full_words) + r"[a-z]*\b){e<=2}"
        elif place:
            pattern = r"(\b" + r"[a-z]*\s+".join(place) + r"[a-z]*\b){e<=2}"
        elif full_words:
            pattern = r"(\b" + r"[a-z]*\s+".join(full_words) + r"[a-z]*\b){e<=2}"

        final_list = []

        # Loop over the schools in the selected_schools list to check if the address matches the regex
        for school in selected:
            name = school[0]
            address = school[1].strip().lower()
            address_abbr = school[2].strip().lower()
            name_score = school[3]

            # Check if the address matches the regex
            if re.search(pattern, address, re.IGNORECASE):
                input_address = "".join(place) or " ".join(full_words)

                """
                Compare both the abbreviation and the full address with the query using jaro-winkler metric.
                We keep the greater score out of both.
                """
                score_1 = jaro.jaro_winkler_metric(input_address, address_abbr) * 100
                score_2 = jaro.jaro_winkler_metric(input_address, address) * 100
                score_address = max(score_1, score_2)

                """
                If the query is directly in the address, we add a bias of +5 to the score.
                For example, if the query is "rkp", and the address abbr is "sxrkpnd",
                we add a bias of +5
                """
                if input_address in address.strip().lower() or input_address in address_abbr:
                    score_address += 5

                final_list.append((name, address, round(name_score, 4), round(score_address, 4)))

                # Sort the final_list by name score and then address score in descending order
                final_list.sort(key=lambda x: (x[2], x[3]), reverse=True)

        # If the final_list is empty, it means that no address matched the regex,
        # so return the top 10 school matches
        if final_list == []:
            # end_time = time.time()
            # print("\nTime taken for abbr search: ", end_time - start_time)
            # print()
            return selected[:10]

        # If the final_list is not empty, return the top 10 from the final_list
        top_ten = final_list[:10]

        # Append the mean score of name and address to the top_ten list
        top_ten = [(school[0].title(), school[1].title(), round((school[2] + school[3]) / 2, 4)) for school in top_ten]

        # end_time = time.time()
        # print("\nTime taken for abbr search: ", end_time - start_time)
        # print()
        
        return top_ten

# Usage example:
# matcher = AbbrSchoolMatcher("cbse_affiliated_schools.csv")
# results = matcher.abbreviation_search("dps rkp")
# print(results)

