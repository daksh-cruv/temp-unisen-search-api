import csv

def txt_to_csv(curriculum):
    # Define the input and output file paths
    input_file = "all_streams_" + curriculum + ".txt"
    output_file = "all_streams_" + curriculum + ".csv"

    # Read the input file
    with open(input_file, "r") as file:
        data = file.read().strip().split("\n")

    # Prepare the data for CSV conversion
    rows = []
    for subjects in data:
        row = [curriculum, "hsc", subjects]
        rows.append(row)

    # Write the data to the CSV file
    with open(output_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["curriculum", "education_level", "streams"])
        writer.writerows(rows)

    print("CSV file created successfully!")

# Usage example:
txt_to_csv("IGCSE")
