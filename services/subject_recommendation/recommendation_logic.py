import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import KMeans
from collections import Counter
from queue import PriorityQueue

class RecommendationSystem:
    def __init__(self, list_of_boards):
        self.list_of_boards = list_of_boards

        self.df = pd.read_csv(r'services\subject_recommendation\Unisen School Datas - Curriculum CBSE.csv', header=0).dropna()
        self.subjects_list = self.df['Class 12'].tolist()
        self.model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
        self.subjects_vectors = self.encode_subjects()
        
        self.init_recomm_for_each_board = {}
        self.all_boards_streams_files = {}

        for board in self.list_of_boards:
            self.current_board_streams_file = self.generate_board_file_name(board)
            self.all_boards_streams_files[board] = self.current_board_streams_file
            self.initial_recommendations = self.get_initial_recommendations()
            self.init_recomm_for_each_board[board] = self.initial_recommendations
            print("Board: ", board, "Initial Recommendations: ", self.initial_recommendations)
        
        print(self.all_boards_streams_files)
        print("\nInitiated Recommendation System\n")
        # self.board = board
        # self.all_streams_file = self.choose_streams_file()
        # self.initial_recommendations = self.get_initial_recommendations()

        # print("\nInitiated Recommendation System\n")

    def recomm_logic(self, board, input_subjects):
        """ The function which recommends different logic considering the requirement. If 
        there is no input_subjects passed, it will recommend based on the initial function. 
        If there is a board specified and input subjects are present, it will recommend based 
        on streams function. If is none returned, it will revert to the model function.
        Arguments: input_subjects list.
        Returns: Subject recommendations"""

        self.current_board_streams_file = self.all_boards_streams_files[board]
        print("Board: ", board)
        print("Input Subjects: ", input_subjects)

        if len(input_subjects) == 0:
            return self.init_recomm_for_each_board[board]
        if len(input_subjects)>0:
            recommendations = self.get_streamwise_recommendations(input_subjects)

        if recommendations:
            return recommendations
        else:
            return self.get_modelwise_recommendation(input_subjects)

    def choose_streams_file(self):
        """ The function chooses a text file including combinations of subjects 
        based on the board that is chosen.
        Expected Input: board string
        Returns: Text file based on Board"""

        if self.board == 'CBSE':
            return r'services\subject_recommendation\all_streams_CBSE.txt'
        elif self.board == 'ICSE':
            return r'services\subject_recommendation\all_streams_ICSE.txt'
        elif self.board == 'IGCSE':
            return r'services\subject_recommendation\all_streams_IGCSE.txt'
        
    def encode_subjects(self):
        """ The function encodes the subjects in the CSV file which is loaded. It uses the 
        utilities from the Sentence Transformers library to encode the subjects.
        Expected Input: Subjects list from CSV
        Returns: Encoded Subjects"""

        vectors = self.model.encode(self.subjects_list)
        return dict(zip(self.df['Class 12'], vectors))

    def get_all_streams(self):
        """ The function reads the streams textfile and returns the list of streams 
        Expected Input: Streams Text File
        Returns: List of Streams"""

        with open(self.current_board_streams_file, 'r') as file:
            return [tuple(line.strip().split(', ')) for line in file]
    
    def load_streams_and_get_subject_frequency(self):
        """ This function generates a dictionary containing the frequency of occurence 
        of each subject in the streams list to each of the subject in it.
        Expected Input: List of Streams from Streams Text File 
        Returns: Dictionary of Frequency of Subjects"""

        all_streams = self.get_all_streams()
        subject_frequency = {}
        for stream in all_streams:
            for subject in stream:
                if subject not in subject_frequency:
                    subject_frequency[subject] = {}
                for other_subject in stream:
                    if other_subject != subject:
                        subject_frequency[subject][other_subject] = subject_frequency[subject].get(other_subject, 0) + 1
        return subject_frequency

    def get_modelwise_recommendation(self, input_subjects):
        """ This function recommends subjects using the Sentence Transformers Model. For 
        single subject in input subjects list, it will encode the input subject and suggest 
        subjects that are similar to it from the encoded subject vectors. For more than one 
        subject, it will take the mean and recommend subjects realted to the mean value obtained.
        Arguments: input subjects list
        Returns: List of recommendations based on model"""

        similarity_queue = PriorityQueue(maxsize=6)
        input_vectors = self.model.encode(input_subjects)
        mean_vector = np.mean(input_vectors, axis=0)
        for subject, vector in self.subjects_vectors.items():
            if subject not in input_subjects:
                sim = util.cos_sim(np.array([mean_vector]), np.array([vector]))[0][0]
                similarity_queue.put((sim, subject))

        recommendations = []
        while not similarity_queue.empty():
            similarity, subject = similarity_queue.get()
            recommendations.append(subject)
        return recommendations

    def get_initial_recommendations(self):
        """ This function generates a set of four initial recommendations based on the 
        frequencies generated previously. The frquencies are normalised and then sorted. 
        It makes use of the K means clustering and divide the data to 7 clusters out of 
        which one subject each is appended to the recommended list and four is returned.
        Returns: Initial Recommendations"""

        subject_frequency = self.load_streams_and_get_subject_frequency()
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

    def get_streamwise_recommendations(self, input_subjects):
        """This function generates a list of six recommendations using the Counter method and 
        based on the subject frequency of occurence. It identifies all the streams which could 
        include the input subjects, count the number of times each subject occurs and recommend 
        the top six subjects.
        Expected Input: List of Streams from Streams Text File
        Arguments: Input subjects list
        Returns: List of six recommendations based"""

        all_streams = self.get_all_streams()
        stream_identify = {stream for stream in all_streams if all(subject in stream for subject in input_subjects)}
        all_subjects = Counter(item for stream in stream_identify for item in stream if item not in input_subjects)
        recommended_subjects = sorted(all_subjects, key=lambda x: all_subjects[x], reverse=True)[:6]
        return recommended_subjects

    def generate_board_file_name(self, curriculum):
        file_path = r"services\subject_recommendation\\"
        file_name = "all_streams_" + curriculum + ".txt"
        return file_path + file_name


# board = 'CBSE'
# input_subjects = ['Chemistry']
# recommendation_system = RecommendationSystem(board)
# recommendations = recommendation_system.recomm_logic(input_subjects)
# print(recommendations)