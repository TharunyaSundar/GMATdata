import g4f
import json
import os
from dotenv import load_dotenv

load_dotenv()

models = ["gpt-4", "gpt-4o", "gpt-4o-mini", "llama-3.1-8b", "llama-3.1-70b", "llama-3.1-405b", "gemini-1.5-flash"]
prompt_style = ["tree_of_thought"]
section = "Data Insight"
subtypes = ["Graphs and Tables", "Multi Source Reasoning", "Two Part Analysis"]

def tree_of_thought_prompt(q):
    subtype = q.get("subtype", "").lower()

    base = f"""
You are a GMAT Integrated Reasoning expert.

Your task is to answer a question from the subtype: {subtype.title()}.
Use Tree of Thought reasoning to carefully analyze the question and options.

--- QUESTION START ---
{q['question']}
--- QUESTION END ---
"""

    if "table" in q:
        base += f"\n--- TABLE DATA ---\n{json.dumps(q['table'], indent=2)}\n"

    if "statements" in q:
        base += f"\n--- STATEMENTS ---\n" + "\n".join([f"{i+1}. {s}" for i, s in enumerate(q["statements"])])

    if "options" in q:
        base += f"\n--- OPTIONS ---\n{json.dumps(q['options'], indent=2)}"

    if "correct_answer" in q and isinstance(q["correct_answer"], dict):
        base += "\nFormat your answer in this structure:\nAnswer: { field_name_1: value_1, field_name_2: value_2 }\n"
    elif "correct_answer" in q and isinstance(q["correct_answer"], list):
        base += "\nFormat your answer as a list:\nAnswer: [val1, val2, val3...]\n"
    else:
        base += "\nFormat your answer as:\nAnswer: [final choice]\n"

    base += "\nExplain your reasoning step-by-step before selecting your final answer.\n"
    return base

def evaluate_with_g4f(prompt, model):
    response = g4f.ChatCompletion.create(
        model=g4f.models.default,
        messages=[{"role": "user", "content": prompt}]
    )
    return response

def extract_predicted_answer(response):
    for line in response.splitlines():
        if line.strip().lower().startswith("answer:"):
            return line.split(":", 1)[1].strip()
    return ""

def evaluate_question(q, model, prompt_style):
    prompt = tree_of_thought_prompt(q)
    response = evaluate_with_g4f(prompt, model=model)

    predicted = extract_predicted_answer(response)

    correct_answer = q.get("correct_answer", None)
    if correct_answer is None:
        print(f"⚠️  Q{q['question_id']} is missing 'correct_answer'. Marking as incorrect.")
        correct = False
    else:
        correct = str(predicted).strip().upper() == str(correct_answer).strip().upper()

    return {
        "question_id": q["question_id"],
        "model": model,
        "subtype": q.get("subtype", ""),
        "prompt_style": prompt_style,
        "predicted": predicted,
        "correct_answer": correct_answer,
        "is_correct": correct,
        "explanation": response
    }

def main():
    with open("IntegratedReasoning.json", "r") as f:
        data = json.load(f)

    questions = [q for q in data["questions"] if q.get("section", "").lower() == "data insight"]

    results = {
        "total_questions": len(questions),
        "questions": [],
        "accuracy": {},
        "overall_accuracy": {}
    }

    for model in models:
        results["accuracy"][model] = {}
        results["overall_accuracy"][model] = {}

        for ps in prompt_style:
            correct = 0
            total = 0
            results["accuracy"][model][ps] = {}

            for st in subtypes:
                subtype_questions = [q for q in questions if q.get("subtype", "").lower() == st.lower()]
                results["accuracy"][model][ps][st] = {"correct": 0, "total": 0}

                for q in subtype_questions:
                    print(f"Evaluating Q{q['question_id']} ({st}) with {model} - {ps}...")
                    result = evaluate_question(q, model, ps)
                    results["questions"].append(result)

                    if result["is_correct"]:
                        correct += 1
                        results["accuracy"][model][ps][st]["correct"] += 1
                    results["accuracy"][model][ps][st]["total"] += 1
                    total += 1

            results["overall_accuracy"][model][ps] = {
                "correct": correct,
                "total": total,
                "accuracy": round((correct / total) * 100, 2) if total else 0
            }

    with open("GMAT_IR_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n IR Evaluation complete! Results saved to GMAT_IR_results.json")

if __name__ == "__main__":
    main()
