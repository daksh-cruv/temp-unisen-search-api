import pandas as pd
import pickle
import re


class DataLoader:

    """
    The following class is used to load the data from the csv files, as well as the encoded pkl files.
    It cleans the data in dataframe by removing unwanted characters and converting the string to lowercase.
    """

    # Function to load the pkl file using pickle
    def load_pkl(self, file_name: str):
        dir_path = r"services\data\cache\\"
        file_path = dir_path + file_name
        with open(file_path, "rb") as f:
            return pickle.load(f)


    # Function to clean the data in the dataframe
    def clean_data(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        df[column] = df[column].apply(self.clean_string)
        return df


    # Function to clean the string
    def clean_string(self, s: str) -> str:
        # Convert the string to lowercase and remove unwanted characters using regular expressions.
        # Remove periods, quotes, hyphens, brackets from string using regex
        # Replace extra spaces with single space using regex: 
        s = s.lower().strip()
        s = re.sub(r' +', ' ', s)
        s = re.sub(r'[\.\,\"\'\(\)\-]', '', s)
        s = re.sub(r'\b\D\b(\s+\b\D\b)+', lambda x: x.group(0).replace(' ', ''), s)
        return s
    
    def remove_extra_spaces(self, s: str) -> str:
        # Replace extra spaces with single space using regex: 
        s = re.sub(r' +', ' ', s)
        return s
    

    def create_abbreviation(self, s: str) -> str:
        # Create abbreviation from the string
        split_name = s.split(" ")
        if len(split_name) > 1:
            first_letters = [name[0] for name in split_name]
            full_name_abbr = "".join(first_letters)
        else:
            full_name_abbr = split_name[0]
        
        # remove numbers from the abbreviation
        full_name_abbr = re.sub(r'\d+', '', full_name_abbr)
        return full_name_abbr.strip().lower()
    

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
            df["name_in_abbr"] = df["name"].apply(self.create_abbreviation)
            df["address_in_abbr"] = df["address"].apply(self.create_abbreviation)
            df["concat"] = df["name"] + " " + df["address"]
            df["concat"] = df["concat"].apply(self.clean_string)
        elif "alias" in required_columns:
            df["name"] = df["name"].apply(self.remove_extra_spaces)
            df["concat"] = df["name"] + " " + df["alias"].fillna("")
            df["concat"] = df["concat"].apply(self.clean_string)
        else:
            df["name"] = df["name"].apply(self.remove_extra_spaces)
            df["name_in_abbr"] = df["name"].apply(self.create_abbreviation)
            df["concat"] = df["name"].apply(self.clean_string)
            df["concat"] = df["concat"].apply(self.clean_string)

        return df