import json
import sys
sys.path.append("../../")
import os
from django.http import JsonResponse, HttpRequest

from .ContextManager import ContextManager
from nft_generator.Collection import Collection
from nft_generator.Errors import NFTGError as E

context_manager = ContextManager()


def new(request: HttpRequest):
    global context_manager
    ret = dict()
    try:
        jsonobj = json.loads(request.body)
        context_manager.new_and_start_context(
            str(jsonobj["context_id"]),
            json.dumps(jsonobj["config"]),
            jsonobj["enable_render"],
            jsonobj["enable_metadata"],
            jsonobj["enable_excel"]
        )
    except Exception as e:
        ret["success"] = False
        ret["message"] = E.errmsg(e)
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
        ret["message"] = E.errmsg(e)
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


def from_excel(request: HttpRequest):
    try:
        jsonobj = json.loads(request.body)
        input_path = jsonobj["config"]["path"]
        output_path = jsonobj["config"]["output-path"]
        metadata_std = jsonobj["config"]["meta-std"]
        enable_delete = jsonobj["enable-delete"]
        enable_reorder = jsonobj["enable-reorder"]
        collection_name = jsonobj["config"]["collection-name"]

        count = Collection.generate_metadata_from_excel(input_path, output_path, collection_name, enable_delete, enable_reorder, metadata_std)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": E.errmsg(e),
            "data": ""
        })
    else:
        return JsonResponse({
            "success": True,
            "message": "",
            "data": {"count": count}
        })