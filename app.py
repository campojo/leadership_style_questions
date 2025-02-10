from flask import Flask, render_template, request, jsonify
import pandas as pd
import random
import requests
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

# GitHub Raw File URL
GITHUB_FILE_URL = "https://raw.githubusercontent.com/campojo/leadership_style_questions/main/Chris%20Leadership.xlsx"

def load_questions():
    response = requests.get(GITHUB_FILE_URL)
    if response.status_code != 200:
        return None
    df = pd.read_excel(BytesIO(response.content))
    styles = df['Style'].unique()
    question_dict = {}
    for style in styles:
        questions = df[df['Style'] == style]['Questions'].tolist()
        question_dict[style] = random.sample(questions, min(5, len(questions)))
    return question_dict

@app.route('/')
def home():
    question_dict = load_questions()
    if question_dict is None:
        return "Error loading questions from GitHub."
    questions = []
    for style, q_list in question_dict.items():
        for q in q_list:
            questions.append((style, q))
    random.shuffle(questions)
    return render_template('assessment.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    responses = request.form
    weight_mapping = {"1": -2.0, "2": -1.0, "3": 0.0, "4": 1.0, "5": 2.0}
    score_summary = {}
    for key, value in responses.items():
        style, _ = key.split('_', 1)
        if style not in score_summary:
            score_summary[style] = 0
        score_summary[style] += weight_mapping[value]
    
    # Generate Bar Chart
    plt.figure(figsize=(10, 6))
    plt.bar(score_summary.keys(), score_summary.values(), color='blue')
    plt.xlabel("Leadership Style")
    plt.ylabel("Score")
    plt.title("Assessment Summary by Leadership Style")
    plt.xticks(rotation=45)
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode()
    
    return render_template('results.html', scores=score_summary, chart=img_b64)

if __name__ == '__main__':
    app.run(debug=True)
