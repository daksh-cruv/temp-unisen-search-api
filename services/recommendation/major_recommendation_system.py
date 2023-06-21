import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from services.data_loader import DataLoader
from services.train_model import TrainModel


class MajorRecommendationSystem:

    """
    Used to generate the mapping between degrees and majors.
    Cosine similarity is used to find the most similar majors for each degree.
    The mapping is created in the form of a dictionary, where the key is the degree name
    and the value is a list of the top 3 most similar majors.
    """

    def __init__(self, degrees_queryset, majors_queryset):
        self.train_model = TrainModel()
        self.loader = DataLoader()
        self.degrees_df = pd.DataFrame(list(degrees_queryset.values_list("name", flat=True)),
                                       columns=["degree_name"])
        self.majors_df = pd.DataFrame(list(majors_queryset.values_list("name", flat=True)),
                                      columns=["major_name"])
        self.preprocess_data()
        self.generate_mapping_if_not_exists()
        self.check_if_data_updated()

        # self.save_mapping_to_csv(r"services\data\cache\major_recommendations.csv")
        self.csv_mappings = self.create_mapping_from_csv(r"services\data\cache\major_recommendations.csv")
        print("\nInitiated Major Recommendation System\n")


    def generate_mapping_if_not_exists(self):

        """
        Checks if the mapping exists. If it does not exist, 
        then it generates the mapping.
        """

        try:
            self.mapping = self.load_mapping()
        except FileNotFoundError:
            print("College major recommendations file not found. Generating mapping...")
            self.generate_mapping()
            self.mapping = self.load_mapping()


    def preprocess_data(self):
        self.degrees_df['degree_name'] = self.degrees_df['degree_name'].apply(lambda x: x.strip())
        self.majors_df['major_name'] = self.majors_df['major_name'].apply(lambda x: x.strip().title())


    def encode_embeddings(self):
        model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
        degree_embeddings = model.encode(self.degrees_df['degree_name'].tolist())
        major_embeddings = model.encode(self.majors_df['major_name'].tolist())
        self.similarity_matrix = cosine_similarity(degree_embeddings, major_embeddings)


    def generate_mapping(self):
        self.encode_embeddings()
        similarity_df = pd.DataFrame(self.similarity_matrix,
                                     columns=self.majors_df['major_name'],
                                     index=self.degrees_df['degree_name']
                                     )
        similarity_df = similarity_df.apply(lambda x: x.sort_values(ascending=False).index.tolist(),axis=1)
        top_3_majors = similarity_df.apply(lambda x: x[:3])
        top_3_majors_dict = top_3_majors.to_dict()

        print("Saving degree to major mapping...")
        self.train_model.save_embeddings(top_3_majors_dict, "major_recommendation_embeddings.pkl")


    def load_mapping(self, input_file="major_recommendation_embeddings.pkl"):
        return self.loader.load_pkl(input_file)
    

    def get_recommendations(self, degree_name):
        
        """
        Returns the top 3 most similar majors for a given degree.
        """
        try:
            return self.csv_mappings[degree_name]
        except KeyError:
            return "No recommendations found"
    

    def check_if_data_updated(self):

        """
        Check that the degrees in the database are the same as the degrees in the mapping.
        If they are not the same, then generate a new mapping.
        """
        degrees_in_df = self.degrees_df['degree_name'].tolist()
        degrees_in_mapping = list(self.mapping.keys())
        if set(degrees_in_df) != set(degrees_in_mapping):
            print("College major recommendation data is not up to date. Generating new mapping...")
            self.generate_mapping()
            self.mapping = self.load_mapping()
            print("New mapping generated")


    def save_mapping_to_csv(self, output_file: str):
        mapping = self.mapping
        data = []
        for degree, majors in mapping.items():
            data.append([degree, majors])
        df = pd.DataFrame(data, columns=['degree_name', 'top_3_majors'])

        df.to_csv(output_file, index=False)

        print("Major recommendations CSV file created successfully!")


    def create_mapping_from_csv(self, input_file: str):
        df = pd.read_csv(input_file)
        df['top_3_majors'] = df['top_3_majors'].apply(lambda x: eval(x))
        mapping = df.set_index('degree_name')['top_3_majors'].to_dict()
        print("\nMajor recommendation mapping created from CSV file\n")
        return mapping