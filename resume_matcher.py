# Think of this like a Venn diagram. You have a circle of "Resume Skills" and a circle of "JD Skills".

# The overlapping part in the middle is called the Intersection. These are your matched skills.

# The part of the JD circle that doesn't overlap is called the Difference. These are your missing skills.

# purpose of SentenceTransformer is to convert text data (like your resume and job description) into numerical vectors that can be easily compared.
# purpose of cosine_similarity is to measure how similar two vectors are, which helps us determine how closely your resume matches the job description based on the skills listed.
# purpose of numpy is to handle the numerical data and perform operations like calculating the average similarity score, which gives us an overall measure of how well your resume matches the job description.
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
# The 'all-MiniLM-L6-v2' model is a pre-trained model that is designed to create meaningful vector representations of sentences. It is efficient and works well for tasks like semantic similarity, which is what we need for comparing the skills in your resume with those in the job description.
model = SentenceTransformer('all-MiniLM-L6-v2')

# Task 2: Extracting Matched and Missing Skills
def extract_match(resume_skills, jd_skills):
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)
    similarity = resume_set.intersection(jd_set)
    missing = jd_set.difference(resume_set)
    score = (len(similarity) / len(jd_set) * 100) if jd_set else 0
    return {
        "matched_skills": list(similarity),
        "missing_skills": list(missing),
        "match_score": score}

# Task 3: Build the Semantic Similarity Function
def semantic_similarity(resume, jd):
    # the reason we don't use np model.encode directly is because it returns a 1D array, and the cosine_similarity function expects 2D arrays. By reshaping the vectors to 2D arrays, we can ensure that they are in the correct format for the cosine_similarity function to compute the similarity score accurately.
    resume_vector = model.encode(resume)
    jd_vector = model.encode(jd)
    
    # reshaping the vectors to 2D arrays for cosine_similarity function
    resume_vector = resume_vector.reshape(1, -1)
    jd_vector = jd_vector.reshape(1, -1)
    similarity_score = cosine_similarity(resume_vector, jd_vector)[0][0]
    return similarity_score*100
resume = "Experienced web developer skilled in HTML, CSS, JavaScript, and React."
jd = "Seeking a software engineer with experience in Python and machine learning."
print(semantic_similarity(resume, jd))

# Task 4: Integrate the Functions by creating master function that combines the matched/missing skills and the semantic similarity score into a comprehensive report.
def get_match_score(resume_text, jd_text, resume_skills, jd_skills):
    matched_missing_score = extract_match(resume_skills, jd_skills)
    similarity_score = semantic_similarity(resume_text, jd_text)
    # The weights (0.40 for matched/missing skills and 0.60 for semantic similarity) are chosen to reflect the importance of both factors in determining the overall match score. The matched/missing skills provide a direct measure of how well the specific skills in the resume align with those required by the job description, while the semantic similarity captures the overall contextual relevance of the resume to the job description. By combining these two scores with appropriate weights, we can get a more comprehensive assessment of how well the resume matches the job description.
    final_score = matched_missing_score*0.40 + similarity_score*0.60
    return {
        "Final Score (%)": round(final_score, 2),
        "Exact Skills Score (%)": round(matched_missing_score, 2),
        "AI Context Score (%)": round(similarity_score, 2),
        "Matched Skills": matched_missing_score["matched_skills"],
        "Missing Skills": matched_missing_score["missing_skills"]
    }


