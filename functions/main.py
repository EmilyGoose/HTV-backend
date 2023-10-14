# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`
import json

from firebase_functions import https_fn
from firebase_admin import initialize_app, firestore
from firebase_functions import options
from google.cloud.firestore_v1 import FieldFilter, DocumentReference
from proto.datetime_helpers import DatetimeWithNanoseconds

options.set_global_options(max_instances=10)

app = initialize_app()


@https_fn.on_request()
def on_request_example(req: https_fn.Request) -> https_fn.Response:
    if req.content_type != 'application/json':
        resp = {"error": "Are you passing a JSON in the body? Use Postman, not the browser",
                "test":req.path}
        return https_fn.Response(response=json.dumps(resp), status=500, content_type='application/json')

    req_data = req.json
    if 'user_id' not in req_data:
        resp = {"error": "Please include a JSON in the body with `user_id` key set as `user_1`"}
        return https_fn.Response(response=json.dumps(resp), status=500, content_type='application/json')

    user_id = req_data['user_id']
    db = firestore.client()
    txn_collection = db.collection("transactions")
    query_ref = txn_collection.where(filter=FieldFilter("user",
                                                        "==",
                                                        DocumentReference('users', user_id, client=db)))
    query_results = query_ref.get()
    if len(query_results) == 0:
        resp = {"error": f"No transactions fround for user_id = `{user_id}`"}
        return https_fn.Response(response=json.dumps(resp), status=500, content_type='application/json')

    result = []

    for i in query_results:
        i = i.to_dict()
        date:DatetimeWithNanoseconds  = i['date']
        result.append({
            "company": i['company'],
            "cost": i['cost'],
            "date": str(date.isoformat()),
            "desc": i['desc'],
            "pay_mode": i['pay_mode'],
            "tx_type": i['tx_type']
        })
    return https_fn.Response(response=json.dumps({"resp": result}), content_type='application/json')
