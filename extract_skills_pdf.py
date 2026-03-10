import spacy
from spacy.matcher import PhraseMatcher
from skillNer.skill_extractor_class import SkillExtractor
from skillNer.general_params import SKILL_DB

# ── Model Loading ─────────────────────────────────────────────────────────────
nlp             = spacy.load("en_core_web_sm")
skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)

# ── Blocklist ─────────────────────────────────────────────────────────────────
# Common words and known false positives that SkillNER sometimes tags as skills

_BLOCKLIST = {
    # Articles / prepositions / conjunctions
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for",
    "of", "with", "by", "is", "it", "be", "as", "are", "was", "were",
    "do", "did", "has", "have", "had", "not", "no", "so", "if", "we",
    "he", "she", "i", "me", "my", "you", "us", "our", "their",
    # Noise from business / product JDs
    "act", "com", "reach", "trust", "space", "based", "they", "that",
    "this", "these", "those", "what", "who", "how", "when", "where",
    # Observed false positives
    "office space", "trust based", "selected projects",
    "applied sciences", "financial datum", "languages english",
    "internal documentation", "training and development",
}


def _is_noise(skill: str) -> bool:
    """
    Return True if this extracted token is noise, not a real skill.

    Blocks:
      - Single characters  ('e', 'b', 'r')
      - Pure digits        ('2', '10')
      - Blocklist entries  (stopwords + known false positives)
    """
    s = skill.strip().lower()
    if len(s) <= 1:
        return True
    if s.isdigit():
        return True
    if s in _BLOCKLIST:
        return True
    return False


def _remove_subsumed(skills: list) -> list:
    """
    Remove any skill that is just a leading fragment of a longer skill.

    Example: ['b', 'b1 german', 'machine', 'machine learning']
             → ['b1 german', 'machine learning']
    """
    skill_set = set(skills)
    return [
        s for s in skills
        if not any(
            other != s and other.startswith(s + " ")
            for other in skill_set
        )
    ]


# ── Main extraction function ──────────────────────────────────────────────────

def extract_skills(text: str) -> list:
    """
    Extract skills from any block of text using SkillNER.

    Returns a clean, sorted, deduplicated list of lowercase skill strings.
    """
    if not text or not text.strip():
        return []

    annotations = skill_extractor.annotate(text)

    raw_skills = []

    # Exact / full matches — e.g. "Python", "SQL", "Docker"
    for match in annotations.get("results", {}).get("full_matches", []):
        raw_skills.append(match["doc_node_value"].lower().strip())

    # Multi-word / ngram matches — e.g. "machine learning", "b1 german"
    for match in annotations.get("results", {}).get("ngram_scored", []):
        raw_skills.append(match["doc_node_value"].lower().strip())

    # Step 1 — Remove noise tokens
    filtered = [s for s in raw_skills if not _is_noise(s)]

    # Step 2 — Deduplicate
    deduplicated = list(set(filtered))

    # Step 3 — Remove leading fragments
    final = _remove_subsumed(deduplicated)

    return sorted(final)


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_text = """
    We are looking for a Data Analyst with experience in Python, SQL, and Tableau.
    Strong communication skills and analytical thinking required.
    Experience with machine learning pipelines, data visualisation, Docker,
    REST APIs, and cloud infrastructure. German language at B1 level is a plus.
    Familiarity with Git, CI/CD, and agile workflows is a bonus.
    """

    print("\nTest text:")
    print(test_text)
    skills = extract_skills(test_text)
    print("\nExtracted skills:")
    for s in skills:
        print(f"  • {s}")
    print(f"\nTotal: {len(skills)} skills found")