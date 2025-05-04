import g4f
import json
import os
from dotenv import load_dotenv

load_dotenv()

models = ["gpt-4", "gpt-4o", "gpt-4o-mini", "llama-3.1-8b", "llama-3.1-70b", "llama-3.1-405b", "gemini-1.5-flash"]
prompt_styles = ["tree_of_thought"]
question_type = "problem_solving"

# Define ToT prompts for each subtype-type
def get_tot_prompt(q):
    subtype = q.get("subtype-type", "").lower()
    question = q["question"]
    options = json.dumps(q["options"], indent=2)

    if subtype == "algebra":
        reasoning = """
Thought 1: Identify the structure of the expression or equation.  
Thought 2: Explore integer/real value constraints or factorizations.  
Thought 3: Determine value ranges or count of solutions.  
Thought 4: Match your answer to the given options.
"""
    elif subtype == "number properties":
        reasoning = """
Thought 1: Understand constraints given for divisibility, remainders or factor counts.  
Thought 2: Use examples or algebra to validate multiple scenarios.  
Thought 3: Use elimination to rule out impossible choices.  
Thought 4: Select the most suitable answer.
"""
    elif subtype == "arithmetic":
        reasoning = """
Thought 1: Identify what operations are involved (sum, difference, etc.).  
Thought 2: Use formulas or logical reasoning to simplify.  
Thought 3: Estimate or directly calculate the result.  
Thought 4: Choose the best-fitting option.
"""
    elif subtype == "combinatorics":
        reasoning = """
Thought 1: Understand what's being arranged or chosen.  
Thought 2: Identify overcounts or duplicates (if any).  
Thought 3: Use permutations or combinations appropriately.  
Thought 4: Finalize your count and compare to options.
"""
    elif subtype == "word problem":
        reasoning = """
Thought 1: Parse the real-world scenario into a mathematical model.  
Thought 2: Translate given quantities and changes into equations.  
Thought 3: Calculate per-unit or total changes as needed.  
Thought 4: Solve and round off (if required), then match to options.
"""
    else:
        reasoning = """
Thought 1: Understand the core mathematical question.  
Thought 2: Consider all plausible solving paths.  
Thought 3: Choose the fastest or most reliable method.  
Thought 4: Solve and select the correct answer.
"""

    return f"""
You are a GMAT Quant expert.

Your task is to solve the following Problem Solving question using Tree of Thought reasoning.

--- QUESTION START ---
{question}
--- QUESTION END ---

Here are the options:
{options}

Follow this reasoning process:
{reasoning}

Format your response as:

Answer: [A/B/C/D/E]  
Explanation: [brief justification]
"""

def evaluate_with_g4f(prompt, model):
    return g4f.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

def evaluate_question(q, model, prompt_style):
    prompt = get_tot_prompt(q)
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
    with open("ProblemSolving.json", "r") as f:
        data = json.load(f)
    
    results = {
        "total_questions": len(data["questions"]),
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

            for q in data["questions"]:
                print(f"Evaluating Q{q['question_id']} ({q['subtype-type']}) with {model} - {ps}...")
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

    with open("GMAT_QUANT_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n✅ Results saved to GMAT_QUANT_results.json")

if __name__ == "__main__":
    main()
