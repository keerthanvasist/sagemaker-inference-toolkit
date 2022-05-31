import json
import subprocess
import sys

import requests
import time

import pytest as pytest


BASE_URL = "http://0.0.0.0:8080/"
PING_URL = BASE_URL + "ping"
INVOCATION_URL = BASE_URL + "models/{}/invoke"
MODELS_URL = BASE_URL + "models"

@pytest.fixture(scope="module", autouse=True)
def container():
    try:
        command = (
            "docker run --name sagemaker-inference-toolkit-test -p 8080:8080"
            " sagemaker-inference-toolkit-test:explain serve"
        )

        proc = subprocess.Popen(command.split(), stdout=sys.stdout, stderr=subprocess.STDOUT)

        attempts = 0
        while attempts < 10:
            time.sleep(3)
            try:
                requests.get(PING_URL)
                break
            except:  # noqa: E722
                attempts += 1
                pass
        yield proc.pid
    finally:
        subprocess.check_call("docker rm -f sagemaker-inference-toolkit-test".split())


def make_invocation_request(model_name, data, content_type="text/csv"):
    headers = {"Content-Type": content_type, "X-Amzn-SageMaker-Enable-Explanations": "`true`"}
    invocation_url = INVOCATION_URL.format(model_name)
    invocation_url = BASE_URL + "invocations?model_name={}".format(model_name)
    response = requests.post(invocation_url, data=data, headers=headers)
    print(response.headers)
    print(response.request.url)
    print(response.request.body)
    return response.status_code, response.content.decode("utf-8")


def test_ping():
    res = requests.get(PING_URL)
    assert res.status_code == 200


def make_load_model_request(data, content_type="application/json"):
    headers = {"Content-Type": content_type}
    response = requests.post(MODELS_URL, data=data, headers=headers)
    return response.status_code, json.loads(response.content.decode("utf-8"))


def make_list_model_request():
    response = requests.get(MODELS_URL)
    return response.status_code, json.loads(response.content.decode("utf-8"))


def test_invocation():
    code, body = make_list_model_request()
    assert code == 200
    assert body['models'] == [{'modelName': 'model', 'modelUrl': 'model'}]

    data = "data"
    code, predictions = make_invocation_request("model", data)
    print(predictions)
    assert code == 200




