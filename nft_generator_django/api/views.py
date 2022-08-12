import json
import sys
sys.path.append("../../")
import os
from django.http import JsonResponse, HttpRequest

from .ContextManager import ContextManager

context_manager = ContextManager()


def new(request: HttpRequest):
    global context_manager
    ret = dict()
    try:
        jsonobj = json.loads(request.body)
        context_manager.new_and_start_context(str(jsonobj["context_id"]), json.dumps(jsonobj["config"]), jsonobj["enable_render"], jsonobj["enable_metadata"])
    except Exception as e:
        ret["success"] = False
        ret["message"] = repr(e)
    else:
        ret["success"] = True
        ret["message"] = ""
    ret["data"] = ""
    return JsonResponse(ret)


def check(request: HttpRequest):
    global context_manager
    ret = dict()
    try:
        jsonobj = json.loads(request.body)
        success, executing, error_msg, progress, total = context_manager.get_progress(jsonobj["context_id"])
    except Exception as e:
        ret["success"] = False
        ret["message"] = repr(e)
        ret["data"] = ""
    else:
        ret["success"] = True
        ret["message"] = ""
        data = dict()
        data["success"] = success
        data["executing"] = executing
        data["error_msg"] = error_msg
        data["progress"] = progress
        data["total"] = total
        ret["data"] = data

    return JsonResponse(ret)


def ping(request: HttpRequest):
    return JsonResponse({
        "success": True,
        "message": "",
        "data": {"pid": os.getpid()}
    })
