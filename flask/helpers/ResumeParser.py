import re
import json
from langchain_community.document_loaders import UnstructuredWordDocumentLoader

class ResumeParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.loader = UnstructuredWordDocumentLoader(self.file_path, mode="elements")
        self.data = self.loader.load()
        self.resume_struct = {
            'skills': {},
            'experience': {},
            'projects': {},
            'education': []
        }
        self.current_header = ""
        self.current_minor_header = ""

    def parse_skills(self, content: str):
        match = re.search(r'(?i)^(languages:|technologies:|frameworks:)', content)
        if match:
            split_content = content.split(match.group(1), maxsplit=1)
            self.resume_struct['skills'][match.group(1).lower()] = split_content[1].strip()

    def parse_experience(self, content: str):
        if content not in self.resume_struct['experience']:
            self.resume_struct['experience'][content] = []

    def parse_education(self, content: str):
        self.resume_struct['education'].append(content)
    
    def parse_projects(self, content: str):
        if content not in self.resume_struct['projects']:
            self.resume_struct['projects'][content] = []

    def parse(self):
        HEADING_KEYWORDS = [
            "experience", "education", "skills", "summary", "projects",
            "certifications", "awards", "accomplishments"
        ]

        for line in self.data:
            if 'category' in line.metadata and line.metadata['category'] == 'Title' and line.page_content.lower() in HEADING_KEYWORDS:
                self.current_header = line.page_content.lower()
            elif 'category' in line.metadata and line.metadata['category'] == 'Title':
                self.current_minor_header = line.page_content
                if self.current_header == 'skills':
                    self.parse_skills(line.page_content)
                elif self.current_header == 'experience':
                    self.parse_experience(line.page_content)
                elif self.current_header == 'education':
                    self.parse_education(line.page_content)
                elif self.current_header == 'projects':
                    self.parse_projects(line.page_content)
            else:
                if self.current_header not in self.resume_struct or self.current_minor_header not in self.resume_struct[self.current_header]:
                    continue
                self.resume_struct[self.current_header][self.current_minor_header].append(line.page_content)

    def save_as_json(self, output_path: str):
        with open(output_path, 'w') as json_file:
            json.dump(self.resume_struct, json_file, indent=4)

    def as_json(self):
        return self.resume_struct

    def as_str(self):
        return json.dumps(self.resume_struct, indent=4)

if __name__ == '__main__':
    # Usage example:
    parser = ResumeParser('resume.docx')
    parser.parse()
    parser.save_as_json('resume.json')
