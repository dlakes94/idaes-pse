# !/usr/bin/env python
# coding: utf-8
"""

"""
import json
import pytest
import requests
import time

from idaes.ui.fsvis.app import App


@pytest.fixture()
def app():
    a = App()
    time.sleep(2)
    yield a
    App().stop()


def test_app(app):
    App()  # should not run twice
    j = {"model": {
           'id': "test", 
           'unit_models': {
               'M101': {'type': 'mixer', 'image': 'mixer.svg'}, 
               'H101': {'type': 'heater', 'image': 'heater_2.svg'}}, 
           'arcs': {
               's03': {'source': 'M101', 'dest': 'H101', 'label': "hello"}}}}  # payload
    jid = b"test"  # id: use un-encoded bytes
    url = f"http://{app.host}:{app.port}/fs"  # server url
    # put the JSON payload into the server
    resp = requests.post(url, json=j, params={'id': jid})
    assert resp.status_code == 200
    assert json.loads(resp.text) == j
    # get back the payload by its ID
    resp = requests.get(url, params={'id': jid})
    assert resp.json() == j
    # try an invalid ID
    # If an invalid ID is passed the code returns an empty model so the
    # page will still pop up but the jointjs graph will be empty
    resp = requests.get(url, params={'id': 'foo'})
    assert resp.status_code == 200


def test_app_stop(app):
    # stop the app
    app.stop()
    # setup
    j = {"test": 123}  # payload
    jid = b"abcdef"  # id: use un-encoded bytes
    url = f"http://{app.host}:{app.port}/fs"  # server url
    # should fail (server was stopped)
    pytest.raises((requests.ConnectionError, requests.exceptions.ReadTimeout),
                  requests.post, url, json=j, params={'id': jid}, timeout=1)
