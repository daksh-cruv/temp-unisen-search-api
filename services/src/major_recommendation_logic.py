import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .data_loader import DataLoader
from .train_model import TrainModel


class MajorRecommendationLogic:
    def __init__(self, degrees_queryset, majors_queryset):
        self.train_model = TrainModel()
        self.loader = DataLoader()
        self.degrees_df = pd.DataFrame(list(degrees_queryset.values_list("name", flat=True)), columns=["degree_title"])
        self.majors_df = pd.DataFrame(list(majors_queryset.values_list("name", flat=True)), columns=["Name"])
        self.generate_mapping_if_not_exists()
        print("\nInitiated Major Recommendation System\n")

    def generate_mapping_if_not_exists(self):
        try:
            self.mapping = self.load_mapping()
        except FileNotFoundError:
            print("File not found. Generating mapping...")
            self.generate_mapping()
            self.mapping = self.load_mapping()


    def preprocess_data(self):
        self.degrees_df['degree_name'] = self.degrees_df['degree_title'].apply(lambda x: x.strip())
        self.majors_df['major_name'] = self.majors_df['Name'].apply(lambda x: x.strip().title())

    def encode_embeddings(self):
        model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
        degree_embeddings = model.encode(self.degrees_df['degree_title'].tolist())
        major_embeddings = model.encode(self.majors_df['Name'].tolist())
        self.similarity_matrix = cosine_similarity(degree_embeddings, major_embeddings)

    def generate_mapping(self):
        self.preprocess_data()
        self.encode_embeddings()
        similarity_df = pd.DataFrame(self.similarity_matrix, columns=self.majors_df['major_name'], index=self.degrees_df['degree_name'])
        similarity_df = similarity_df.apply(lambda x: x.sort_values(ascending=False).index.tolist(), axis=1)
        top_3_majors = similarity_df.apply(lambda x: x[:3])
        top_3_majors_dict = top_3_majors.to_dict()

        print("Saving degree to major mapping...")
        self.train_model.save_embeddings(top_3_majors_dict, "major_recommendation_embeddings.pkl")

    def load_mapping(self, input_file="major_recommendation_embeddings.pkl"):
        return self.loader.load_pkl(input_file)
    
    def get_recommendations(self, degree_name):
        try:
            return self.mapping[degree_name]
        except KeyError:
            return "No recommendations found"