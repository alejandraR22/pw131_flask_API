from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from random import shuffle 

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String(64), primary_key = True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    username = db.Column(db.String(16), unique = True, nullable = False)
    password = db.Column(db.String(256), nullable = False)
    
    
    quizzes = db.relationship("Quiz", backref="author")


    def __init__(self, username, password):
        self.id = str(uuid4())
        self.username = username
        self.password = generate_password_hash(password)

    def compare_password(self, password):
        return check_password_hash(self.password, password)

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key == "password":
                setattr(self, key, generate_password_hash(value))
            else:
                setattr(self, key, value)
        db.session.commit()

    def to_response(self):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "username": self.username,
            "quizzes": [quiz.to_response() for quiz in self.quizzes]
        }
        
class Quiz(db.Model):
    id = db.Column(db.String(64), primary_key = True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    title = db.Column(db.String(64), unique = True, nullable = False)
    description = db.Column(db.Text)
    created_by = db.Column(db.String(64), db.ForeignKey("user.id"), nullable = False)

    questions = db.relationship("Question", backref="quiz")

    def __init__(self, title, description, created_by):
        self.id = str(uuid4())
        self.title = title
        self.description = description
        self.created_by = created_by
        
    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def to_response(self):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "title": self.title,
            "description": self.description,
            "created_by": self.author.username,
            "questions": [question.to_response() for question in self.questions]
        }


class Question(db.Model):
    id = db.Column(db.String(64), primary_key = True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    prompt = db.Column(db.Text, nullable = False)
    option_one = db.Column(db.String(255), nullable = False)
    option_two = db.Column(db.String(255), nullable = False)
    option_three = db.Column(db.String(255), nullable = False)
    answer = db.Column(db.String(255))
    quiz_id = db.Column(db.String(64), db.ForeignKey("quiz.id"))
    

    def __init__(self, prompt, option_one, option_two, option_three, answer, quiz_id):
        self.id = str(uuid4())
        self.prompt = prompt
        self.option_one = option_one
        self.option_two = option_two
        self.option_three = option_three
        self.answer = answer
        self.quiz_id = quiz_id

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def shuffle_options(self):
        options =[self.option_one, self.option_two, self.option_three, self.answer] 
        shuffle(options)
        return options

    def to_response(self):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "prompt": self.prompt,
            "options": self.shuffle_options(),
            "quiz_id": self.quiz_id
        }


class Choice(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    question_id = db.Column(db.String(64), db.ForeignKey('question.id'), nullable=False)

    def __init__(self, text, is_correct, question_id):
        self.id = str(uuid4())
        self.text = text
        self.is_correct = is_correct
        self.question_id = question_id

    def create(self):
        db.session.add(self)
        db.session.commit()

class UserQuizScore(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.String(64), db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, default=0)

    def __init__(self, user_id, quiz_id, score):
        self.id = str(uuid4())
        self.user_id = user_id
        self.quiz_id = quiz_id
        self.score = score

    def create(self):
        db.session.add(self)
        db.session.commit()
