import openai
import json
import numpy as np
import random
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def construct_message(agents, question, idx):
    if len(agents) == 0:
        return {"role": "user", "content": "Can you double check that your answer is correct? Please reiterate your answer, with your final answer as a single letter corresponding to the best choice (A, B, C, etc.)."}

    prefix_string = "These are the solutions to the question from other agents:"

    for agent in agents:
        agent_response = agent[idx]["content"]
        response = "\n\nOne agent's solution: ```{}```".format(agent_response)
        prefix_string += response

    prefix_string += f"""\n\nUsing the solutions from other agents as additional information, can you provide your answer to this reasoning question? \nThe question is: {question}. Your final answer should be a single letter (A, B, C, etc.) corresponding to the best choice at the end of your response."""
    return {"role": "user", "content": prefix_string}

def construct_assistant_message(completion):
    content = completion["choices"][0]["message"]["content"]
    return {"role": "assistant", "content": content}

def read_jsonl(path: str):
    with open(path) as fh:
        return [json.loads(line) for line in fh.readlines() if line]

if __name__ == "__main__":
    agents = 1
    rounds = 1
    random.seed(0)

    generated_description = {}

    questions = read_jsonl("modified_test.jsonl")
    random.shuffle(questions)

    for data in questions[:100]:
        question = data['question']
        answer = data['answer']

        agent_contexts = [[{"role": "user", "content": f"Can you solve this reasoning question? {question} Explain your reasoning. Your final answer should be a single letter (A, B, C, etc.) corresponding to the best choice at the end of your response."}] for agent in range(agents)]

        for round in range(rounds):
            for i, agent_context in enumerate(agent_contexts):
                if round != 0:
                    agent_contexts_other = agent_contexts[:i] + agent_contexts[i+1:]
                    message = construct_message(agent_contexts_other, question, 2 * round - 1)
                    agent_context.append(message)

                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-1106",
                    messages=agent_context,
                    n=1
                )

                assistant_message = construct_assistant_message(completion)
                agent_context.append(assistant_message)

        generated_description[question] = (agent_contexts, answer)

    json.dump(generated_description, open(f"commonsense_qa_{agents}_{rounds}.json", "w"))

    import pdb
    pdb.set_trace()
    print(answer)
    print(agent_context)