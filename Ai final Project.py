import spacy
import json
from difflib import get_close_matches
from datetime import datetime

# spaCy English model
nlp = spacy.load("en_core_web_sm")

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as file:
        data: dict = json.load(file)
    return data

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.55)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]

def preprocess_input(user_input: str) -> str:
    # Updated NLP 
    doc = nlp(user_input)
    processed_input = " ".join([token.lemma_ for token in doc])
    return processed_input

def evaluate_chatbot(knowledge_base: dict):
    total_questions = len(knowledge_base["questions"])
    correct_answers = 0
    false_positives = 0
    false_negatives = 0

    for question_entry in knowledge_base["questions"]:
        user_question = question_entry["question"]
        expected_answer = question_entry["answer"]

        processed_input = preprocess_input(user_question)
        best_match = find_best_match(processed_input, [q["question"] for q in knowledge_base["questions"]])

        if best_match:
            bot_answer = get_answer_for_question(best_match, knowledge_base)
            if bot_answer == expected_answer:
                correct_answers += 1
            else:
                false_positives += 1
                false_negatives += 1
        else:
            false_negatives += 1

    accuracy = correct_answers / total_questions
    precision = correct_answers / (correct_answers + false_positives) if (correct_answers + false_positives) > 0 else 0
    recall = correct_answers / (correct_answers + false_negatives) if (correct_answers + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print(f"Accuracy: {accuracy:.2f}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1 Score: {f1_score:.2f}")

def chat_bot():
    knowledge_base: dict = load_knowledge_base('knowledge_base.json')

    while True:
        user_input: str = input('You: ')

        if user_input.lower() == 'quit':
            break
        
        processed_input = preprocess_input(user_input)

        best_match: str | None = find_best_match(processed_input, [q["question"] for q in knowledge_base["questions"]])

        if best_match:
            answer: str = get_answer_for_question(best_match, knowledge_base)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #updated time
            print(f'Bot ({current_time}): {answer}')
        else:
            print('Bot: Idk! can you teach me please?')
            new_answer: str = input('Type the answer or skip to skip: ')

            if new_answer.lower() != 'skip':
                knowledge_base["questions"].append({"question": processed_input, "answer": new_answer})
                save_knowledge_base('knowledge_base.json', knowledge_base)
                print('Bot: Thank you! I learned a new response!')

    evaluate_chatbot(knowledge_base)

if __name__ == '__main__':
    chat_bot()
