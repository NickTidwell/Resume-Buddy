import os
import json

def combine_jsonl_files(directory, output_file):
    with open(output_file, 'w') as outfile:
        for filename in os.listdir(directory):
            if filename.endswith('.jsonl'):
                file_path = os.path.join(directory, filename)
                print(filename)
                with open(file_path, 'r') as infile:
                    for line in infile:
                        outfile.write(line)

# Example usage
combine_jsonl_files('./', 'combined_output.jsonl')
