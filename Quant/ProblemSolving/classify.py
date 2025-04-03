import json
import re

# Load the JSON file
with open("ProblemSolving.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Manual fix function
def clean_text(s):
    if not isinstance(s, str):
        return s
    # Replace Unicode-like escape strings with actual symbols
    s = s.replace("\\u221a", "√")  # √
    s = s.replace("\\u00b2", "²")  # squared
    s = s.replace("\\u00b3", "³")  # cubed
    s = s.replace("\\u00b0", "°")  # degree symbol
    # Remove LaTeX wrappers (optional)
    s = re.sub(r"\\\\\((.*?)\\\\\)", r"\1", s)
    return s

# Apply recursively to all string fields
def deep_clean(obj):
    if isinstance(obj, dict):
        return {k: deep_clean(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deep_clean(i) for i in obj]
    elif isinstance(obj, str):
        return clean_text(obj)
    else:
        return obj

# Grouping logic
mapping = {
    "Arithmetic": "quant_arithmetic",
    "Number Properties": "quant_numberproperties",
    "Statistics": "quant_statistics",
    "Word Problem": "quant_wordproblem",
    "Algebra": "quant_algebra"
}

grouped_questions = {filename: [] for filename in mapping.values()}

# Classify and clean
for q in data["Allquestions"]:
    subtype_type = q.get("subtype-type")
    file_key = mapping.get(subtype_type)
    if file_key:
        cleaned = deep_clean(q)
        grouped_questions[file_key].append(cleaned)

# Write cleaned files
for filename, questions in grouped_questions.items():
    with open(f"{filename}.json", "w", encoding="utf-8") as out:
        json.dump({"questions": questions}, out, indent=2, ensure_ascii=False)

print("✅ Unicode cleaned and files created!")
