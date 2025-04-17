import json

# Load the original JSON file
with open("IntergratedReasoning.json", "r") as file:
    data = json.load(file)

# Prepare empty lists for each subtype
multi_source_reasoning = []
two_part_analysis = []
graphs_and_tables = []

# Loop through all questions in the file
for item in data.get("Allquestions", []):
    questions = item.get("questions", [item])  # Support both list-of-items and flat items
    for q in questions:
        subtype = q.get("subtype", "").strip()
        if subtype == "Multi Source Reasoning":
            multi_source_reasoning.append(q)
        elif subtype == "Two Part Analysis":
            two_part_analysis.append(q)
        elif subtype == "Graphs and Tables":
            graphs_and_tables.append(q)

# Save each list to its respective file
with open("IR_multi_source_reasoning.json", "w") as f:
    json.dump({"Questions": multi_source_reasoning}, f, indent=2, ensure_ascii=False)

with open("IR_two_part_analysis.json", "w") as f:
    json.dump({"Questions": two_part_analysis}, f, indent=2, ensure_ascii=False)

with open("IR_graphs_and_tables.json", "w") as f:
    json.dump({"Questions": graphs_and_tables}, f, indent=2, ensure_ascii=False)

print("Files created successfully:")
print("- IR_multi_source_reasoning.json")
print("- IR_two_part_analysis.json")
print("- IR_graphs_and_tables.json")
