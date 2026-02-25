# Think of this like a Venn diagram. You have a circle of "Resume Skills" and a circle of "JD Skills".

# The overlapping part in the middle is called the Intersection. These are your matched skills.

# The part of the JD circle that doesn't overlap is called the Difference. These are your missing skills.

# purpose of SentenceTransformer is to convert text data (like your resume and job description) into numerical vectors that can be easily compared.
# purpose of cosine_similarity is to measure how similar two vectors are, which helps us determine how closely your resume matches the job description based on the skills listed.
# purpose of numpy is to handle the numerical data and perform operations like calculating the average similarity score, which gives us an overall measure of how well your resume matches the job description.
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity
# import numpy as np
# The 'all-MiniLM-L6-v2' model is a pre-trained model that is designed to create meaningful vector representations of sentences. It is efficient and works well for tasks like semantic similarity, which is what we need for comparing the skills in your resume with those in the job description.
# model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_match(resume, jd_skills):
    resume_set = set(resume)
    jd_set = set(jd_skills)
    similarity = resume_set.intersection(jd_set)
    missing = jd_set.difference(resume_set)
    score = (len(similarity) / len(jd_set) * 100) if jd_set else 0
    return {
        "matched_skills": list(similarity),
        "missing_skills": list(missing),
        "match_score": score}
print(extract_match(["Python", "Data Analysis", "Machine Learning"], ["Python", "Data Analysis", "Communication"]))