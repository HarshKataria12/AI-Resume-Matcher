import threading
import customtkinter
from pypdf import PdfReader
from tkinter import filedialog as fd, messagebox
from extract_skills_pdf import extract_skills
from resume_matcher import get_match_score

# ── App Setup ────────────────────────────────────────────────────────────────
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.title("AI Resume Matcher")
app.geometry("960x680")
app.resizable(True, True)

# Shared state
resume_path_var = customtkinter.StringVar()
jd_path_var = customtkinter.StringVar(value="Or paste text below ↓")
pdf_resume_path = None
pdf_jd_path = None
last_result_text = ""  # Used for copy-to-clipboard


# ── PDF Helpers ───────────────────────────────────────────────────────────────
def read_pdf(path: str) -> str:
    """Extract all text from a PDF file. Returns empty string on failure."""
    try:
        reader = PdfReader(path)
        return "".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        messagebox.showerror("PDF Error", f"Could not read PDF:\n{e}")
        return ""


# ── File Pickers ──────────────────────────────────────────────────────────────
def pick_resume_pdf():
    global pdf_resume_path
    path = fd.askopenfilename(
        title="Select Resume PDF",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
    )
    if path:
        pdf_resume_path = path
        # Show just the filename, not the full path
        resume_path_var.set(path.split("/")[-1])


def pick_jd_pdf():
    global pdf_jd_path
    path = fd.askopenfilename(
        title="Select Job Description PDF",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
    )
    if path:
        pdf_jd_path = path
        jd_path_var.set(f"📄 {path.split('/')[-1]}")
        # Clear the textbox since user chose a PDF instead
        jd_textbox.delete("1.0", "end")
        jd_textbox.insert("1.0", "[JD loaded from PDF — clear this to type manually]")
        jd_textbox.configure(text_color="gray")


# ── UI State Helpers ──────────────────────────────────────────────────────────
def set_status(text: str, color: str = "yellow"):
    result_label.configure(text=text, text_color=color)
    app.update_idletasks()


def show_result(text: str):
    global last_result_text
    last_result_text = text
    result_label.configure(text=text, text_color="#00FF00")
    copy_btn.pack(pady=(0, 10), padx=40)  # Show copy button after results arrive


def show_error(text: str):
    result_label.configure(text=f"⚠️  {text}", text_color="#FF5555")


def lock_ui(locked: bool):
    state = "disabled" if locked else "normal"
    calculate_button.configure(state=state)


# ── Core Processing (runs in background thread) ───────────────────────────────
def _process():
    try:
        # 1. Read resume
        app.after(0, lambda: set_status("📖  Reading resume... ⏳"))
        resume_text = read_pdf(pdf_resume_path)
        if not resume_text.strip():
            app.after(0, lambda: show_error("Could not extract text from the resume PDF."))
            return

        # 2. Get JD text — prefer PDF over textbox
        if pdf_jd_path:
            app.after(0, lambda: set_status("📖  Reading job description PDF... ⏳"))
            jd_text = read_pdf(pdf_jd_path)
        else:
            jd_text = jd_textbox.get("1.0", "end-1c").strip()

        if not jd_text or jd_text == "[JD loaded from PDF — clear this to type manually]":
            app.after(0, lambda: show_error("Please provide a job description (PDF or text)."))
            return

        # 3. Extract skills
        app.after(0, lambda: set_status("🧠  Extracting skills with AI..."))
        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)

        if not resume_skills:
            app.after(0, lambda: show_error("No recognisable skills found in the resume. Try a different PDF."))
            return
        if not jd_skills:
            app.after(0, lambda: show_error("No recognisable skills found in the job description."))
            return

        # 4. Calculate scores
        app.after(0, lambda: set_status("🧮  Calculating match score..."))
        result = get_match_score(resume_text, jd_text, resume_skills, jd_skills)

        # 5. Format and display
        final_score   = result["Final Score (%)"]
        exact_score   = result["Exact Skills Score (%)"]
        ai_score      = result["AI Context Score (%)"]
        matched       = result["Matched Skills"]
        missing       = result["Missing Skills"]

        matched_str       = ", ".join(matched)       if matched       else "None"
        missing_str       = ", ".join(missing)       if missing       else "None"
        resume_skills_str = ", ".join(resume_skills) if resume_skills else "None"
        jd_skills_str     = ", ".join(jd_skills)     if jd_skills     else "None"

        display = (
            f"🎯  Final Match Score : {final_score}%\n"
            f"     (Exact Skills: {exact_score}%  |  AI Context: {ai_score}%)\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📄  Resume Skills  ({len(resume_skills)}):  {resume_skills_str}\n\n"
            f"📋  JD Skills  ({len(jd_skills)}):  {jd_skills_str}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✅  Matched  ({len(matched)}):  {matched_str}\n\n"
            f"❌  Missing  ({len(missing)}):  {missing_str}"
        )

        app.after(0, lambda: show_result(display))

    except Exception as e:
        app.after(0, lambda: show_error(f"Unexpected error: {e}"))
    finally:
        app.after(0, lambda: lock_ui(False))


