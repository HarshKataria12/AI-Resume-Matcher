# Think of this like a Venn diagram. You have a circle of "Resume Skills" and a circle of "JD Skills".

# The overlapping part in the middle is called the Intersection. These are your matched skills.

# The part of the JD circle that doesn't overlap is called the Difference. These are your missing skills.

# purpose of SentenceTransformer is to convert text data (like your resume and job description) into numerical vectors that can be easily compared.
# purpose of cosine_similarity is to measure how similar two vectors are, which helps us determine how closely your resume matches the job description based on the skills listed.
# purpose of numpy is to handle the numerical data and perform operations like calculating the average similarity score, which gives us an overall measure of how well your resume matches the job description.
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
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

# Task 4: Integrate the Functions by creating master function that combines the matched/missing skills and the semantic similarity score into a comprehensive report.
def get_match_score(resume_text, jd_text, resume_skills, jd_skills):
    match_data = extract_match(resume_skills, jd_skills)
    
    # Extract the actual values from that dictionary
    score = match_data["match_score"]
    matched = match_data["matched_skills"]
    missing = match_data["missing_skills"]
    similarity_score = semantic_similarity(resume_text, jd_text)
    # The weights (0.40 for matched/missing skills and 0.60 for semantic similarity) are chosen to reflect the importance of both factors in determining the overall match score. The matched/missing skills provide a direct measure of how well the specific skills in the resume align with those required by the job description, while the semantic similarity captures the overall contextual relevance of the resume to the job description. By combining these two scores with appropriate weights, we can get a more comprehensive assessment of how well the resume matches the job description.
    final_score = score*0.40 + similarity_score*0.60
    return {
        "Final Score (%)": round(final_score, 2),
        "Exact Skills Score (%)": round(score, 2),
        "AI Context Score (%)": round(similarity_score, 2),
        "Matched Skills": matched,
        "Missing Skills": missing
    }


