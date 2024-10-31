import difflib
from docx import Document
import os

def allowed_file(filename, allow_ext):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allow_ext

def extract_text(file_path):
    if file_path.endswith('.docx'):
        doc = Document(file_path)
        text = [para.text for para in doc.paragraphs]
    elif file_path.endswith('.txt'):
        with open(file_path, 'r') as file:
            text = file.readlines()
    else:
        text = []
    return text

def compare_documents(doc1_path, doc2_path):
    doc1_lines = extract_text(doc1_path)
    doc2_lines = extract_text(doc2_path)

    differ = difflib.Differ()
    diff = list(differ.compare(doc1_lines, doc2_lines))
    return diff

def generate_html_diff(diff):
    html_diff = ['<div style="display: flex;">']
    doc1 = []
    doc2 = []

    for line in diff:
        if line.startswith(' '):
            doc1.append(f'<div>{line[2:]}</div>')
            doc2.append(f'<div>{line[2:]}</div>')
        elif line.startswith('-'):
            doc1.append(f'<div style="background-color: #fdd; color: #d00;">{line[2:]}</div>')
        elif line.startswith('+'):
            doc2.append(f'<div style="background-color: #dfd; color: #080;">{line[2:]}</div>')

    html_diff.append(f'<div style="width: 50%; border-right: 1px solid #ccc; padding: 10px;">{"".join(doc1)}</div>')
    html_diff.append(f'<div style="width: 50%; padding: 10px;">{"".join(doc2)}</div>')
    html_diff.append('</div>')

    return ''.join(html_diff)

def append_llm_output(rel_output_file_path, updated_data):
    # Open the file in append mode; it will be created if it doesn't exist
    output_file_path = os.path.join(os.getcwd(), rel_output_file_path)  # Make sure to specify the correct path
    print("\n\nCWD:")
    print(os.getcwd())
    print(output_file_path)

    with open(output_file_path, 'a') as output_file:
        # Append the prompt_out followed by a newline for JSONL format
        output_file.write(updated_data + '\n')
        
