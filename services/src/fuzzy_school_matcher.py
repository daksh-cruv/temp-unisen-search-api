from sentence_transformers import SentenceTransformer, util
import pandas as pd
from fuzzywuzzy import fuzz, process


class FuzzySchoolMatcher:

    """
    In the below class, we have used sentence transformer model to encode the school names
    and addresses into embeddings. Then we use the cosine similarity between the input query and
    the dataset embeddings to find the top k most similar embeddings. After that, use fuzzywuzzy
    to find the top 5 most similar strings from the top k matches, using the token_set_ratio scorer.
    We assume name and address columns to be present. If address column is not present, we only
    perform fuzzy matching on the name column.
    """
    def __init__(self):

        # Define the model name for sentence transformation
        self.model_name = 'all-MiniLM-L6-v2'

        # Initialize the sentence transformer model
        self.model = SentenceTransformer(self.model_name)


    def fuzzy_using_ST(self,
                       query: str,
                       df: pd.DataFrame,
                       embeddings) -> list:

        query_embedding = self.model.encode(query)

        similarities = {}

        for name, embedding in embeddings.items():
            similarity = util.pytorch_cos_sim(query_embedding, embedding)
            similarities[name] = similarity.item()
        
        # Get the indices of the top k most similar embeddings
        sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

        k = 25
        # Get the indices top k most similar embeddings
        top_k_entries = sorted_similarities[:k]

        top_k_strings = [entry[0] for entry in top_k_entries]

        # Perform fuzzy matching on the top k addresses
        top_5_matches = process.extractBests(query, top_k_strings, scorer=fuzz.token_set_ratio, limit=5)

        final_list = []

        # Extract the school name, address, and score for the top 5 matches and append
        # them to the final list.
        for match in top_5_matches:
            name = df.loc[df["concat"] == match[0], "name"].values[0]
            score = match[1]
            try:
                address = df.loc[df["concat"] == match[0], "address"].values[0]
                final_list.append((name.title(), address.title(), score))
            except KeyError:
                # If the dataframe does not have the address column, then append only the name and score
                final_list.append((name.title(), score))

        return final_list