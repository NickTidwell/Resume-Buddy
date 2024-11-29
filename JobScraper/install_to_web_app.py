import os
import json

def combine_json_files(directory, output_file):
    combined_list = []

    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    combined_list.extend(data)
                else:
                    print(f"Warning: {filename} does not contain a list. Skipping.")

    # Create the final output dictionary
    output_data = {"jobs": combined_list}

    # Write the combined list to the output file
    with open(output_file, 'w') as output:
        json.dump(output_data, output, indent=4)

# Example usage
combine_json_files('./', '../flask/jobs.json')
