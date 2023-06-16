import pickle
from sentence_transformers import SentenceTransformer
from .data_loader import DataLoader
import pandas as pd


class TrainModel:

    """
    This class is used to train the sentence transformer model on the dataset.
    It loads the dataframe and encodes the concatenated columns into embeddings.
    The final embeddings are saved to a pickle file.
    """
    def __init__(self):
        
        self.model_name = 'all-MiniLM-L6-v2'
        self.model = SentenceTransformer(self.model_name)

        self.loader = DataLoader()


    def save_embeddings(self, embeddings, file_name: str):
        output_path = r"services\data\cache\\"
        dest_path = output_path + file_name

        with open(dest_path, "wb") as f:
            pickle.dump(embeddings, f)

        print("Embeddings saved to: ", dest_path, "\n")
    

    def train(self, df: pd.DataFrame, file_name: str):
        print("Encoding the model...")

        dataset_embeddings = {}
        
        """
        Encode the concatenated columns into embeddings, and save them to a dictionary
        with the key as the concatenated string and the value as the embedding
        """
        for index, row in df.iterrows():
            name_address = row["concat"]
            embedding = self.model.encode(name_address)
            dataset_embeddings[name_address] = embedding

        self.save_embeddings(dataset_embeddings, file_name)       


    # Function to update the pickle file by encoding the new values and saving them
    def update_pickle_values(self, data: set(), file_name: str):

        dataset_embeddings = self.loader.load_pkl(file_name)
        for value in data:
            embedding = self.model.encode(value)
            dataset_embeddings[value] = embedding
        self.save_embeddings(dataset_embeddings, file_name)


    def delete_extra_values(self, data: set(), file_name: str):
        dataset_embeddings = self.loader.load_pkl(file_name)
        for value in data:
            del dataset_embeddings[value]

        self.save_embeddings(dataset_embeddings, file_name)