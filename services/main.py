from src.search_engine import SearchEngine


if __name__ == "__main__":
    # Initialize the search engine
    search_engine = SearchEngine()

    # Perform the search
    results = search_engine.search(query="dps rkp", board="cbse")

    # Print the results
    print("Results:")
    for result in results:
        print(result[0], result[1], result[2], sep="\n")
        print()