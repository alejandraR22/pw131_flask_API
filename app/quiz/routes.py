from . import quiz_blueprint as quiz
from flask import request
from flask_jwt_extended import jwt_required, current_user
from ..models import Quiz, Question,User
from ..utils import bad_request_if_none

@quiz.post("/new")
@jwt_required()
def handle_create_quiz():
    body = request.json

    if body is None:
        response = {
            "message": "invalid request"
        }
        return response, 400
    
    title = body.get("title")
    if title is None or title == "":
        response = {
            "message": "invalid request"
        }
        return response, 400

    description = body.get("description")
    if description is None or description == "":
        response = {
            "message": "invalid request"
        }
        return response, 400

    existing_quiz = Quiz.query.filter_by(title=title).one_or_none()
    if existing_quiz is not None:
        response = {
            "message": "that title is already in use"
        }
        return response, 400

    quiz = Quiz(title=title, description=description, created_by=current_user.id)
    quiz.create()

    response = {
        "message": "successfully created quiz",
        "quiz": quiz.to_response()
    }
    return response, 201

@quiz.get("/all")
@jwt_required()
def handle_get_all_quizzes():
    quizzes = Quiz.query.all()
    response = {
        "message": "quizzes retrieved",
        "quizzes": [quiz.to_response() for quiz in quizzes]
    }
    return response, 200

@quiz.get("/mine")
@jwt_required()
def handle_get_my_quizzes():
    quizzes = Quiz.query.filter_by(created_by=current_user.id).all()
    response = {
        "message": "quizzes retrieved",
        "quizzes": [quiz.to_response() for quiz in quizzes]
    }
    return response, 200

@quiz.get("/<quiz_id>")
@jwt_required()
def handle_get_one_quiz(quiz_id):
    quiz = Quiz.query.filter_by(id=quiz_id).one_or_none()
    if quiz is None:
        response = {
            "message": "quiz does not exist"
        }
        return response, 404

    response = {
        "message": "quiz found",
        "quiz": quiz.to_response() 
    }
    return response, 200

@quiz.delete("/delete-quiz/<quiz_id>")
@jwt_required()
def handle_delete_quiz(quiz_id):
    quiz = Quiz.query.filter_by(id=quiz_id).one_or_none()
    if quiz is None:
        response = {
            "message": "quiz does not exist"
        }
        return response, 404

    if quiz.created_by != current_user.id:
        response = {
            "message":"you cant delete someone elses quiz"
        }
        return response, 401
    
    quiz.delete()

    response = {
        "message": f"quiz {quiz.id} deleted"
    }
    return response, 200

@quiz.post("/add-question/<quiz_id>")
@jwt_required()
def handle_add_question(quiz_id):
    body = request.json

    if body is None:
        response = {
            "message": "invalid request"
        }
        return response, 400

    quiz = Quiz.query.filter_by(id=quiz_id).one_or_none()
    if quiz is None:
        response = {
            "message": "quiz not found"
        }
        return response, 404
    
    if quiz.created_by != current_user.id:
        response = {
            "message":"you cant add questions someone elses quiz"
        }
        return response, 401
    
    prompt = body.get("prompt")
    opt_one = body.get("option_one")
    opt_two = body.get("option_two")
    opt_three = body.get("option_three")
    answer = body.get("answer")

    if not all([prompt, opt_one, opt_two, opt_three, answer]):
        response = {
            "message": "invalid request"
        }
        return response, 400
    
    question = Question(prompt=prompt, option_one=opt_one, option_two=opt_two, option_three=opt_three, answer=answer, quiz_id=quiz.id)
    question.create()

    quiz.questions.append(question)
    quiz.update()

    response = {
        "message":"question added",
        "quiz": quiz.to_response()
    }
    return response, 201

@quiz.delete("/delete-question/<question_id>")
@jwt_required()
def handle_delete_question(question_id):
    question = Question.query.filter_by(id=question_id).one_or_none()
    if question is None:
        response = {
            "message": "question does not exist"
        }
        return response, 404

    if question.quiz.author.id != current_user.id:
        response = {
            "message": "unauthorized"
        }
        return response, 401

    quiz_id = question.quiz.id 

    updated_questions = [q for q in question.quiz.questions if q.id != question_id]
    question.quiz.questions = updated_questions

    question.delete()

    quiz = Quiz.query.filter_by(id=quiz_id).first()

    response = {
        "message": "question deleted",
        "quiz": quiz.to_response()
    }
    return response, 200

@quiz.put("/update/quiz/<quiz_id>")
@jwt_required()
def handle_update_quiz(quiz_id):
    body = request.json

    quiz = Quiz.query.filter_by(id=quiz_id).one_or_none()
    if quiz is None:
        response = {
            "message": "not found"
        }
        return response, 404

    if quiz.created_by != current_user.id:
        response = {"message":"no sir/maam"}
        return response, 401
    

    quiz.title = body.get("title", quiz.title)
    quiz.description = body.get("description", quiz.description)
    
    quiz.update()

    response = {
        "message": "quiz updated",
        "quiz": quiz.to_response()
    }
    return response, 200

@quiz.put("/update/question/<question_id>")
@jwt_required()
def handle_update_question(question_id):
    body = request.json

    question = Question.query.filter_by(id=question_id).one_or_none()
    if question is None:
        response = {
            "message": "not found"
        }
        return response, 404
    
    if question.quiz.author.id != current_user.id:
        response = {"message":"no sir/maam"}
        return response, 401
    
    question.prompt = body.get("prompt", question.prompt)
    question.option_one = body.get("option_one", question.option_one)
    question.option_two = body.get("option_two", question.option_two)
    question.option_three = body.get("option_three", question.option_three)
    question.answer = body.get("answer", question.answer)

    question.update()

    response = {
        "message": "question updated",
        "question": question.to_response()
    }

    return response, 200