import g4f
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Constants
models = ["gpt-4", "gpt-4o", "gpt-4o-mini", "llama-3.1-8b", "llama-3.1-70b", "llama-3.1-405b", "gemini-1.5-flash"]
prompt_styles = ["tree_of_thought"]
question_type = "reading_comprehension"

def tree_of_thought_prompt(question_data, passage):
    question = question_data["question"]
    options = question_data["options"]

    prompt = f"""
You are a GMAT Verbal Reasoning expert.

Your task is to evaluate a Reading Comprehension question using Tree of Thought reasoning.
Carefully read the passage and analyze the question using logical reasoning.

--- PASSAGE START ---
{passage}
--- PASSAGE END ---

--- QUESTION START ---
{question}
--- QUESTION END ---

Here are the options:
{json.dumps(options, indent=2)}

Follow this reasoning process:

Thought 1: What is the main topic of the passage?  
Thought 2: What part(s) of the passage are relevant to this specific question?  
Thought 3: What are the plausible answer choices based on the relevant lines?  
Thought 4: Rule out incorrect options.  
Thought 5: Choose the best option.

Format your response as:

Answer: [A/B/C/D/E]  
Explanation: [brief justification]
"""
    return prompt

def evaluate_with_g4f(prompt, model):
    return g4f.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

def evaluate_question(q, passage, model, prompt_style):
    prompt = tree_of_thought_prompt(q, passage)
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
    with open("ReadingComprehension.json", "r") as f:
        data = json.load(f)

    all_questions = []
    for p in data["questions"]:
        passage = p["passage"]
        for q in p["questions"]:
            q["passage_text"] = passage
            all_questions.append(q)

    results = {
        "total_questions": len(all_questions),
        "questions": [],
        "accuracy": {question_type: {}},
        "overall_accuracy": {}
    }

    for model in models:
        results["accuracy"][question_type][model] = {}
        results["overall_accuracy"][model] = {}
        for ps in prompt_styles:
            correct = 0
            total = 0
            results["accuracy"][question_type][model][ps] = {"correct": 0, "total": 0}

            for q in all_questions:
                print(f"Evaluating Q{q['question_id']} with {model} - {ps}...")
                result = evaluate_question(q, q["passage_text"], model, ps)
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

    with open("GMAT_RC_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n✅ Results saved to GMAT_RC_results.json")

if __name__ == "__main__":
    main()
