import customtkinter
from pypdf import PdfReader
from tkinter import filedialog as fd
from extract_skills_pdf import extract_skills
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")
app = customtkinter.CTk()
app.title("AI Resume Matcher")
app.geometry("900x600")
file_path_var = customtkinter.StringVar()
def calculate_match():
    # Placeholder function for calculating match score
    pass

def file_path():
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
        resume_text = extract_text_from_pdf(filename)
        print(resume_text)
        print(extract_skills(resume_text))
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
result_label = customtkinter.CTkLabel(bottom_frame, text="Match Score: N/A", font=customtkinter.CTkFont(size=16, weight="bold"))
result_label.pack(pady=30)



app.mainloop()