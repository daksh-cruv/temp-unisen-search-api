import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz, process
from sentence_transformers import SentenceTransformer, util


class FuzzyQueryMatcher:

    """
    Cosine similarity is used to identify the top k most similar embeddings to the input query.
    From these matches, fuzzywuzzy is applied to determine the top 5 most similar strings.
    The class assumes the presence of name and address columns in the dataset. If the
    address column is absent, only matches from the name column are returned.
    """
    def __init__(self):
        self.model_name = 'all-MiniLM-L6-v2'
        self.model = SentenceTransformer(self.model_name)


    def fuzzy_using_ST(self,
                       query: str,
                       df: pd.DataFrame,
                       embeddings) -> list:

        query_embedding = self.model.encode(query)
        embeddings_array = np.array(list(embeddings.values()))
        query_embedding = np.array(query_embedding)
        cosine_similarities = util.pytorch_cos_sim(query_embedding, embeddings_array)

        # get the indices of the top k most similar embeddings
        k = 25
        flattened_cosine_similarities = cosine_similarities.flatten()
        sorted_indices = (-flattened_cosine_similarities).argsort()[:k]

        # get the top k names and scores
        top_k_names = [list(embeddings.keys())[index] for index in sorted_indices]
        top_k_scores = [flattened_cosine_similarities[index] for index in sorted_indices]

        # Perform fuzzy matching on the top k names to find top 5 matches
        top_5_matches = process.extractBests(query, top_k_names, scorer=fuzz.token_set_ratio, limit=5)

        # get respective scores
        top_5_scores = [top_k_scores[top_k_names.index(match[0])] 
                        for match in top_5_matches]
        top_5_scores = [(score.item() * 100) for score in top_5_scores]

        # append the cos similarity scores to the fuzzy (match, score) tuple
        top_5_matches = [(match[0], match[1], score) 
                         for match, score in zip(top_5_matches, top_5_scores)]

        # do weighted sum of fuzzy and context scores as (0.3 * fuzzy + 0.7 * context)
        top_5_matches = [(match[0], (match[1] * 0.3) + (match[2] * 0.7)) 
                         for match in top_5_matches]

        final_list = []
        
        """
        Extract the school name, address, and score for the top 5 matches and append
        them to the final list.
        """
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
                # If the dataframe does not have the address column, then append onlythe name and score
                final_list.append((name.title(), score))

        return final_list