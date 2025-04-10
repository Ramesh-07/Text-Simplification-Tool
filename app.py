import spacy
from textblob import TextBlob
import nltk
from nltk.corpus import wordnet
from flask import Flask, render_template, request, jsonify

nltk.download("wordnet")
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)

def get_simple_synonym(word):
    synonyms = wordnet.synsets(word)
    if synonyms:
        lemmas = [lemma.name() for synonym in synonyms for lemma in synonym.lemmas()]
        simple_synonyms = [lemma for lemma in set(lemmas) if "_" not in lemma and lemma.isalpha()]
        if simple_synonyms:
            return min(simple_synonyms, key=len)
    return word

def simplify_sentence(sentence, level="medium"):
    doc = nlp(sentence)
    simplified_words = []
    # Adjust length threshold based on level
    length_threshold = 4 if level == "easy" else 6 if level == "medium" else 8
    
    for token in doc:
        if token.is_stop or token.is_punct or token.is_digit:
            simplified_words.append(token.text)
        elif len(token.text) > length_threshold:
            simplified_words.append(get_simple_synonym(token.text))
        else:
            simplified_words.append(token.text)
    return " ".join(simplified_words)

def simplify_text(complex_text, level="medium"):
    # Split text into sentences and simplify each
    sentences = complex_text.split(". ")
    simplified_sentences = [simplify_sentence(sentence.strip(), level) for sentence in sentences]
    return ". ".join(simplified_sentences)

@app.route("/", methods=["GET"])
def quiz():
    return render_template("quiz.html")

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    if request.is_json:
        data = request.get_json()
        answers = data.get("answers", {})
        
        questions = [
            {"answer": "B"},  # Synonym for 'happy'
            {"answer": "C"},  # Plural of 'child'
            {"answer": "B"},  # Noun
            {"answer": "D"},  # Past tense of 'go'
            {"answer": "B"}   # Correct spelling
        ]
        
        score = sum(1 for i, q in enumerate(questions) if answers.get(str(i)) == q["answer"])
        level = "hard" if score == 5 else "medium" if 2 < score < 4 else "easy"
        
        return jsonify({"score": score, "level": level})
    return jsonify({"error": "Invalid request"})

@app.route("/simplify_page", methods=["GET"])
def simplify_page():
    score = request.args.get("score", 0, type=int)
    level = "hard" if score == 5 else "medium" if 2 < score < 4 else "easy"
    return render_template("index.html", initial_level=level)

@app.route("/simplify", methods=["POST"])
def simplify():
    if request.is_json:
        data = request.get_json()
        complex_text = data.get("text", "")
        level = data.get("level", "easy")
        
        if complex_text:
            simplified_text = simplify_text(complex_text, level)
            return jsonify({"result": simplified_text})
    
    return jsonify({"error": "Invalid request"})

if __name__ == "__main__":
    app.run(debug=True)