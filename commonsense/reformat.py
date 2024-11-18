import json

# Input and output file paths
input_file = "test.jsonl"
output_file = "modified_test.jsonl"

# Function to reformat each question
def reformat_question(entry):
    # Extract relevant data
    question_id = entry['id']
    original_question_text = entry['question']['stem']
    choices = entry['question']['choices']
    answer = entry['answerKey']

    # Build the choices text
    choices_text = ", ".join([f"{choice['label']}: {choice['text']}" for choice in choices])

    # Create the reformatted question string
    question_reformatted = f"{original_question_text}. Is it {choices_text}?"

    # Return the new structure with the question ID and original question
    return {
        "question": question_reformatted,
        "answer": answer
    }

# Read, transform, and write to new file
with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        entry = json.loads(line.strip())
        modified_entry = reformat_question(entry)
        json.dump(modified_entry, outfile)
        outfile.write("\n")

print(f"Modified data saved to {output_file}")