def calculate_match():
    """Validate inputs, then kick off processing in a background thread."""
    if not pdf_resume_path:
        show_error("Please upload a resume PDF first.")
        return

    jd_text = jd_textbox.get("1.0", "end-1c").strip()
    has_jd_text = bool(jd_text) and jd_text != "[JD loaded from PDF — clear this to type manually]"

    if not pdf_jd_path and not has_jd_text:
        show_error("Please upload a JD PDF or paste the job description text.")
        return

    lock_ui(True)
    copy_btn.pack_forget()  # Hide copy button while new result is loading
    thread = threading.Thread(target=_process, daemon=True)
    thread.start()


# ── Copy to Clipboard ─────────────────────────────────────────────────────────
def copy_to_clipboard():
    app.clipboard_clear()
    app.clipboard_append(last_result_text)
    copy_btn.configure(text="✅  Copied!")
    app.after(2000, lambda: copy_btn.configure(text="📋  Copy Results"))


# ── UI Layout ─────────────────────────────────────────────────────────────────

# Title
title_label = customtkinter.CTkLabel(
    app, text="🔍  AI Resume Matcher",
    font=customtkinter.CTkFont(family="Helvetica", size=22, weight="bold"),
)
title_label.pack(pady=(20, 4))

subtitle_label = customtkinter.CTkLabel(
    app, text="Upload your resume & job description to see how well you match.",
    font=customtkinter.CTkFont(size=12),
    text_color="gray",
)
subtitle_label.pack(pady=(0, 16))

# ── Two-column middle section ─────────────────────────────────────────────────
middle_frame = customtkinter.CTkFrame(app, fg_color="transparent")
middle_frame.pack(fill="both", expand=True, padx=20)

# Left column — Resume upload
left_frame = customtkinter.CTkFrame(middle_frame)
left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=0)

customtkinter.CTkLabel(
    left_frame, text="📄  Your Resume",
    font=customtkinter.CTkFont(size=14, weight="bold"),
).pack(pady=(16, 4))

customtkinter.CTkLabel(
    left_frame, text="PDF only",
    font=customtkinter.CTkFont(size=11), text_color="gray",
).pack()

resume_name_label = customtkinter.CTkLabel(
    left_frame,
    textvariable=resume_path_var,
    font=customtkinter.CTkFont(size=11),
    text_color="#5B9BD5",
    wraplength=300,
)
resume_name_label.pack(pady=(8, 4))

upload_resume_btn = customtkinter.CTkButton(
    left_frame, text="Upload Resume PDF",
    font=customtkinter.CTkFont(size=13),
    command=pick_resume_pdf,
)
upload_resume_btn.pack(padx=20, pady=(4, 16))

# Right column — Job Description
right_frame = customtkinter.CTkFrame(middle_frame)
right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=0)

customtkinter.CTkLabel(
    right_frame, text="📋  Job Description",
    font=customtkinter.CTkFont(size=14, weight="bold"),
).pack(pady=(16, 4))

jd_top_row = customtkinter.CTkFrame(right_frame, fg_color="transparent")
jd_top_row.pack(fill="x", padx=20)

customtkinter.CTkLabel(
    jd_top_row, text="Upload PDF  or  paste text below",
    font=customtkinter.CTkFont(size=11), text_color="gray",
).pack(side="left")

upload_jd_btn = customtkinter.CTkButton(
    jd_top_row, text="Upload JD PDF",
    font=customtkinter.CTkFont(size=11),
    width=120, height=28,
    command=pick_jd_pdf,
)
upload_jd_btn.pack(side="right")

jd_pdf_label = customtkinter.CTkLabel(
    right_frame,
    textvariable=jd_path_var,
    font=customtkinter.CTkFont(size=11),
    text_color="#5B9BD5",
    wraplength=300,
)
jd_pdf_label.pack(pady=(4, 4))

jd_textbox = customtkinter.CTkTextbox(
    right_frame, width=400, height=160,
    font=customtkinter.CTkFont(size=12),
)
jd_textbox.pack(padx=20, pady=(0, 16), fill="both", expand=True)
jd_textbox.insert("1.0", "Paste job description here...")

# ── Bottom section ────────────────────────────────────────────────────────────
bottom_frame = customtkinter.CTkFrame(app)
bottom_frame.pack(fill="x", padx=20, pady=(0, 16))

calculate_button = customtkinter.CTkButton(
    bottom_frame,
    text="Calculate Match Score",
    font=customtkinter.CTkFont(size=18, weight="bold"),
    height=50,
    command=calculate_match,
)
calculate_button.pack(pady=(16, 8), padx=40, fill="x")

# Copy button — hidden until results are shown
copy_btn = customtkinter.CTkButton(
    bottom_frame,
    text="📋  Copy Results",
    font=customtkinter.CTkFont(size=12),
    height=32,
    fg_color="gray30",
    hover_color="gray40",
    command=copy_to_clipboard,
)
# (packed dynamically after results appear)

# Scrollable result area
result_scroll = customtkinter.CTkScrollableFrame(
    bottom_frame, height=180, fg_color="transparent",
)
result_scroll.pack(pady=(4, 12), fill="both", expand=True)

result_label = customtkinter.CTkLabel(
    result_scroll,
    text="Upload your resume and job description to begin.",
    font=customtkinter.CTkFont(size=13),
    justify="left",
    wraplength=860,
    text_color="gray",
)
result_label.pack(pady=10, padx=10, anchor="w")

# ── Run ───────────────────────────────────────────────────────────────────────
app.mainloop()