import json
import numpy as np
import re


def parse_answer(input_str):
    """
    Extracts the answer letter (A, B, C, etc.) from the response.
    """
    pattern = r"\b[A-E]\b"  # Looks for standalone letters A-E
    matches = re.findall(pattern, input_str)
    if matches:
        return matches[-1]
    return None


def compute_accuracy(gt, pred_solutions):
    """
    Compares the predicted solution with the ground truth answer key.
    """
    if type(pred_solutions) == list:
        # Collect all parsed answers from agents' final responses
        pred_answers = [parse_answer(solution) for solution in pred_solutions]
        pred_answers = [answer for answer in pred_answers if answer is not None]
        pred_answer = most_frequent(pred_answers) if pred_answers else None
    else:
        pred_answer = parse_answer(pred_solutions)

    # Return accuracy as 1 if correct, otherwise 0
    return 1 if pred_answer == gt else 0


def most_frequent(answers_list):
    """
    Finds the most frequent answer in the list.
    """
    if not answers_list:
        return None
    return max(set(answers_list), key=answers_list.count)


def load_ground_truth(test_file):
    """
    Loads the ground truth answers from modified_test.jsonl.
    """
    ground_truth = {}
    with open(test_file, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            question_text = entry["question"]
            answer_key = entry["answer"]
            ground_truth[question_text] = answer_key
    return ground_truth


if __name__ == "__main__":
    input_filename = "commonsense_qa_1_1.json"
    test_file = "modified_test.jsonl"  # Ground truth data with question, original_question, and answer

    # Load ground truth answers
    ground_truth = load_ground_truth(test_file)

    # Load the generated multiagent responses
    response_dict = json.load(open(input_filename, "r"))

    accuracies = []

    for question_text, (responses, _) in response_dict.items():
        # Get the ground truth answer key by matching the `question` field
        gt_answer = ground_truth.get(question_text, None)
        if gt_answer is None:
            print(f"Ground truth answer missing for question: {question_text}")
            continue

        # Collect final responses from all agents
        pred_solutions = [response[-1]['content'] for response in responses]

        # Compute accuracy for the question
        accurate = compute_accuracy(gt_answer, pred_solutions)

        if accurate is not None:
            accuracies.append(float(accurate))
        else:
            print(f"Prediction missing for question: {question_text}")

    # Calculate mean accuracy, standard deviation, and standard error
    mean_accuracy = np.mean(accuracies)
    std_deviation = np.std(accuracies)  # Standard deviation
    std_error = std_deviation / (len(accuracies) ** 0.5)  # Standard error

    # Print and write results to a file
    print("Mean Accuracy:", mean_accuracy)
    print("Standard Deviation:", std_deviation)
    print("Standard Error:", std_error)

    with open("eval_" + input_filename.replace(".json", ".txt"), "w") as f:
        f.write(f"Mean Accuracy: {mean_accuracy}\n")
        f.write(f"Standard Deviation: {std_deviation}\n")
        f.write(f"Standard Error: {std_error}\n")
