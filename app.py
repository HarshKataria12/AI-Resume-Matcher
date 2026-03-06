import customtkinter
from pypdf import PdfReader
from tkinter import filedialog as fd
from extract_skills_pdf import extract_skills
from resume_matcher import get_match_score
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")
app = customtkinter.CTk()
app.title("AI Resume Matcher")
app.geometry("900x600")
file_path_var = customtkinter.StringVar()
pdf_file_path = None
def calculate_match():

    jd_text = jd_textbox.get("1.0", "end-1c") # Get the text from the textbox
    # Check if the PDF file path and JD text are available
    if not pdf_file_path:
        result_label.configure(text="Please upload a resume PDF first.")
        return
    if not jd_text:
        result_label.configure(text="Please enter a Job Description in the textbox.")
        return
    # Update the result label to show that the AI is processing
    result_label.configure(text="AI is reading your resume... Please wait ⏳", text_color="yellow")
    app.update() # This forces the app to update the text on the screen instantly
    # Read the PDF Text
    resume_text = extract_text_from_pdf(pdf_file_path)
    # 5. UI Update: Extracting Skills
    result_label.configure(text="Extracting skills with AI... 🧠", text_color="yellow")
    app.update()
    result_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    if not result_skills:
        result_label.configure(text="No skills found in the resume PDF.")
        return
    if not jd_skills:
        result_label.configure(text="No skills found in the Job Description.")
        return
    # 6. UI Update: Running the Math
    result_label.configure(text="Calculating match score... 🧮", text_color="yellow")
    app.update()
    # Calculate the match score
    match_score = get_match_score(resume_text,jd_text,result_skills, jd_skills)
    
    # Extract the exact values from your dictionary
    final_score = match_score["Final Score (%)"]
    matched_skills = match_score["Matched Skills"]
    missing_skills = match_score["Missing Skills"]
    matched_str = ", ".join(matched_skills) if matched_skills else "None"
    missing_str = ", ".join(missing_skills) if missing_skills else "None"
        
        # Format the text beautifully
    display_text = (
        f"🎯 Final Match Score: {final_score}%\n\n"
        f"✅ Matched ({len(matched_skills)}): {matched_str}\n\n"
        f"❌ Missing ({len(missing_skills)}): {missing_str}"
    )
        
        # Update the UI
    result_label.configure(text=display_text, text_color="#00FF00")
    


    
    

def file_path():
    global pdf_file_path # Declare as global to modify the variable outside the function
    filetypes = (("PDF files", "*.pdf"), ("All files", "*.*"))
    filename = fd.askopenfilename(title="Open a file", initialdir="/", filetypes=filetypes)
    file_path_var.set(filename)
    customtkinter.CTkLabel(
    left_frame,
    text=file_path_var.get(),
    font=customtkinter.CTkFont(size=12),
    text_color="gray",
).pack(pady=(0, 14))
    if filename:
        pdf_file_path = filename

        print(f"Selected file: {filename}")

# open the pdf and extract text
def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
print("\n" + "="*40)

# Add a label
label = customtkinter.CTkLabel(app, text="Resume-Matcher", font=("Helvetica", 20))
label.pack(pady=20)
# --- MIDDLE: TWO COLUMNS ---
# Create a transparent wrapper frame to hold the left and right sides
middle_frame = customtkinter.CTkFrame(app, fg_color="transparent")
middle_frame.pack(fill="both", expand=True, padx=20)
# left frame
left_frame = customtkinter.CTkFrame(middle_frame)
left_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
# label for left frame
customtkinter.CTkLabel(
    left_frame,
    text="Select your resume PDF",
    font=customtkinter.CTkFont(size=12),
    text_color="gray",
).pack(pady=(0, 14))
#button

    

upload_btn = customtkinter.CTkButton(left_frame, text="Upload Pdf", font=customtkinter.CTkFont(size=12), command=file_path)
upload_btn.pack(padx=20, pady=10)


# right frame
right_frame = customtkinter.CTkFrame(middle_frame)
right_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
# label for right frame
customtkinter.CTkLabel(
    right_frame,
    text="Add your Job Description PDF",
    font=customtkinter.CTkFont(size=12),
    text_color="gray",
).pack(pady=(0, 14))
# large textbox
jd_textbox = customtkinter.CTkTextbox(right_frame, width=400, height=200)

# 2. Pack it onto the screen
jd_textbox.pack(padx=20, pady=10)
# bottom frame for calculate button and result label
bottom_frame = customtkinter.CTkFrame(app)
bottom_frame.pack(fill="x", padx=20, pady=(0, 20))
# calculate button
calculate_button = customtkinter.CTkButton(bottom_frame, text="Calculate Match Score", font=customtkinter.CTkFont(size=20, weight="bold"),height=50,command=calculate_match)
calculate_button.pack(pady=20, padx=40, fill="x")
# result label bottom
result_label = customtkinter.CTkLabel(
    bottom_frame, 
    text="Upload your Resume and Job Description to begin.", 
    font=customtkinter.CTkFont(size=14, weight="bold"),
    justify="center",
    wraplength=800  
)
result_label.pack(pady=(10, 20))



app.mainloop()