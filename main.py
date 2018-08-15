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
nerModel = DrugNER('drug', './models/drug/')

PLACEHOLDER_TEXT = '''LABA, such as vilanterol, one of the active ingredients in BREO ELLIPTA, increase the risk of asthma-related death. Currently available data are inadequate to determine whether concurrent use of inhaled corticosteroids or other long-term asthma control drugs mitigates the increased risk of asthma-related death from LABA. Available data from controlled clinical trials suggest that LABA increase the risk of asthma-related hospitalization in pediatric and adolescent patients. Data from a large placebo-controlled US trial that compared the safety of another LABA (salmeterol) or placebo added to usual asthma therapy showed an increase in asthma-related deaths in subjects receiving salmeterol.  [See Warnings and Precautions (5.1).]'''

def _base64_decode(encoded_str):
    # Add paddings manually if necessary.
    num_missed_paddings = 4 - len(encoded_str) % 4
    if num_missed_paddings != 4:
        encoded_str += b'=' * num_missed_paddings
    return base64.b64decode(encoded_str).decode('utf-8')

@app.route('/')
def index():
    return render_template('index.html', input=PLACEHOLDER_TEXT)

@app.route('/echo', methods=['POST'])
def echo():
    """Simple echo service."""
    message = request.get_json().get('message', '')
    return jsonify({'message': message})

@app.route('/ner/drug', methods=['POST'])
def ner():
    """Identify FDA adverse events from text"""
    text = request.form.get('text')
    response = nerModel.evaluate(text)

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
    app.run(host='127.0.0.1', port=8080, debug=False)
