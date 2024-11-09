from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
from flask_session import Session
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # Keep this for session security
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# PostgreSQL URI from Render (replace this with your actual URI)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Use your PostgreSQL URI here
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable tracking modifications to save memory
db = SQLAlchemy(app)

# Define Response model to store user responses in PostgreSQL
class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_index = db.Column(db.Integer, nullable=False)
    question = db.Column(db.String(200), nullable=False)
    response = db.Column(db.String(10), nullable=False)
    comment = db.Column(db.String(500), nullable=True)

# Load stories from data.json
def load_stories():
    with open('data.json', 'r') as file:
        return json.load(file)

@app.route('/')
def index():
    if 'story_index' not in session:
        session['story_index'] = 0  # Start at the first story

    data = load_stories()  # Load stories from JSON file
    stories = data['stories']

    # Check if there are more stories
    if session['story_index'] < len(stories):
        story_data = stories[session['story_index']]
        return render_template('index.html', story=story_data['story'], questions=story_data['questions'], story_id=story_data['id'])
    else:
        return render_template('end.html')  # Render an end page when done

@app.route('/submit', methods=['POST'])
def submit():
    story_index = session['story_index']
    questions = load_stories()['stories'][story_index]['questions']

    # Collect user responses and store them in PostgreSQL
    for i, question in enumerate(questions):
        user_response = request.form.get(f'response_{i + 1}')
        user_comment = request.form.get(f'comment_{i + 1}', '')

        # Create a new Response object and store it in the database
        new_response = Response(
            story_index=story_index,
            question=question,
            response=user_response,
            comment=user_comment
        )
        db.session.add(new_response)  # Add the response to the session

    db.session.commit()  # Commit the transaction to save all responses to the database
    session['story_index'] += 1  # Move to the next story

    return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()  # Create the database tables if they don't exist already
    app.run(debug=True)
