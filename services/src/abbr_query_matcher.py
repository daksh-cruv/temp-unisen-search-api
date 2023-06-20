import pandas as pd
import regex as re
import jaro
from constants import SearchConstants


class AbbrQueryMatcher:

    def __init__(self):
        self.common_words_set = {'sec', 'st', 'sr', 'the', 'of', 'new', 'no'}


    def filter_by_first_char(self, query: str, df: pd.DataFrame) -> pd.DataFrame:
        """
        This function filters the dataframe by the first character of the query.
        """
        df = df[df["name_first_letter_ascii"] == ord(query[0])]
        return df


    def abbreviation_search(self,
                            query: str,
                            df: pd.DataFrame) -> list:
        """
        This function takes an abbreviation (query) and a pandas DataFrame, and returns
        a list of matches. It filters the DataFrame based on matching school names,
        and then further narrows down the matches by matching school addresses.
        """

        df = self.filter_df_by_first_char(query, df)
        query_words_list = query.split(" ")
        selected_items = []
        full_or_common_words = []

        """
        If the length of the query is bigger than 1, it means that there are more than
        1 words in the query. We assume that the first word is the institute name and
        the rest is the location.
        """
        if len(query_words_list) > 1:

            """
            For each word in list, if that word is in common_words_set or bigger than 4 chars,
            add it to a different list
            """
            filtered_words = [word for word in query_words_list 
                               if word not in self.common_words_set 
                               and len(word) <= SearchConstants.abbr_char_limit]
            full_or_common_words = [word for word in query_words_list 
                          if word in self.common_words_set 
                          or len(word) > SearchConstants.abbr_char_limit]

            """
            If filtered_words list is still bigger than length 1, it means there are more
            than 1 word that are not in common_words_set or smaller than 4 chars. So we
            assume that the first word is the institute name and assign it to filtered_words
            and the rest is the place. Also, we have not appended the full_words list to
            the place variable in "if" block. This is because we use it to form the
            address regex pattern later in the code anyway.
            """
            if len(filtered_words) > 1:
                place = " ".join(filtered_words[1:])
                filtered_words = filtered_words[0]
            else:
                place = " ".join(full_or_common_words)

            list_of_letters = [letter for word in filtered_words for letter in word]
            pattern = r"^(\b" + r"[a-z]*\b\s+".join(list_of_letters) + r"[a-z]*\b)"
            simplified_query = "".join(list_of_letters) + " " + " ".join(full_or_common_words)
        else:

            """
            If the length of query is 1, it means that there is only one word in the query.
            most likely it is the institute name.
            """
            place = ""
            simplified_query = query_words_list[0]
            pattern = r"^(\b" + r'[a-z]*\b.*?\b'.join(simplified_query) + r'[a-z]*\b)'

        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        
        if place == " ".join(full_or_common_words):
            place = ""

        """
        First we loop through the school names to find the ones that match the name regex,
        then we loop through the selected schools' addresses to find the ones that match
        the address regex.
        """

        if "address" in df.columns:

            """
            df.to_dict("records") returns a list of dictionaries where each dictionary
            is a row in the dataframe. For example, if the dataframe has 3 rows,
            df.to_dict("records") will return a list of 3 dictionaries, with the keys
            being the column names and the values being the values in the row.
            """
            for school_row in df.to_dict("records"):
                if compiled_pattern.search(school_row["name"].strip().lower()):
                    name_abbr = school_row["name_abbr"]
                    score = jaro.jaro_winkler_metric(simplified_query, name_abbr) * 100
                    selected_items.append((
                        school_row["name"].title(),
                        school_row["address"],
                        school_row["address_abbr"],
                        round(score, 4)))
                    selected_items.sort(key=lambda x: x[2], reverse=True)
        else:
            for school_row in df.to_dict("records"):
                if compiled_pattern.search(school_row["name"].strip().lower()):
                    name_abbr = school_row["name_abbr"]
                    score = jaro.jaro_winkler_metric(simplified_query, name_abbr) * 100
                    selected_items.append((school_row["name"].title(), round(score, 4)))
                    selected_items.sort(key=lambda x: x[1], reverse=True)
        
            # Since we are not using the address, we can return the top 10 results.
            return selected_items[:10]

        """
        School names have been selected, now we need to select the top addresses.
        Make a regex for the address.
        """
        if place and full_or_common_words:
            pattern = r"(\b" + r"[a-z]*\s+".join(place) + r"[a-z]*\s+\b" + r"[a-z]*\s+".join(full_or_common_words) + r"[a-z]*\b){e<=2}"
        elif place:
            pattern = r"(\b" + r"[a-z]*\s+".join(place) + r"[a-z]*\b){e<=2}"
        elif full_or_common_words:
            pattern = r"(\b" + r"[a-z]*\s+".join(full_or_common_words) + r"[a-z]*\b){e<=2}"

        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        final_list = []


        # Loop over the schools in the selected_schools list to check if the address matches the regex
        for school in selected_items:
            name = school[0]
            address = school[1].strip().lower()
            address_abbr = school[2]
            name_score = school[3]

            if compiled_pattern.search(address):
                input_address = "".join(place) or " ".join(full_or_common_words)

                """
                Compare both the abbreviation and the full address with the query using
                jaro-winkler metric. We keep the greater score out of both.
                """
                score_1 = jaro.jaro_winkler_metric(input_address, address_abbr) * 100
                score_2 = jaro.jaro_winkler_metric(input_address, address) * 100
                score_address = max(score_1, score_2)

                """
                If the query is directly in the address, we add a bias of +5 to the score.
                For example, if the query is "rkp", and the address abbr is "sxrkpnd",
                we add a bias of +5
                """
                if input_address in address or input_address in address_abbr:
                    score_address += 5
                final_list.append(
                    (name,
                     address,
                     round(name_score, 4),
                     round(score_address, 4))
                     )
                final_list.sort(key=lambda x: (x[2], x[3]), reverse=True)

        """
        If the final_list is empty, it means that no address matched the regex,
        so return the top 10 school matches
        """
        if final_list == []:
            return selected_items[:10]
        top_ten = final_list[:10]
        top_ten = [(school[0], school[1].title(), round((school[2] + school[3]) / 2, 4))
                   for school in top_ten]
        return top_ten