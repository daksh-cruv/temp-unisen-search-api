from sentence_transformers import SentenceTransformer, util
import pandas as pd
from fuzzywuzzy import fuzz, process
import numpy as np


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
        self.model_name = 'all-MiniLM-L6-v2'
        self.model = SentenceTransformer(self.model_name)


    def fuzzy_using_ST(self,
                       query: str,
                       df: pd.DataFrame,
                       embeddings) -> list:

        query_embedding = self.model.encode(query)

        # get all the embeddings values in a numpy array
        embeddings_array = np.array(list(embeddings.values()))

        query_embedding = np.array(query_embedding)
        cosine_similarities = util.pytorch_cos_sim(query_embedding, embeddings_array)

        # get the indices of the top k most similar embeddings
        k = 25
        flattened_cosine_similarities = cosine_similarities.flatten()
        sorted_indices = (-flattened_cosine_similarities).argsort()[:k]

        # get the top k names
        top_k_names = [list(embeddings.keys())[index] for index in sorted_indices]

        # get the top k scores from the indices
        top_k_scores = [flattened_cosine_similarities[index] for index in sorted_indices]

        # Perform fuzzy matching on the top k names
        top_5_matches = process.extractBests(query, top_k_names, scorer=fuzz.token_set_ratio, limit=5)

        # get respective scores
        top_5_scores = [top_k_scores[top_k_names.index(match[0])] for match in top_5_matches]

        # convert the tensor values to float and scale similarity scores to 100
        top_5_scores = [(score.item() * 100) for score in top_5_scores]

        # append the similarity scores to the fuzzy (match, score) tuple
        top_5_matches = [(match[0], match[1], score) for match, score in zip(top_5_matches, top_5_scores)]

        # do weighted sum of fuzzy and context scores as (0.3 * fuzzy + 0.7 * context)
        top_5_matches = [(match[0], (match[1] * 0.3) + (match[2] * 0.7)) for match in top_5_matches]

        final_list = []
        
        # Extract the school name, address, and score for the top 5 matches and append
        # them to the final list.
        for match in top_5_matches:
            try:
                name = df.loc[df["concat"] == match[0], "name"].values[0]
            except IndexError:
                # Index error occurs when the dataframe does not have a matching name
                continue
            score = match[1]
            try:
                address = df.loc[df["concat"] == match[0], "address"].values[0]
                final_list.append((name.title(), address.title(), score))
            except KeyError:
                # If the dataframe does not have the address column, then append only the name and score
                final_list.append((name.title(), score))

        return final_list