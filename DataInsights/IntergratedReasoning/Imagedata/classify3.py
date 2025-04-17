import json

# Load the original file
with open("IntergratedReasoningImg.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

# Create containers for each type
graphs = []
tables = []
multi_source = []
two_part = []

# Loop through all questions
for q in data.get("questions", []):
    subtype = q.get("subtype-subtype", "").strip()

    if subtype == "Graphs":
        graphs.append(q)
    elif subtype == "Tables":
        tables.append(q)
    elif subtype == "Multi Source Reasoning":
        multi_source.append(q)
    elif subtype == "Two Part Analysis":
        two_part.append(q)

# Save each category to its own file
with open("IR_GraphsIMG.json", "w", encoding="utf-8") as f:
    json.dump({"questions": graphs}, f, indent=2, ensure_ascii=False)

with open("IR_TablesIMG.json", "w", encoding="utf-8") as f:
    json.dump({"questions": tables}, f, indent=2, ensure_ascii=False)

with open("IR_Multi_Source_ReasoningIMG.json", "w", encoding="utf-8") as f:
    json.dump({"questions": multi_source}, f, indent=2, ensure_ascii=False)

with open("IR_Two_part_analysisIMG.json", "w", encoding="utf-8") as f:
    json.dump({"questions": two_part}, f, indent=2, ensure_ascii=False)

print("✅ JSON files created successfully:")
print("- IR_GraphsIMG.json")
print("- IR_TablesIMG.json")
print("- IR_Multi_Source_ReasoningIMG.json")
print("- IR_Two_part_analysisIMG.json")
