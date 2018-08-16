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

PLACEHOLDER_TEXT = '''LABA, such as vilanterol, one of the active ingredients in BREO ELLIPTA, increase the risk of asthma-related death. Currently available data are inadequate to determine whether concurrent use of inhaled corticosteroids or other long-term asthma control drugs mitigates the increased risk of asthma-related death from LABA. Available data from controlled clinical trials suggest that LABA increase the risk of asthma-related hospitalization in pediatric and adolescent patients. Data from a large placebo-controlled US trial that compared the safety of another LABA (salmeterol) or placebo added to usual asthma therapy showed an increase in asthma-related deaths in subjects receiving salmeterol.  [See Warnings and Precautions (5.1).]'''
PLACEHOLDER_RESPONSE = {'entities': [{'text': 'death', 'start_char': 109, 'end_char': 114, 'label': 'AdverseReaction'}, {'text': 'corticosteroids', 'start_char': 203, 'end_char': 218, 'label': 'DrugClass'}, {'text': 'death', 'start_char': 306, 'end_char': 311, 'label': 'AdverseReaction'}, {'text': 'LABA', 'start_char': 317, 'end_char': 321, 'label': 'DrugClass'}, {'text': 'LABA', 'start_char': 560, 'end_char': 564, 'label': 'DrugClass'}, {'text': 'deaths', 'start_char': 656, 'end_char': 662, 'label': 'AdverseReaction'}]}

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


    # {'entities': [{'text': 'death', 'start_char': 109,
    #  'end_char': 114, 'label': 'AdverseReaction'}]}
    '''
drug-portal-ner | {'text': 'death', 'start_char': 109, 'end_char': 114, 'label': 'AdverseReaction'}
drug-portal-ner | {'text': 'corticosteroids', 'start_char': 203, 'end_char': 218, 'label': 'DrugClass'}
drug-portal-ner | {'text': 'death', 'start_char': 306, 'end_char': 311, 'label': 'AdverseReaction'}
drug-portal-ner | {'text': 'LABA', 'start_char': 317, 'end_char': 321, 'label': 'DrugClass'}
drug-portal-ner | {'text': 'LABA', 'start_char': 560, 'end_char': 564, 'label': 'DrugClass'}
drug-portal-ner | {'text': 'deaths', 'start_char': 656, 'end_char': 662, 'label': 'AdverseReaction'}
drug-portal-ner | [[109 114]
drug-portal-ner |  [203 218]
drug-portal-ner |  [306 311]
drug-portal-ner |  [317 321]
drug-portal-ner |  [560 564]
drug-portal-ner |  [656 662]]
    '''

    def annotate_text(annotations, text):
        response = {}

        locs = np.empty((len(annotations), 2), dtype=np.int16)
        for i, annotation in enumerate(annotations):
            print(annotation)
            locs[i, :] = (annotation['start_char'], annotation['end_char'])
        locs = np.sort(locs, axis=0)

        annotations.sort(key=lambda x: x['start_char'])
        print(annotations)

        def build_annotation_block(text, label):
            return {'text': text, 'label': label}


        # initialize
        annotated_text = []
        text_block = ''
        annotating = False
        annotated_loc = 0
        for i, char in enumerate(text):
            if i >= locs[annotated_loc, 0] and i <= locs[annotated_loc, 1]:
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

        print(annotated_text)



        return locs

    annotated_text = annotate_text(entities['entities'], text)

    return render_template('index.html',
            input=text,
            annotated_text=annotated_text)

@app.route('/echo', methods=['POST'])
def echo():
    """Simple echo service."""
    message = request.get_json().get('message', '')
    return jsonify({'message': message})

@app.route('/ner/drug', methods=['POST'])
def ner():
    """Identify FDA adverse events from text"""
    text = request.form.get('text')

    def get_response(text):
        if (text == PLACEHOLDER_TEXT):
            return PLACEHOLDER_RESPONSE;
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
