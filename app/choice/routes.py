from flask import request
from flask_jwt_extended import jwt_required, current_user
from ..models import Choice
from ..utils import bad_request_if_none
from . import choice_blueprint as choice

@choice.post("/new")
@jwt_required()
def handle_create_choice():
    body = request.json

    if body is None:
        response = {
            "message": "Invalid request"
        }
        return response, 400

    text = body.get("text")
    is_correct = body.get("is_correct")

    if not all([text, is_correct is not None]):
        response = {
            "message": "Invalid request"
        }
        return response, 400

    choice = Choice(text=text, is_correct=is_correct, question_id=question_id)
    choice.create()

    response = {
        "message": "Choice created",
        "choice": choice.to_response()
    }
    return response, 201

@choice.get("/<choice_id>")
@jwt_required()
def handle_get_choice(choice_id):
    choice = Choice.query.filter_by(id=choice_id).one_or_none()
    if choice is None:
        response = {
            "message": "Choice does not exist"
        }
        return response, 404

    response = {
        "message": "Choice found",
        "choice": choice.to_response()
    }
    return response, 200

@choice.put("/update/<choice_id>")
@jwt_required()
def handle_update_choice(choice_id):
    body = request.json

    choice = Choice.query.filter_by(id=choice_id).one_or_none()
    if choice is None:
        response = {
            "message": "Choice not found"
        }
        return response, 404


    text = body.get("text")
    is_correct = body.get("is_correct")

    if text is not None:
        choice.text = text
    if is_correct is not None:
        choice.is_correct = is_correct

    choice.update()

    response = {
        "message": "Choice updated",
        "choice": choice.to_response()
    }
    return response, 200

@choice.delete("/delete/<choice_id>")
@jwt_required()
def handle_delete_choice(choice_id):
    choice = Choice.query.filter_by(id=choice_id).one_or_none()
    if choice is None:
        response = {
            "message": "Choice does not exist"
        }
        return response, 404

    choice.delete()

    response = {
        "message": f"Choice {choice.id} deleted"
    }
    return response, 200
