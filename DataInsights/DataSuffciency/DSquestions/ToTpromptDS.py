import g4f
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Constants
models = ["gpt-4", "gpt-4o", "gpt-4o-mini",
    "llama-3.1-8b", "llama-3.1-70b", "llama-3.1-405b",
    "gemini-1.5-flash",]
prompt_style = ["tree_of_thought"]
question_type = "data_sufficiency"

def tree_of_thought_prompt(question_data):
    question = question_data["question"]


    prompt = f"""
You are a GMAT expert.

Your task is to evaluate a GMAT Data Sufficiency question using Tree of Thought reasoning.
Carefully analyze the statements (1) and (2) and determine whether each is sufficient alone or in combination to answer the question.

--- QUESTION START ---
{question}
--- QUESTION END ---

Here are the standard Data Sufficiency answer options you must choose from:

A: Statement (1) ALONE is sufficient, but statement (2) ALONE is not sufficient to answer the question asked.  
B: Statement (2) ALONE is sufficient, but statement (1) ALONE is not sufficient to answer the question asked.  
C: BOTH statements (1) and (2) TOGETHER are sufficient to answer the question asked, but NEITHER statement ALONE is sufficient to answer the question asked.  
D: EACH statement ALONE is sufficient to answer the question asked.  
E: Statements (1) and (2) TOGETHER are NOT sufficient to answer the question asked, and additional data specific to the problem are needed.

Follow this reasoning process:

Thought 1: What is the question asking?  
Thought 2: Analyze Statement (1) alone. Is it sufficient?  
Thought 3: Analyze Statement (2) alone. Is it sufficient?  
Thought 4: Analyze them together. Are they sufficient jointly?  
Thought 5: Choose the correct answer from options A to E.

Format your response as:

Answer: [A/B/C/D/E]  
Explanation: [brief justification]
"""
    return prompt

def evaluate_with_g4f(prompt,model):
    response = g4f.ChatCompletion.create(
        model=g4f.models.default,
        messages=[{"role": "user", "content": prompt}]
    )
    return response


def evaluate_question(q, model, prompt_style="tree_of_thought"):
    prompt = tree_of_thought_prompt(q)
    response = evaluate_with_g4f(prompt, model=model)

    answer_line = next((line for line in response.splitlines() if line.strip().startswith("Answer:")), "")
    predicted_answer = answer_line.replace("Answer:", "").strip().upper()
    correct = predicted_answer == q["correct_answer"].strip().upper()

    return {
        "question_id": q["question_id"],
        "model": model,
        "prompt_style": prompt_style,
        "predicted": predicted_answer,
        "correct_answer": q["correct_answer"],
        "is_correct": correct,
        "explanation": response
    }


def main():
    with open("DataSufficiency.json", "r") as f:
        data = json.load(f)

    questions = [
    q for q in data["questions"]
    if q.get("section", "").lower() == "data insights" and q.get("subtype", "").lower() == "data sufficiency"
]


    results = {
        "total_questions": len(questions),
        "questions": [],
        "accuracy": {question_type: {}},
        "overall_accuracy": {}
    }

    for model in models:
        results["accuracy"][question_type][model] = {}
        results["overall_accuracy"][model] = {}
        for ps in prompt_style:
            correct = 0
            total = 0
            results["accuracy"][question_type][model][ps] = {"correct": 0, "total": 0}

            for q in questions:
                print(f"Evaluating Q{q['question_id']} with {model} - {ps}...")
                result = evaluate_question(q, model=model, prompt_style=ps)
                results["questions"].append(result)

                if result["is_correct"]:
                    correct += 1
                total += 1

            results["accuracy"][question_type][model][ps]["correct"] = correct
            results["accuracy"][question_type][model][ps]["total"] = total
            results["overall_accuracy"][model][ps] = {
                "correct": correct,
                "total": total,
                "accuracy": round((correct / total) * 100, 2) if total else 0
            }

    with open("GMAT_DS_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n✅ Results saved to GMAT_DS_results.json")

if __name__ == "__main__":
    main()
