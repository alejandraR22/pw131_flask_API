def bad_request_if_none(obj):
    if obj is None or obj == "":
        response = {
            "message": "invalid request"
        }
        return response, 400