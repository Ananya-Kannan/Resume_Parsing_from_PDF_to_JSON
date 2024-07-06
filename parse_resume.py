import json
import pdfplumber
import re

def extract_contact_info(text):
    email_pattern = r'[\w\.-]+@[\w\.-]+'
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    
    email = re.findall(email_pattern, text)
    phone = re.findall(phone_pattern, text)
    
    return {
        "email": email[0] if email else None,
        "phone": phone[0] if phone else None,
    }

def extract_section(text, start_marker, end_marker=None):
    if end_marker:
        pattern = rf'{start_marker}(.*?){end_marker}'
    else:
        pattern = rf'{start_marker}(.*)'
    
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def parse_skills(skills_text):
    skills_list = re.split(r'[,\s]+', skills_text)
    return ', '.join(skills_list)

def parse_experience_section(experience_text):
    experiences = []
    # regular expression to capture company name, job title, and duration
    experience_pattern = re.compile(
        r'(?P<company>[^\n]+)\s+(?P<start_date>\d{2} \w{3}, \d{4})\s+-\s+(?P<end_date>Present|\d{2} \w{3}, \d{4})\n(?P<job_title>[^\n]+)',
        re.DOTALL
    )
    matches = experience_pattern.finditer(experience_text)
    
    for match in matches:
        experiences.append({
            "company": match.group('company').strip(),
            "job_title": match.group('job_title').strip(),
            "start_date": match.group('start_date').strip(),
            "end_date": match.group('end_date').strip()
        })
    
    return experiences

def parse_education_section(education_text):
    education_entries = []
    entries = education_text.split('\n')
    for i in range(0, len(entries), 2):
        if i + 1 < len(entries):
            education_entries.append({
                "institution": entries[i].strip(),
                "details": entries[i + 1].strip()
            })
    
    return education_entries


def parse_pdf_resume(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    
    contact_info = extract_contact_info(text)
    
    # Extracting sections using broad markers
    skills_text = extract_section(text, "KEY EXPERTISE", "EDUCATION")
    education_text = extract_section(text, "EDUCATION", "AWARDS AND SCHOLARSHIPS")
    experience_text = extract_section(text, "INTERNSHIPS", "PROJECTS")
    
    # If sections are not found by previous markers, using alternative markers
    if not skills_text:
        skills_text = extract_section(text, "KEY EXPERTISE")
    if not education_text:
        education_text = extract_section(text, "EDUCATION", "INTERNSHIPS")
    if not experience_text:
        experience_text = extract_section(text, "INTERNSHIPS", "KEY EXPERTISE")
    
    
    skills = parse_skills(skills_text) if skills_text else None
    education = parse_education_section(education_text) if education_text else None
    experience = parse_experience_section(experience_text) if experience_text else None
    
    resume_data = {
        "contact_information": contact_info,
        "skills": skills,
        "education": education,
        "experience": experience,
    }
    
    return json.dumps(resume_data, indent=4)

# Example usage
pdf_path = "PodAi Resume-K-Ananya.pdf"
parsed_resume = parse_pdf_resume(pdf_path)
print(parsed_resume)
