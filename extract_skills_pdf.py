import spacy            
from spacy.matcher import PhraseMatcher
from skillNer.skill_extractor_class import SkillExtractor
from skillNer.general_params import SKILL_DB

# Load spaCy and initialize the SkillNER extractor
nlp = spacy.load("en_core_web_sm")
skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)

# Notice how it now just accepts 'text', not a file path!
def extract_skills(text):
    # Ask AI to extract skills from the text
    annotations = skill_extractor.annotate(text)
    
    # FIXED: consistent variable naming
    extracted_skills = []
    
    # Pull out exact matches (e.g., "Python")
    for match in annotations.get("results", {}).get("full_matches", []):
        skill = match['doc_node_value']
        extracted_skills.append(skill.lower())
        
    # Pull out complex/multi-word skills (e.g., "Machine Learning")
    for match in annotations.get("results", {}).get("ngram_scored", []):
        skill = match['doc_node_value']
        extracted_skills.append(skill.lower())
        
    # Return a clean list with no duplicates
    return list(set(extracted_skills))







