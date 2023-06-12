import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import KMeans
from collections import Counter
from queue import PriorityQueue

class RecommendationSystem:
    def __init__(self, list_of_boards, subjects_queryset):
        self.list_of_boards = list_of_boards
        self.subjects_queryset = subjects_queryset
        self.model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
        self.streams_df = pd.read_csv(r"services\subject_recommendation\train\all_streams.csv", header=0)
        self.required_columns = ["name", "curriculum__abbreviation", "education_level"]
        self.all_boards_subjects_df = self.get_subjects_df_of_all_boards()

    # A function to get subjects of all boards from list of boards, and store them as dictionary
    # with board as key and values as dataframe of subjects of that board
    def get_subjects_df_of_all_boards(self):
        subjects_of_all_boards = {}
        df_from_queryset = pd.DataFrame(list(self.subjects_queryset
                                             .values_list(*self.required_columns)),
                                             columns=self.required_columns)
        for board in self.list_of_boards:
            subjects_of_all_boards[board] = df_from_queryset[df_from_queryset['curriculum__abbreviation'] == board]
        return subjects_of_all_boards

    def select_df_by_board(self, board):
        """ This function selects the board and returns the dataframe of subjects of that board"""
        return self.all_boards_subjects_df[board]

    def filter_logic_combinations(self, curriculum, education_level):
        df = self.streams_df
        data_streamcomb = {}
        columns = df.columns.tolist()
        for index, row in df.iterrows():
            if row['curriculum'] == curriculum and row['education_level'] == education_level:
                data_streamcomb[index] = tuple(row['streams'].split(', '))
        return data_streamcomb

    def filter_logic_subjects(self, curriculum, education_level):
        # for the fallback, subjects from the main unisen database
        df = self.select_df_by_board(curriculum)
        data_subjects = {}

        for index, row in df.iterrows():
            if row['curriculum'] == curriculum.lower() and row['education_level'] == education_level.lower():
                data_subjects[index] = row['name']
        return data_subjects

    def recomm_logic(self, input_subjects, curriculum, education_level):
        """The function recommends different logic considering the requirement. If
        there are no input_subjects passed, it will recommend based on the initial function.
        If a board is specified and input subjects are present, it will recommend based
        on the streams function. If none is returned, it will revert to the model function.
        Arguments: input_subjects list.
        Returns: Subject recommendations"""

        if len(input_subjects) == 0:
            data = self.filter_logic_combinations(curriculum, education_level)
            recommendations = self.get_initial_recommendations(data)

            if recommendations:
                return recommendations

        data = self.filter_logic_combinations(curriculum, education_level)
        recommendations = self.get_streamwise_recommendations(input_subjects, data)

        if recommendations:
            return recommendations

        data = self.filter_logic_subjects(curriculum, education_level)
        recommendations = self.get_modelwise_recommendation(input_subjects, data)

        if recommendations:
            return recommendations

        # If no recommendations are found
        return "No recommendations available."


    def encode_subjects(self, data):
        """The function encodes the subjects in the CSV file which is loaded. It uses the
        utilities from the Sentence Transformers library to encode the subjects.
        Returns: Encoded Subjects"""

        vectors = self.model.encode(list(data.values()))
        return dict(zip(data.values(), vectors))

    def load_streams_and_get_subject_frequency(self, data):
        """This function generates a dictionary containing the frequency of occurrence
        of each subject in the streams list to each of the subject in it.
        Returns: Dictionary of Frequency of Subjects"""

        all_streams = data.values()
        subject_frequency = {}
        for stream in all_streams:
            for subject in stream:
                if subject not in subject_frequency:
                    subject_frequency[subject] = {}
                for other_subject in stream:
                    if other_subject != subject:
                        subject_frequency[subject][other_subject] = subject_frequency[subject].get(other_subject, 0) + 1
        return subject_frequency

    def get_modelwise_recommendation(self, input_subjects, data):
        """This function recommends subjects using the Sentence Transformers Model. For each
        input subject, it will take the mean and recommend subjects related to the mean value obtained.
        Arguments: input_subjects list
        Returns: List of recommendations based on the model"""

        similarity_queue = PriorityQueue()
        input_vectors = self.model.encode(input_subjects)
        mean_vector = np.mean(input_vectors, axis=0)
        for subject, vector in self.encode_subjects(data).items():
            if subject not in input_subjects:
                sim = util.cos_sim(np.array([mean_vector]), np.array([vector]))[0][0]
                similarity_queue.put((sim, subject))

        recommendations = []
        while not similarity_queue.empty() and len(recommendations) < 6:
            similarity, subject = similarity_queue.get()
            recommendations.append(subject)
        return recommendations

    def get_initial_recommendations(self, data):
        """This function generates a set of four initial recommendations based on the
        frequencies generated previously. The frequencies are normalized and then sorted.
        It makes use of the K means clustering and divides the data into 7 clusters out of
        which one subject each is appended to the recommended list and four is returned.
        Returns: Initial Recommendations"""

        subject_frequency = self.load_streams_and_get_subject_frequency(data)
        for subject, scores in subject_frequency.items():
            max_score = np.amax(list(scores.values()))
            for sub, score in scores.items():
                normalized_score = score / max_score
                subject_frequency[subject][sub] = normalized_score

        sum_dict = {}
        for subject, scores in subject_frequency.items():
            for key, value in scores.items():
                sum_dict[key] = sum_dict.get(key, 0) + value

        sorted_dict = dict(sorted(sum_dict.items(), key=lambda x: x[1], reverse=True))
        subjects = list(sorted_dict.keys())
        similarity_scores = np.array(list(sorted_dict.values())).reshape(-1, 1)

        k = 7
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(similarity_scores)
        cluster_labels = kmeans.labels_

        clusters = {}
        for subject, label in zip(subjects, cluster_labels):
            cluster = clusters.get(label, [])
            cluster.append(subject)
            clusters[label] = cluster

        recommended_subjects = [subjects[0] for label, subjects in clusters.items()]
        return recommended_subjects[:4]

    def get_streamwise_recommendations(self, input_subjects, data):
        """This function generates a list of six recommendations using the Counter method and
        based on the subject frequency of occurrence. It identifies all the streams that could
        include the input subjects, count the number of times each subject occurs, and recommend
        the top six subjects.
        Arguments: Input subjects list
        Returns: List of six recommendations based on the streams"""

        stream_identify = {tuple(stream) for stream in data.values() if all(subject in stream for subject in input_subjects)}
        all_subjects = Counter(item for stream in stream_identify for item in stream if item not in input_subjects)
        recommended_subjects = sorted(all_subjects, key=lambda x: all_subjects[x], reverse=True)[:6]
        return recommended_subjects


curriculum = 'CBSE'
education_level = 'hsc'
input_subjects = ['Hindi']
recommendation_system = RecommendationSystem()
recommendations = recommendation_system.recomm_logic(input_subjects, curriculum, education_level)
print(recommendations)