from json import dumps

from firebase_admin import firestore
from firebase_functions import https_fn
from google.cloud.firestore_v1 import DocumentReference, FieldFilter


def retrieve_user_data(req: https_fn.Request) -> https_fn.Response:
    # Return error if there is no JSON value passed in the request body
    if req.content_type != 'application/json':
        resp = {"error": "Are you passing a JSON in the body? Use Postman, not the browser",
                "test":req.path}
        return https_fn.Response(response=dumps(resp), status=500, content_type='application/json')

    req_data = req.json

    # Return error if the JSON body does not have necessary key -> user_id
    if 'user_id' not in req_data:
        resp = {"error": "Please include a JSON in the body with `user_id` key set as `user_1`"}
        return https_fn.Response(response=dumps(resp), status=500, content_type='application/json')

    # Query Firestore based on user ID
    user_id = req_data['user_id']
    db = firestore.client()
    txn_collection = db.collection("transactions")
    query_ref = txn_collection.where(filter=FieldFilter("user",
                                                        "==",
                                                        DocumentReference('users', user_id, client=db)))
    query_results = query_ref.get()

    result = []

    # Iterate and format result of the Firestore query
    for i in query_results:
        i = i.to_dict()
        result.append({
            "company": i['company'],
            "cost": i['cost'],
            "date": str(i['date'].isoformat()),
            "desc": i['desc'],
            "pay_mode": i['pay_mode'],
            "tx_type": i['tx_type']
        })
    return https_fn.Response(response=dumps({"trx": result}), content_type='application/json')