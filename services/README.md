# Unisen Institution Search
---

## Feature Description

The search engine is implemented as a feature for Unisen that searches and selects the user entered school name.

#### File descriptions:

- **abbr_school_matcher.py**: This Python file defines a class called `AbbrSchoolMatcher`, which contains a method named `abbreviation_search`. This method takes in an abbreviation query and a pandas DataFrame that contains school names and addresses. It aims to find schools that match the abbreviation query using regex.

- **fuzzy_school_matcher.py**: Defines a class called `FuzzySchoolMatcher`, which contains a method named `fuzzy_using_ST`. This method performs fuzzy matching of query on school names and addresses using sentence transformers and fuzzywuzzy library.

- **data_loader.py**: Provides a class called `DataLoader` that is responsible for loading and cleaning data from CSV files and encoded pickle (pkl) files.

- **get_common_words.py**: This file defines a class called `GetCommonWords` that is responsible for extracting the most common words from school names in the given datasets. Single as well as multiple datasets can be passed for the purpose. Please not that the **csv file paths can be provided as space separated command line arguments only.**

- **train_model.py**: The file provides a class `TrainModel` that is responsible for using a sentence transformer model to encode a dataset and save the encoded embeddings of school data to a pickle file. **An input file path and an output destination path must be given as space separated command line arguments.**

- **search_engine.py**: Defines a class called `SearchEngine`, which is a subclass of both `AbbrSchoolMatcher` and `FuzzySchoolMatcher`. It represents a search engine that performs school name searches based on different criteria. This class has a `search()` method that takes in the query and the affiliated board name and returns a list of matches.

---

#### Important Notes

- All the datasets as well as pickle files are present in the `data` folder.
- Each CSV file must be placed in the `input` folder within the `data` folder. Naming convention for csv dataset files is `"<board name>_schools.csv"`. For example: `cbse_schools.csv`.
- The destination path for the dumped pkl files must be in the `output` folder within `data` folder. Naming convention is `"<board name>_embeddings.pkl"`. For example: `icse_embeddings.pkl`.
- Each newly included csv dataset must be encoded using sentence transformers for the functioning of fuzzy search. Encode the dataset using `train()` method in `train_model.py`.
- The paths of .csv as well as .pkl file must be entered in `board_file_paths.json` present in `input` folder. The program uses this json files to load the respective dataset and embeddings. Make sure to take care of escape sequences using `\\`.
- In the `.json` file, make separate entries for each board as done before. Mention the board name and the respective file paths inside it. 