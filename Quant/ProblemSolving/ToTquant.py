import g4f
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Constants
models = [
    "gpt-4", "gpt-4o", "gpt-4o-mini",
    "llama-3.1-8b", "llama-3.1-70b", "llama-3.1-405b",
    "gemini-1.5-flash"
]
prompt_styles = ["tree_of_thought"]
question_type = "algebra"


def tree_of_thought_prompt(question_data):
    question = question_data["question"]
    options = question_data["options"]

    prompt = f"""
You are a GMAT Quant expert.

Your task is to evaluate a Problem Solving (Algebra) question using Tree of Thought reasoning.
Analyze the problem step by step, eliminate incorrect choices, and select the best answer.

--- QUESTION START ---
{question}
--- QUESTION END ---

Here are the options:
{json.dumps(options, indent=2)}

Follow this reasoning process:

Thought 1: What kind of algebraic problem is this?
Thought 2: What equation(s) or concept(s) can be applied?
Thought 3: Perform the necessary calculations step-by-step.
Thought 4: Eliminate options that don’t make sense.
Thought 5: Choose the best answer.

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


def evaluate_question(q, model, prompt_style):
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


def save_results_by_model(model_name, results_dict, section_name="Quant_Algebra", save_dir="quant_results"):
    os.makedirs(save_dir, exist_ok=True)
    filename = f"GMAT_{section_name}_Results_{model_name.replace('.', '_').replace('-', '_')}.json"
    filepath = os.path.join(save_dir, filename)

    with open(filepath, "w") as f:
        json.dump(results_dict, f, indent=2)
    print(f"\n✅ Saved results for {model_name} to {filepath}")


def main():
    with open("quant_algebra.json", "r") as f:
        data = json.load(f)

    questions = data["questions"]

    for model in models:
        model_results = {
            "total_questions": len(questions),
            "questions": [],
            "accuracy": {question_type: {model: {}}},
            "overall_accuracy": {model: {}}
        }

        for ps in prompt_styles:
            correct = 0
            total = 0
            for q in questions:
                print(f"Evaluating Q{q['question_id']} with {model} - {ps}...")
                result = evaluate_question(q, model=model, prompt_style=ps)
                model_results["questions"].append(result)
                if result["is_correct"]:
                    correct += 1
                total += 1

            model_results["accuracy"][question_type][model][ps] = {
                "correct": correct,
                "total": total
            }
            model_results["overall_accuracy"][model][ps] = {
                "correct": correct,
                "total": total,
                "accuracy": round((correct / total) * 100, 2) if total else 0
            }

        save_results_by_model(model, model_results)


if __name__ == "__main__":
    main()