if __name__ == "__main__":
    print("\n" + "="*40)
    print("🚀 RUNNING AI RESUME MATCHER TESTS")
    print("="*40 + "\n")

    # ---------------------------------------------------------
    # TEST 1: The Perfect Match (High Exact, High Semantic)
    # ---------------------------------------------------------
    print("TEST 1: THE PERFECT MATCH")
    print("Expectation: High Exact Score, High AI Score")
    res_text_1 = "Backend developer with 5 years of Python, building REST APIs and managing SQL databases."
    jd_text_1 = "Looking for a backend developer skilled in Python, REST APIs, and SQL databases."
    res_skills_1 = ["python", "backend", "apis", "sql"]
    jd_skills_1 = ["python", "backend", "apis", "sql"]
    
    result_1 = get_match_score(res_text_1, jd_text_1, res_skills_1, jd_skills_1)
    print(f"Final Score: {result_1['Final Score (%)']}% | AI Score: {result_1['AI Context Score (%)']}% | Exact Skills Score: {result_1['Exact Skills Score (%)']}% | Matched Skills: {result_1['Matched Skills']} | Missing Skills: {result_1['Missing Skills']}")
    print("-" * 40)


    # ---------------------------------------------------------
    # TEST 2: The Complete Mismatch (Low Exact, Low Semantic)
    # ---------------------------------------------------------
    print("TEST 2: THE COMPLETE MISMATCH")
    print("Expectation: 0% Exact Score, Low AI Score")
    res_text_2 = "Graphic designer specializing in Adobe Illustrator, Photoshop, and brand identity."
    jd_text_2 = "Looking for a backend developer skilled in Python, REST APIs, and SQL databases."
    res_skills_2 = ["illustrator", "photoshop", "branding"]
    jd_skills_2 = ["python", "backend", "apis", "sql"]
    
    result_2 = get_match_score(res_text_2, jd_text_2, res_skills_2, jd_skills_2)
    print(f"Final Score: {result_2['Final Score (%)']}% | AI Score: {result_2['AI Context Score (%)']}% | Exact Skills Score: {result_2['Exact Skills Score (%)']}% | Matched Skills: {result_2['Matched Skills']} | Missing Skills: {result_2['Missing Skills']}")
    print("-" * 40)


    # ---------------------------------------------------------
    # TEST 3: The AI Magic (Low Exact, High Semantic)
    # ---------------------------------------------------------
    print("TEST 3: THE AI MAGIC (Different Words, Same Meaning)")
    print("Expectation: 0% Exact Score, but a solid AI Score because the concepts are similar.")
    res_text_3 = "AI Researcher building predictive models using neural networks and deep learning."
    jd_text_3 = "Machine Learning Engineer focused on natural language processing and statistical modeling."
    
    res_skills_3 = ["neural networks", "deep learning", "predictive models"]
    jd_skills_3 = ["machine learning", "nlp", "statistical modeling"]
    
    result_3 = get_match_score(res_text_3, jd_text_3, res_skills_3, jd_skills_3)
    print(f"Final Score: {result_3['Final Score (%)']}% | AI Score: {result_3['AI Context Score (%)']}% | Exact Skills Score: {result_3['Exact Skills Score (%)']}% | Matched Skills: {result_3['Matched Skills']} | Missing Skills: {result_3['Missing Skills']}")
    print("-" * 40)


    # ---------------------------------------------------------
    # TEST 4: The Edge Case (Empty Job Description)
    # ---------------------------------------------------------
    print("TEST 4: THE EDGE CASE (Empty JD Skills)")
    print("Expectation: Should not crash! Should handle the division by zero safely.")
    res_text_4 = "Great software engineer."
    jd_text_4 = "We don't really know what we want yet."
    res_skills_4 = ["software engineering"]
    jd_skills_4 = [] 
    
    result_4 = get_match_score(res_text_4, jd_text_4, res_skills_4, jd_skills_4)
    print(f"Final Score: {result_4['Final Score (%)']}% | AI Score: {result_4['AI Context Score (%)']}% | Exact Skills Score: {result_4['Exact Skills Score (%)']}% | Matched Skills: {result_4['Matched Skills']} | Missing Skills: {result_4['Missing Skills']}")
    print("="*40 + "\n")

    # Test 5 : My own CV:
    # ---------------------------------------------------------
    # TEST 6: HARSH vs. BETTERMILE (The Real Deal)
    # ---------------------------------------------------------
    print("TEST 6: HARSH'S CV vs. BETTERMILE DATA/ML ROLE")
    
    # Your CV Text & Skills
    res_text_bm = """Computer Science student in Berlin, Germany. Experience with Python, SQL, 
    Exploratory Data Analysis (EDA), Machine Learning Pipeline Automation, evaluating classification models, 
    data preprocessing, and visualizations using Pandas, Matplotlib, and Scikit-learn. English professional."""
    
    res_skills_bm = ["python", "sql", "exploratory data analysis", "machine learning", "data pipelines", 
                     "data preprocessing", "pandas", "scikit-learn", "matplotlib", "english", "analytical thinking"]
    
    # Bettermile JD Text & Skills
    jd_text_bm = """Data role at Bettermile in Berlin. Tasks include Exploratory Data Analysis (EDA), 
    evaluating ML models, data pipelines, and dashboards. Requires Python, SQL, data visualization, 
    statistical methods, English, and analytical thinking."""
    
    jd_skills_bm = ["python", "sql", "exploratory data analysis", "ml models", "data pipelines", 
                    "data visualization", "statistical methods", "english", "analytical thinking", "dashboards"]
    
    result_6 = get_match_score(res_text_bm, jd_text_bm, res_skills_bm, jd_skills_bm)
    
    print(f"Final Score: {result_6['Final Score (%)']}% | AI Score: {result_6['AI Context Score (%)']}% | Exact Skills Score: {result_6['Exact Skills Score (%)']}%")
    print(f"Matched Skills: {result_6['Matched Skills']}")
    print(f"Missing Skills: {result_6['Missing Skills']}")
    print("="*40 + "\n")