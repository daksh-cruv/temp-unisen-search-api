from .abbr_query_matcher import AbbrQueryMatcher
from .fuzzy_query_matcher import FuzzyQueryMatcher
import json
from .data_loader import DataLoader
import pandas as pd
from .check_pickle_exists import CheckPickleExists
from constants import SearchConstants


class SearchEngine(AbbrQueryMatcher, FuzzyQueryMatcher):

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
        self.json_file = r"services\data\input\query_data.json"
        self.json_data = json.load(open(self.json_file))

        self.pkl_data_holder = {}
        self.pkl_data_loader()

        self.dataset = dataset
        self.required_columns = self.get_required_column_list(dataset=self.dataset)
        self.queryset = queryset
        self.df = self.loader.create_dataframe_from_queryset(self.queryset,
                                                             self.required_columns)

        super().__init__()
        super(AbbrQueryMatcher, self).__init__()


    def get_required_column_list(self, dataset: str):
        return self.json_data[dataset]["columns_required"]


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
        Perform search based on word lengths in the query. If all words are less than or
        equal to 4 characters, perform abbreviation search. If all words are greater than
        4 characters, perform fuzzy search, else perform both and combine the results.
        Fuzzy search requires a cleaned string, abbreviation search does not.
        """

        words = query.split()
        if all(len(word) <= SearchConstants.abbr_char_limit for word in words):
            results = self.abbreviation_search(query=query, df=filtered_df)
        
        elif len(words) == 1 and len(words[0]) <= SearchConstants.abbr_single_word_str_threshold:
            """
            If the query contains only 1 word, and the word is less than or equal to 5
            characters, perform abbreviation search.
            """

            results = self.abbreviation_search(query=query, df=filtered_df)

        elif all(len(word) > SearchConstants.abbr_char_limit for word in words):
            query = self.loader.clean_string(query)
            results = self.fuzzy_using_ST(query=query,
                                        df=filtered_df,
                                        embeddings=embeddings)

        else:
            abbreviation_results = self.abbreviation_search(query=query, df=filtered_df)
            query = self.loader.clean_string(query)
            fuzzy_results = self.fuzzy_using_ST(query=query,
                                              df=filtered_df,
                                              embeddings=embeddings)

            count_short_words = sum(1 for word in words if len(word) <= 4)
            count_long_words = sum(1 for word in words if len(word) > 4)

            """
            Adjust the score based on the count of short and long words. If the count of
            short words is less than the count of long words, adjust the score of fuzzy results,
            else adjust the score of abbreviation results.
            """
            try:
                if count_short_words < count_long_words:
                    results = [(name, address, score + 10) 
                               if score is not None else None 
                               for name, address, score in fuzzy_results] + abbreviation_results
                else:
                    results = fuzzy_results + [(name, address, score + 10) 
                                               if score is not None else None 
                                               for name, address, score in abbreviation_results]
            except ValueError:
                
                """
                ValueError occurs when the score is None in either fuzzy or abbreviation results.
                Score is None when no matches are not found in the dataset.
                In this case, we simply combine the results.
                """
                results = fuzzy_results + abbreviation_results

        not_null_results = [result for result in results if result is not None]
        try:
            not_null_results.sort(key=lambda x: x[2], reverse=True)
        except IndexError:
            not_null_results.sort(key=lambda x: x[1], reverse=True)
        except Exception:
            return not_null_results
        
        return not_null_results


    def fuzzy_search(self,
                     query: str,
                     df: pd.DataFrame,
                     embeddings) -> list:

        return super().fuzzy_using_ST(query=query,
                                      df=df,
                                      embeddings=embeddings)

    def abbreviation_search(self,
                            query: str,
                            df = pd.DataFrame) -> list:

        return super().abbreviation_search(query=query.strip().lower(), df=df)


    def filter_df(self, filters: dict) -> list:
        """
        Function to filter the dataframe based on the filters. "filters" is a dictionary
        with key as column name and value as the value to be filtered.
        """
        filtered_df = self.df
        for key, value in filters.items():
            filtered_df = filtered_df[filtered_df[key] == value]

        return filtered_df