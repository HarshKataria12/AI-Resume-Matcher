import threading
import customtkinter
from pypdf import PdfReader
from tkinter import filedialog as fd
from extract_skills_pdf import extract_skills
from resume_matcher import get_match_score

# ── App Setup ─────────────────────────────────────────────────────────────────
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.title("AI Resume Matcher")
app.geometry("900x600")

# Shared state
file_path_var = customtkinter.StringVar()
pdf_file_path = None
pdf_jd_path   = None
last_result_text = ""


# ── PDF helpers ───────────────────────────────────────────────────────────────
def extract_text_from_pdf(path):
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        error_msg = str(e)          # save the value NOW while still in except block
        app.after(0, lambda msg=error_msg: result_label.configure(text=f"...{msg}"))


# ── File pickers ──────────────────────────────────────────────────────────────
def file_path():
    global pdf_file_path
    filetypes = (("PDF files", "*.pdf"), ("All files", "*.*"))
    filename = fd.askopenfilename(title="Open a file", initialdir="/", filetypes=filetypes)
    if filename:
        file_path_var.set(filename)
        pdf_file_path = filename


def pick_jd_pdf():
    global pdf_jd_path
    filetypes = (("PDF files", "*.pdf"), ("All files", "*.*"))
    filename = fd.askopenfilename(title="Select JD PDF", initialdir="/", filetypes=filetypes)
    if filename:
        pdf_jd_path = filename
        jd_textbox.delete("1.0", "end")
        jd_textbox.insert("1.0", f"[PDF loaded: {filename.split('/')[-1]}]")


def clear_jd():
    """Clear the JD textbox and reset the JD PDF path."""
    global pdf_jd_path
    pdf_jd_path = None
    jd_textbox.delete("1.0", "end")


# ── Copy to clipboard ─────────────────────────────────────────────────────────
def copy_to_clipboard():
    app.clipboard_clear()
    app.clipboard_append(last_result_text)
    copy_btn.configure(text="✅ Copied!")
    app.after(2000, lambda: copy_btn.configure(text="📋 Copy Results"))


# ── Core processing (background thread — UI never freezes) ───────────────────
def _process():
    try:
        app.after(0, lambda: result_label.configure(
            text="AI is reading your resume... Please wait ⏳", text_color="yellow"))
        app.after(0, app.update_idletasks)

        resume_text = extract_text_from_pdf(pdf_file_path)
        if not resume_text.strip():
            app.after(0, lambda: result_label.configure(
                text="Could not extract text from the resume PDF.", text_color="red"))
            return

        # PDF takes priority over textbox for JD
        if pdf_jd_path:
            jd_text = extract_text_from_pdf(pdf_jd_path)
        else:
            jd_text = jd_textbox.get("1.0", "end-1c").strip()

        if not jd_text:
            app.after(0, lambda: result_label.configure(
                text="Please enter a Job Description or upload a JD PDF.", text_color="red"))
            return

        app.after(0, lambda: result_label.configure(
            text="Extracting skills with AI... 🧠", text_color="yellow"))
        app.after(0, app.update_idletasks)

        result_skills = extract_skills(resume_text)
        jd_skills     = extract_skills(jd_text)

        if not result_skills:
            app.after(0, lambda: result_label.configure(
                text="No skills found in the resume PDF.", text_color="red"))
            return
        if not jd_skills:
            app.after(0, lambda: result_label.configure(
                text="No skills found in the Job Description.", text_color="red"))
            return

        app.after(0, lambda: result_label.configure(
            text="Calculating match score... 🧮", text_color="yellow"))
        app.after(0, app.update_idletasks)

        match_score = get_match_score(resume_text, jd_text, result_skills, jd_skills)

        final_score    = match_score["Final Score (%)"]
        matched_skills = match_score["Matched Skills"]
        missing_skills = match_score["Missing Skills"]

        matched_str       = ", ".join(matched_skills) if matched_skills else "None"
        missing_str       = ", ".join(missing_skills) if missing_skills else "None"
        resume_skills_str = ", ".join(result_skills)  if result_skills  else "None"
        jd_skills_str     = ", ".join(jd_skills)      if jd_skills      else "None"

        display_text = (
            f"🎯 Final Match Score: {final_score}%\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📄 Your Resume Skills ({len(result_skills)}): {resume_skills_str}\n\n"
            f"📋 Job Description Skills ({len(jd_skills)}): {jd_skills_str}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✅ Matched ({len(matched_skills)}): {matched_str}\n\n"
            f"❌ Missing ({len(missing_skills)}): {missing_str}"
        )

        global last_result_text
        last_result_text = display_text

        app.after(0, lambda: result_label.configure(text=display_text, text_color="#00FF00"))
        # Show the copy button (it sits above the scroll area, always visible)
        app.after(0, lambda: copy_btn.configure(state="normal"))

    except Exception as e:
        app.after(0, lambda: result_label.configure(
            text=f"Unexpected error: {e}", text_color="red"))
    finally:
        app.after(0, lambda: calculate_button.configure(state="normal"))


