# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`
import json

from firebase_functions import https_fn
from firebase_admin import initialize_app, firestore
from firebase_functions import options


from api import retrieve_user_data

options.set_global_options(max_instances=10)

app = initialize_app()


@https_fn.on_request()
def on_request_example(req: https_fn.Request) -> https_fn.Response:
    if req.path == '/transactions':
        return retrieve_user_data(req)
