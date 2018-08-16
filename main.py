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
    input_text = request.form.get('text')
    if (input_text is None):
        response = None
        text = PLACEHOLDER_TEXT
    elif (input_text == PLACEHOLDER_TEXT):
        response = PLACEHOLDER_RESPONSE
        text = input_text
    else:
        response = nerModel.evaluate(input_text)
        text = input_text

    return render_template('index.html', entities=response, input=text)

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
