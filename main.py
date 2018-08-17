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

"""Google Cloud Endpoints sample application.

Demonstrates how to create a simple echo API as well as how to deal with
various authentication methods.
"""

import base64
import json
import logging
import numpy as np
from flask import Flask, jsonify, request, render_template
from six.moves import http_client
from drugner import DrugNER

import drugner

app = Flask(__name__)

# Load model 
nerModel = DrugNER('drug', '/models/drug/')

PLACEHOLDER_TEXT = '''Beta-adrenergic agonist medicines may produce significant hypokalemia in some patients, possibly through intracellular shunting, which has the potential to produce adverse cardiovascular effects. The decrease in serum potassium is usually transient, not requiring supplementation. Beta-agonist medications may produce transient hyperglycemia in some patients. In clinical trials evaluating BREO ELLIPTA in subjects with COPD or asthma, there was no evidence of a treatment effect on serum glucose or potassium.'''

PLACEHOLDER_RESPONSE ={'entities': [{'text': 'may', 'start_char': 34, 'end_char': 37, 'label': 'Factor'}, {'text': 'significant', 'start_char': 46, 'end_char': 57, 'label': 'Severity'}, {'text': 'hypokalemia', 'start_char': 58, 'end_char': 69, 'label': 'AdverseReaction'}, {'text': 'decrease in serum potassium', 'start_char': 200, 'end_char': 227, 'label': 'AdverseReaction'}, {'text': 'Beta-agonist medications', 'start_char': 281, 'end_char': 305, 'label': 'DrugClass'}, {'text': 'may', 'start_char': 306, 'end_char': 309, 'label': 'Factor'}, {'text': 'transient', 'start_char': 318, 'end_char': 327, 'label': 'Severity'}, {'text': 'hyperglycemia', 'start_char': 328, 'end_char': 341, 'label': 'AdverseReaction'}, {'text': 'potassium', 'start_char': 500, 'end_char': 509, 'label': 'AdverseReaction'}]} 


def _get_entities_from_text(request):

    if request.method == 'POST':
        input_text = request.form.get('text')
        if input_text == PLACEHOLDER_TEXT:
            entities = PLACEHOLDER_RESPONSE
            text = input_text
        else:
            entities = nerModel.evaluate(input_text)
            text = input_text
    elif request.method == 'GET':
        entities = None
        text = PLACEHOLDER_TEXT

    return entities, text


def _annotate_text(annotations, text):

    locs = np.empty((len(annotations), 2), dtype=np.int16)
    for i, annotation in enumerate(annotations):
        locs[i, :] = (annotation['start_char'], annotation['end_char'])
    locs = np.sort(locs, axis=0)

    annotations.sort(key=lambda x: x['start_char'])

    def build_annotation_block(text, label):
        if label is not None:
            text_class = label.lower().replace(" ", "")
        else:
            text_class = None
        return {'text': text, 'label': label, 'class': text_class}

    # initialize
    annotated_text = []
    text_block = ''
    annotating = False
    annotated_loc = 0
    for i, char in enumerate(text):
        if locs.shape[0] > 0  and i >= locs[annotated_loc, 0] and i <= locs[annotated_loc, 1]:
            # if we should continue annotating add the character
            if i == locs[annotated_loc, 1]:
                # finished label, add text block
                block = build_annotation_block(text_block, annotations[annotated_loc]['label'])
                annotated_text.append(block)
                annotating = False
                text_block = ''
                text_block += char
                if (annotated_loc < locs.shape[0] - 1):
                    annotated_loc += 1
            elif i == locs[annotated_loc, 0]:
                # starting label, add text block
                block = build_annotation_block(text_block, None)
                annotated_text.append(block)
                text_block = ''
                text_block += char
            else:
                annotating = True
                text_block += char
        else:
            text_block += char
            if i == len(text) - 1:
                block = build_annotation_block(text_block, None)
                annotated_text.append(block)

    return annotated_text


def _base64_decode(encoded_str):
    # Add paddings manually if necessary.
    num_missed_paddings = 4 - len(encoded_str) % 4
    if num_missed_paddings != 4:
        encoded_str += b'=' * num_missed_paddings
    return base64.b64decode(encoded_str).decode('utf-8')


@app.route('/', methods=['POST', 'GET'])
def index():

    """Identify FDA adverse events from text"""
    # TODO: change variable scops in conditionals
    entities, text = _get_entities_from_text(request)

    annotated_text = None
    if entities is not None:
        annotated_text = _annotate_text(entities['entities'], text)

    return render_template('index.html',
                           input=text,
                           annotated_text=annotated_text)


@app.route('/ner/drug', methods=['POST'])
def ner():
    """Identify FDA adverse events from text"""
    text = request.form.get('text')

    def get_response(text):
        if (text == PLACEHOLDER_TEXT):
            return PLACEHOLDER_RESPONSE
        else:
            return nerModel.evaluate(text)

    response = get_response(text)

    return render_template('index.html', entities=response, input=text)


@app.route('/ner/drug.json', methods=['POST'])
def nerJson():
    """Identify FDA adverse events from text"""
    text = request.get_json().get('text', '')
    response = nerModel.evaluate(text)
    return jsonify(response)


@app.errorhandler(http_client.INTERNAL_SERVER_ERROR)
def unexpected_error(e):
    """Handle exceptions by returning swagger-compliant json."""
    logging.exception('An error occured while processing the request.')
    response = jsonify({
        'code': http_client.INTERNAL_SERVER_ERROR,
        'message': 'Exception: {}'.format(e)})
    response.status_code = http_client.INTERNAL_SERVER_ERROR
    return response


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='0.0.0.0', port=8080, debug=True)
