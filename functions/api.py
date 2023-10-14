from collections import Counter
from json import dumps

from firebase_admin import firestore
from firebase_functions import https_fn
from google.cloud.firestore_v1 import DocumentReference, FieldFilter, CollectionReference
from google.cloud.firestore_v1.base_query import BaseQuery


# Query Firestore based on the request_json
def generate_query_ref(req_json: dict) -> BaseQuery:
    # {"user_id":"user_1", "filter" : {"pay_mode":"Paypal/credit", "tx_type":"travel/food/"}}
    user_id = req_json['user_id']

    filters = req_json['filter']  # not sure if this sticks it into another dictionary or just dumps as a string
    company = ""
    transaction_type = ""

    # go ahead and dig into the filters passed
    if filters != "":
        try:
            company = req_json['filter']['company']
        except:
            print("error")

        try:
            transaction_type = req_json['filter']['tx_type']
        except:

            print("error")

    db = firestore.client()
    txn_collection: CollectionReference = db.collection("transactions")

    # Default query
    query_ref = txn_collection.where(filter=FieldFilter("user", "==",
                                                        DocumentReference('users', user_id, client=db)))

    if company != "":
        # If company included in filter
        query_ref = query_ref.where(filter=FieldFilter("company", "==", company))

    if transaction_type != "":
        # If company included in filter
        query_ref = query_ref.where(filter=FieldFilter("tx_type", "==", transaction_type))

    return query_ref


def validate_request(req: https_fn.Request) -> dict:
    # Return error if there is no JSON value passed in the request body
    if req.content_type != 'application/json':
        raise Exception("Are you passing a JSON in the body? Use Postman, not the browser")
        # resp = {"error": }
        # return https_fn.Response(response=dumps(resp), status=500, content_type='application/json')

    req_data = req.json

    # Return error if the JSON body does not have necessary key -> user_id
    if 'user_id' not in req_data:
        # resp = {"error": "Please include a JSON in the body with `user_id` key set as `user_1`"}
        raise Exception("Please include a JSON in the body with `user_id` key set as `user_1`")
        # return https_fn.Response(response=dumps(resp), status=500, content_type='application/json')

    return req_data


def retrieve_categories(req: https_fn.Request) -> https_fn.Response:
    req_data = validate_request(req)

    query_ref = generate_query_ref(req_data)
    query_results = query_ref.get()  # ok so this is a list of arrays

    # foreach unique item in the dictionary, count
    counts = dict()
    for i in query_results:  # ok wait, list of dictionaries? or list of arrays so access each row by query_results[i], then access key with .get(key)
        i = i.to_dict()
        category = i.get("tx_type")
        # if its arrays this will need to be (query_results[i])[5]
        if (counts[category] != ""):
            counts[category] = 1
        else:
            counts[category] = counts.get('category') + 1

    # using counter obj type?
    # resultDict = Counter(query_results)

    # i think this is going to return the category name and the counts ??
    return https_fn.Response(response=dumps({"categories": counts}), content_type='application/json')


def evaluate_user_response(req: https_fn.Request) -> https_fn.Response:
    req_data = validate_request(req)

    # this is already going to be the filtered list based on categories so literally just sum it
    query_ref = generate_query_ref(req_data)
    query_results = query_ref.get()
    sum = 0

    for i in query_results:  # ok wait, list of dictionaries? or list of arrays so access each row by query_results[i], then access key with .get(key)
        i = i.to_dict()
        sum = sum + i.get("cost")
        # if its arrays this will need to be (query_results[i])[5]

    resp = {"sum": sum}

    return https_fn.Response(response=dumps(resp), content_type='application/json')


def retrieve_user_data(req: https_fn.Request) -> https_fn.Response:
    # Return error if there is no JSON value passed in the request body
    if req.content_type != 'application/json':
        resp = {"error": "Are you passing a JSON in the body? Use Postman, not the browser"}
        return https_fn.Response(response=dumps(resp), status=500, content_type='application/json')

    req_data = req.json

    # Return error if the JSON body does not have necessary key -> user_id
    if 'user_id' not in req_data:
        resp = {"error": "Please include a JSON in the body with `user_id` key set as `user_1`"}
        return https_fn.Response(response=dumps(resp), status=500, content_type='application/json')

    query_ref = generate_query_ref(req_data)
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
