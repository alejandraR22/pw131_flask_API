from flask import request, json
from flask_jwt_extended import jwt_required
from ..models import UserQuizScore
from . import quizscore_blueprint as quizscore_blueprint

@quizscore_blueprint.route("/create", methods=["POST"])
@jwt_required
def create_quizscore():
    data = request.get_json()
    user_id = data.get("user_id")
    quiz_id = data.get("quiz_id")
    score = data.get("score")

    if not all([user_id, quiz_id, score]):
        return json.dumps({"message": "user_id, quiz_id, and score are required"}), 400

    quizscore = UserQuizScore(user_id=user_id, quiz_id=quiz_id, score=score)
    quizscore.create()

    return json.dumps({"message": "Quiz score created", "quizscore_id": quizscore.id}), 201

