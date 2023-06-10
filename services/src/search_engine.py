from .abbr_school_matcher import AbbrSchoolMatcher
from .fuzzy_school_matcher import FuzzySchoolMatcher
import json
from .data_loader import DataLoader
import pandas as pd
from .check_pickle_exists import CheckPickleExists
from constants import SearchConstants


class SearchEngine(AbbrSchoolMatcher, FuzzySchoolMatcher):

    """
    This class loads the Dataframe and PKL files into memory and performs search.
    The 'search()' method performs search based on the word lengths in the query.
    """

    def __init__(self, queryset, dataset: str, options: list = None):

        self.loader = DataLoader()
        self.checker = CheckPickleExists(
            queryset=queryset,
            dataset=dataset,
            options=options
            )
        self.file_names = self.checker.get_file_names()

        # load data from json file
        self.json_file = r"services\data\input\query_data.json"
        self.json_data = json.load(open(self.json_file))

        self.pkl_data_holder = {}
        self.pkl_data_loader()

        self.dataset = dataset
        self.required_columns = self.get_required_column_list(dataset=self.dataset)
        self.queryset = queryset
        self.df = self.create_dataframe_from_queryset(self.queryset)

        # Initialize the AbbrSchoolMatcher and FuzzySchoolMatcher classes
        super().__init__()
        super(AbbrSchoolMatcher, self).__init__()


    def get_required_column_list(self, dataset: str):
        return self.json_data[dataset]["columns_required"]


    def create_dataframe_from_queryset(self, queryset):
        data = list(queryset.values_list(*self.required_columns))
        df = pd.DataFrame(data, columns=self.required_columns)

        if "address" in self.required_columns:
            df["concat"] = df["name"] + " " + df["address"]
            # clean all the data in concat column
            df["concat"] = df["concat"].apply(self.loader.clean_string)

        elif "alias" in self.required_columns:
            df["concat"] = df["name"] + " " + df["alias"].fillna("")
            # clean all the data in concat column
            df["concat"] = df["concat"].apply(self.loader.clean_string)

        else:
            df["concat"] = df["name"].apply(self.loader.clean_string)
            # clean all the data in concat column
            df["concat"] = df["concat"].apply(self.loader.clean_string)

        return df


    def pkl_data_loader(self):
        for dataset_name, file_name in self.file_names.items():
            pkl_data = self.loader.load_pkl(file_name)
            self.pkl_data_holder[dataset_name] = pkl_data


    def select_dataset(self, option: str = None) -> tuple:
        if not option:
            pkl_data = self.pkl_data_holder[self.dataset]
            return pkl_data
        else:
            pkl_data = self.pkl_data_holder[option]
            return pkl_data

    
    # function to subject search using fuzzy only
    def subject_search(self, query: str, filters: dict, embeddings) -> list:

        filtered_df = self.filter_df(filters=filters)
        query = self.loader.clean_string(query)
        results = self.fuzzy_search(query=query,
                                    df=filtered_df,
                                    embeddings=embeddings)
        return results
    

    def search(self,
               query: str,
               filter_dict: dict = None,
               subject: bool = False) -> list:
        
        if filter_dict:
            embeddings = self.select_dataset(
                option=filter_dict["curriculum__abbreviation"].lower()
                )
            filtered_df = self.filter_df(filters=filter_dict)
        else:
            filtered_df = self.df
            embeddings = self.select_dataset()
        
        
        if subject:
            return self.subject_search(
                query=query,
                filters=filter_dict,
                embeddings=embeddings
                )


        """
        Perform search based on word lengths in the query.
        if all words are less than or equal to 4 characters, perform abbreviation search
        if all words are greater than 4 characters, perform fuzzy search
        else perform both and combine the results.
        Fuzzy search requires a cleaned string, abbreviation search does not.
        """

        words = query.split()
        if all(len(word) <= SearchConstants.abbr_char_limit for word in words):
            results = self.abbreviation_search(query=query, df=filtered_df)

        # if the query contains only 1 word, and the word is less than or equal to 4 characters,
        # perform abbreviation search
        # TEST
        elif len(words) == 1 and len(words[0]) <= SearchConstants.abbr_single_word_str_threshold:
            results = self.abbreviation_search(query=query, df=filtered_df)

        elif all(len(word) > SearchConstants.abbr_char_limit for word in words):
            query = self.loader.clean_string(query)
            results = self.fuzzy_using_spellwise(query=query,
                                        df=filtered_df,
                                        embeddings=embeddings)

        else:
            abbreviation_results = self.abbreviation_search(query=query, df=filtered_df)
            query = self.loader.clean_string(query)
            fuzzy_results = self.fuzzy_using_spellwise(query=query,
                                              df=filtered_df,
                                              embeddings=embeddings)

            # Count the number of words with length <= 4 and > 4
            count_short_words = sum(1 for word in words if len(word) <= 4)
            count_long_words = sum(1 for word in words if len(word) > 4)

            """
            Adjust the score based on the count of short and long words.
            If the count of short words is less than the count of long words, adjust the score of fuzzy results,
            else adjust the score of abbreviation results.
            """
            if count_short_words < count_long_words:
                results = [(name, address, score + 10) if score is not None else None for name, address, score in fuzzy_results] + abbreviation_results
            else:
                results = fuzzy_results + [(name, address, score + 10) if score is not None else None for name, address, score in abbreviation_results]
                # results = fuzzy_results + abbreviation_results
        
        # Filter out non-null results, sort by score, and return
        non_null_results = [result for result in results if result is not None]
        try:
            non_null_results.sort(key=lambda x: x[2], reverse=True)
        except IndexError:
            non_null_results.sort(key=lambda x: x[1], reverse=True)
        except Exception:
            return non_null_results
        
        return non_null_results


    def fuzzy_search(self,
                     query: str,
                     df: pd.DataFrame,
                     embeddings) -> list:

        # Perform fuzzy search using FuzzySchoolMatcher's fuzzy_using_ST method
        return super().fuzzy_using_ST(query=query,
                                      df=df,
                                      embeddings=embeddings)


    def abbreviation_search(self,
                            query: str,
                            df = pd.DataFrame) -> list:

        # Perform abbreviation search using AbbrSchoolMatcher's abbreviation_search method
        return super().abbreviation_search(query=query, df=df)


    # function to filter the dataframe based on the filters
    # filters is a dictionary with key as column name and value as the value to be filtered
    def filter_df(self, filters: dict) -> list:

        filtered_df = self.df
        for key, value in filters.items():
            filtered_df = filtered_df[filtered_df[key] == value]

        return filtered_df


# search = SearchEngine()
# res = search.search(query="dps rkp", board="cbse")
# print(res)
