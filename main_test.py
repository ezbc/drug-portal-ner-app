# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import json
import os

import pytest

import main

@pytest.fixture
def client(monkeypatch):
    monkeypatch.chdir(os.path.dirname(main.__file__))
    main.app.testing = True
    client = main.app.test_client()
    return client

class Request:

    def __init__(self, method, form):
        self.method = method
        self.form = form

def test__get_entities_from_text_expecting_none():

    request = Request('GET', {})

    entities, text = main._get_entities_from_text(request)

    assert text == main.PLACEHOLDER_TEXT

    assert entities == None


def test__annotate_text_expecting_entities():

    text = '''Beta-adrenergic agonist medicines may produce significant hypokalemia in some patients,'''

    annotations = [{'text': 'may', 'start_char': 34, 'end_char': 37, 'label': 'Factor'}, {'text': 'significant', 'start_char': 46, 'end_char': 57, 'label': 'Severity'}, {'text': 'hypokalemia', 'start_char': 58, 'end_char': 69, 'label': 'AdverseReaction'}]


    annotated_text_actual = main._annotate_text(annotations, text)


    annotated_text_expected = [{'text': 'Beta-adrenergic agonist medicines ', 'label': None, 'class': None}, {'text': 'may', 'label': 'Factor', 'class': 'factor'}, {'text': ' produce ', 'label': None, 'class': None}, {'text': 'significant', 'label': 'Severity', 'class': 'severity'}, {'text': ' ', 'label': None, 'class': None}, {'text': 'hypokalemia', 'label': 'AdverseReaction', 'class': 'adversereaction'}, {'text': ' in some patients,', 'label': None, 'class': None}]

    assert annotated_text_actual == annotated_text_expected

def test__annotate_text_expecting_no_entities():

    text = '''Beta-adrenergic agonist medicines may produce significant hypokalemia in some patients,'''

    annotations = []

    annotated_text_actual = main._annotate_text(annotations, text)

    annotated_text_expected = [{'text': 'Beta-adrenergic agonist medicines may produce significant hypokalemia in some patients,', 'label': None, 'class': None}]

    assert annotated_text_actual == annotated_text_expected


'''
def test_ner(client):
    r = client.post(
        '/ner',
        data='{"text": "Hello"}',
        headers={
            'Content-Type': 'application/json'
        })

    assert r.status_code == 200
    data = json.loads(r.data.decode('utf-8'))
    print(data)
    assert data['text'] == 'drug'
'''
