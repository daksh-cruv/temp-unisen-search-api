import pandas as pd
import pickle
import re


class DataLoader:

    """
    The following class is used to load the data from the pkl files.
    It cleans the data in dataframe by removing unwanted characters.
    """

    def load_pkl(self, file_name: str):
        dir_path = r"services\data\cache\\"
        file_path = dir_path + file_name
        with open(file_path, "rb") as f:
            return pickle.load(f)


    def clean_data(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        df[column] = df[column].apply(self.clean_string)
        return df


    def clean_string(self, s: str) -> str:
        s = s.lower().strip()
        s = re.sub(r' +', ' ', s)
        s = re.sub(r'[\.\,\"\'\(\)\-]', '', s)
        s = re.sub(r'\b\D\b(\s+\b\D\b)+', lambda x: x.group(0).replace(' ', ''), s)
        return s
    

    def remove_extra_spaces(self, s: str) -> str:
        s = re.sub(r' +', ' ', s)
        return s


    def create_abbreviation(self, s: str) -> str:
        split_s = s.split(" ")
        if len(split_s) > 1:
            first_letters = [word[0] for word in split_s]
            abbr = "".join(first_letters)
        else:
            abbr = split_s[0]
        
        # remove numbers from the abbreviation
        abbr = re.sub(r'\d+', '', abbr)
        return abbr.strip().lower()
    

    def create_dataframe_from_queryset(self,
                                       queryset,
                                       required_columns: list) -> pd.DataFrame:
        """
        This function receives a queryset and a list of required columns.
        It creates a dataframe from the queryset and returns the dataframe,
        having the required columns.
        """

        data = list(queryset.values_list(*required_columns))
        df = pd.DataFrame(data, columns=required_columns)

        if "address" in required_columns:
            df["name"] = df["name"].apply(self.remove_extra_spaces)
            df["name_first_letter_ascii"] = df["name"].apply(self.get_first_char_ascii)
            df["name_abbr"] = df["name"].apply(self.create_abbreviation)
            df["address_abbr"] = df["address"].apply(self.create_abbreviation)
            df["concat"] = df["name"] + " " + df["address"]
            df["concat"] = df["concat"].apply(self.clean_string)
        elif "alias" in required_columns:
            df["name"] = df["name"].apply(self.remove_extra_spaces)
            df["name_first_letter_ascii"] = df["name"].apply(self.get_first_char_ascii)
            df["concat"] = df["name"] + " " + df["alias"].fillna("")
            df["concat"] = df["concat"].apply(self.clean_string)
        else:
            df["name"] = df["name"].apply(self.remove_extra_spaces)
            df["name_first_letter_ascii"] = df["name"].apply(self.get_first_char_ascii)
            df["name_abbr"] = df["name"].apply(self.create_abbreviation)
            df["concat"] = df["name"].apply(self.clean_string)
            df["concat"] = df["concat"].apply(self.clean_string)

        # using dictionary to convert specific columns to specific datatype
        convert_dict = {
                        'name_first_letter_ascii': int
                        }
        df = df.astype(convert_dict)
        return df


    def get_first_char_ascii(self, s: str) -> int:
        s = s.lower().strip()
        return ord(s[0])