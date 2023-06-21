Recommendation System
This is a recommendation system implemented in Python that suggests subjects based on input subjects and a specified board. The system uses various libraries and techniques to generate recommendations.

Dependencies
The following libraries are required to run the recommendation system:

pandas (imported as pd)
numpy (imported as np)
sentence_transformers (imported as SentenceTransformer, util)
sklearn.cluster (imported as KMeans)
collections (imported as Counter)
queue (imported as PriorityQueue)
Make sure these libraries are installed before running the recommendation system.


Class: RecommendationSystem
Methods
__init__(self, board): Initializes the RecommendationSystem object with the specified board. It also loads the subject data from a CSV file, encodes the subjects using a Sentence Transformers model, and retrieves the initial recommendations based on subject frequencies.

recomm_logic(self, input_subjects): Recommends subjects based on the input subjects. If no input subjects are provided, it returns the initial recommendations. If there are input subjects, it tries to generate recommendations based on streams. If stream-based recommendations are not available, it falls back to the model-based recommendations.

choose_streams_file(self): Returns the name of the text file containing subject combinations based on the specified board.

encode_subjects(self): Encodes the subjects from the loaded CSV file using a Sentence Transformers model.

get_all_streams(self): Reads the streams text file and returns a list of streams.

load_streams_and_get_subject_frequency(self): Generates a dictionary containing the frequency of occurrence of each subject in the streams.

get_modelwise_recommendation(self, input_subjects): Recommends subjects using the Sentence Transformers model. For single input subjects, it suggests subjects similar to the input subject. For multiple input subjects, it recommends subjects related to the mean value of the input subject vectors.

get_initial_recommendations(self): Generates four initial recommendations based on subject frequencies. It normalizes the frequencies, applies K-means clustering, and selects one subject from each cluster.

get_streamwise_recommendations(self, input_subjects): Generates six recommendations based on subject frequency of occurrence in the streams that include the input subjects.

Attributes
board: Specifies the board (e.g., 'CBSE', 'ICSE', 'IGCSE').
df: DataFrame containing subject data loaded from a CSV file.
subjects_list: List of subjects extracted from the DataFrame.
model: Sentence Transformers model used for subject encoding.
subjects_vectors: Dictionary containing the encoded vectors for each subject.
all_streams_file: Name of the text file containing subject combinations based on the board.
initial_recommendations: List of initial recommendations based on subject frequencies.