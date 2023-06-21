import json
import os
import warnings

import pandas as pd

from services.data_loader import DataLoader
from services.train_model import TrainModel


class CheckPickleExists():
    def __init__(self, queryset, dataset: str, options: list=None):

        self.loader = DataLoader()
        self.train = TrainModel()

        self.options = options
        self.dataset = dataset
        self.queryset = queryset

        self.get_column_list()
        self.df = self.loader.create_dataframe_from_queryset(
            queryset=queryset,
            required_columns=self.required_columns)

        self.generate_file_names()
        self.file_in_dir_list = self.get_dir_file_names()
        self.file_not_in_dir = self.check_file_exists()

        self.run_encode_df()
        self.check_each_pkl()


    def file_name_generator(self, dataset_name: str, options: list=None) -> dict:

            """
            Generates name of the pkl file based on the dataset.
            If the dataset is "college", then the pkl file name will be "college_embeddings.pkl"
            if the dataset is "school" and the options are "cbse", "icse", then the pkl
            file names will be "school_cbse_embeddings.pkl", "school_icse_embeddings.pkl".
            """

            if not options:
                file_names_with_curriculum = {}
                file_names_with_curriculum[dataset_name] = dataset_name + "_embeddings.pkl"
            else:
                file_names_with_curriculum = {}
                for option in options:
                    file_names_with_curriculum[option.lower()] = "{}_{}_embeddings.pkl"\
                        .format(dataset_name, option.lower())

            print("File names generated are:", file_names_with_curriculum)
            return file_names_with_curriculum
    

    def generate_file_names(self):
        
        """
        Generates the file names based on the dataset and options.
        """
        if self.options:
            self.file_names = self.file_name_generator(
                dataset_name = self.dataset,
                options = self.options
                )
        else:
            self.file_names = self.file_name_generator(dataset_name=self.dataset)


    def get_column_list(self) -> None:
        
        """
        Gets the list of columns required for the dataset from the json file.
        """
        self.json_file = r"services\data\input\query_data.json"
        self.json_data = json.load(open(self.json_file))
        self.required_columns = self.json_data[self.dataset]["columns_required"]


    def get_dir_file_names(self) -> list:
        
        """
        Returns the list of files present in the cache directory
        """
        path = r"services\data\cache\\"
        dir_list = os.listdir(path)
        return dir_list


    def check_file_exists(self) -> dict:

        """
        Checks if the pkl file exists in the cache directory or not.
        Returns the name of the pkl file that does not exist.
        """
        file_not_found = {}
        for option, file_name in self.file_names.items():
            if file_name not in self.file_in_dir_list:
                file_not_found[option] = file_name

        return file_not_found
    

    def filter_df(self, filters: dict) -> list:
        
        """
        Filters the dataframe based on the filters passed to it. The filters are passed
        as a dictionary. Keys are the column names and values are the values to be
        filtered on.
        """
        filtered_df = self.df
        for key, value in filters.items():
            if key in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[key] == value]
            else:
                warnings.warn("The column " + key + " is not present in the dataframe",
                              stacklevel=2)
        return filtered_df


    def run_encode_df(self) -> None:

        """
        Runs the encode_df function for each option in the options list
        """
        for option, file_name in self.file_not_in_dir.items():
            print("Encoding dataframe for", self.dataset, "dataset and", option.upper(), "option")
            filters = {"curriculum__abbreviation": option.upper()}
            self.encode_df(filters=filters, file_name=file_name)


    def encode_df(self, filters: dict, file_name: str) -> None:
        
        """
        Filters and then encodes the dataframe and saves it as
        a pkl file in the cache directory.
        """
        filtered_df = self.filter_df(filters=filters)
        self.train.train(df=filtered_df, file_name=file_name)
    

    def get_file_names(self) -> dict:
        return self.file_names
    

    def check_pickle_updated(self, df: pd.DataFrame, pkl_path: str) -> None:

        """
        First creates a set of the concat column values in df, then creates a set of the
        keys in pkl file. Perform set arithmetic to check if the values in df are
        in pkl file or not. If the values in df are not in pkl file, then encode the new
        values and update the pkl file. if there are more values in pkl file than in df,
        then delete the extra values from pkl file.
        """

        pkl_data = self.loader.load_pkl(file_name=pkl_path)
        df_values = set(df["concat"].values)
        pkl_keys = set(pkl_data.keys())

        values_to_encode = df_values - pkl_keys
        values_to_delete = pkl_keys - df_values

        if df_values == pkl_keys:
            print("No update required")
            print()
        
        elif values_to_encode:
            print("Encoding new values")
            print()
            self.train.update_pickle_values(data=values_to_encode, file_name=pkl_path)
            
        elif values_to_delete:
            print("Deleting extra values")
            print()
            self.train.delete_extra_values(data=values_to_delete, file_name=pkl_path)


    def check_each_pkl(self) -> None:

        """
        Checks for updates for each pkl file
        """
        for option, file_name in self.file_names.items():
            print("For", self.dataset, "dataset and", option, "option")
            filters = {"curriculum__abbreviation": option.upper()}
            filtered_df = self.filter_df(filters=filters)
            self.check_pickle_updated(df=filtered_df, pkl_path=file_name)