def calculate_match():
    jd_text = jd_textbox.get("1.0", "end-1c").strip()

    if not pdf_file_path:
        result_label.configure(text="Please upload a resume PDF first.", text_color="red")
        return
    if not pdf_jd_path and not jd_text:
        result_label.configure(text="Please enter a Job Description or upload a JD PDF.", text_color="red")
        return

    calculate_button.configure(state="disabled")
    copy_btn.configure(state="disabled")
    thread = threading.Thread(target=_process, daemon=True)
    thread.start()


# ── UI Layout ─────────────────────────────────────────────────────────────────

label = customtkinter.CTkLabel(app, text="Resume-Matcher", font=("Helvetica", 20))
label.pack(pady=20)

middle_frame = customtkinter.CTkFrame(app, fg_color="transparent")
middle_frame.pack(fill="both", expand=True, padx=20)

# Left frame — Resume
left_frame = customtkinter.CTkFrame(middle_frame)
left_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

customtkinter.CTkLabel(
    left_frame, text="Select your resume PDF",
    font=customtkinter.CTkFont(size=12), text_color="gray",
).pack(pady=(0, 14))

file_name_label = customtkinter.CTkLabel(
    left_frame, textvariable=file_path_var,
    font=customtkinter.CTkFont(size=12), text_color="gray", wraplength=350,
)
file_name_label.pack(pady=(0, 14))

upload_btn = customtkinter.CTkButton(
    left_frame, text="Upload PDF",
    font=customtkinter.CTkFont(size=12), command=file_path,
)
upload_btn.pack(padx=20, pady=10)

# Right frame — Job Description
right_frame = customtkinter.CTkFrame(middle_frame)
right_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

customtkinter.CTkLabel(
    right_frame, text="Add your Job Description",
    font=customtkinter.CTkFont(size=12), text_color="gray",
).pack(pady=(0, 6))

# Row with Upload JD PDF + Clear buttons side by side
jd_btn_row = customtkinter.CTkFrame(right_frame, fg_color="transparent")
jd_btn_row.pack(pady=(0, 6))

upload_jd_btn = customtkinter.CTkButton(
    jd_btn_row, text="Upload JD PDF (optional)",
    font=customtkinter.CTkFont(size=11), height=28, width=180,
    fg_color="gray30", hover_color="gray40",
    command=pick_jd_pdf,
)
upload_jd_btn.pack(side="left", padx=(0, 8))

clear_jd_btn = customtkinter.CTkButton(
    jd_btn_row, text="🗑 Clear",
    font=customtkinter.CTkFont(size=11), height=28, width=80,
    fg_color="gray30", hover_color="#8B0000",
    command=clear_jd,
)
clear_jd_btn.pack(side="left")

jd_textbox = customtkinter.CTkTextbox(right_frame, width=400, height=200)
jd_textbox.pack(padx=20, pady=10)

# ── Bottom frame ──────────────────────────────────────────────────────────────
bottom_frame = customtkinter.CTkFrame(app)
bottom_frame.pack(fill="x", padx=20, pady=(0, 20))

calculate_button = customtkinter.CTkButton(
    bottom_frame, text="Calculate Match Score",
    font=customtkinter.CTkFont(size=20, weight="bold"),
    height=50, command=calculate_match,
)
calculate_button.pack(pady=20, padx=40, fill="x")

# ── Copy Results button — always visible, above the scroll area ───────────────
copy_btn = customtkinter.CTkButton(
    bottom_frame, text="📋 Copy Results",
    font=customtkinter.CTkFont(size=12), height=32,
    fg_color="gray30", hover_color="gray40",
    state="disabled",           # Greyed out until results are ready
    command=copy_to_clipboard,
)
copy_btn.pack(pady=(0, 8), padx=40, fill="x")

# Scrollable result area
result_scroll_frame = customtkinter.CTkScrollableFrame(
    bottom_frame, width=800, height=200, fg_color="transparent"
)
result_scroll_frame.pack(pady=(4, 20), fill="both", expand=True)

result_label = customtkinter.CTkLabel(
    result_scroll_frame,
    text="Upload your Resume and Job Description to begin.",
    font=customtkinter.CTkFont(size=14, weight="bold"),
    justify="left",
    wraplength=750,
)
result_label.pack(pady=10, padx=10)

# ── Run ───────────────────────────────────────────────────────────────────────
app.mainloop()