# The Google App Engine python runtime is Debian Jessie with Python installed
# and various os-level packages to allow installation of popular Python
# libraries. The source is on github at:
#   https://github.com/GoogleCloudPlatform/python-docker
FROM gcr.io/drug-portal/spacy/models/drug:1.0.0 as models

FROM gcr.io/google_appengine/python

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm /var/lib/apt/lists/*_*

RUN pip3 install \
	Flask==0.12.2 \
	gunicorn==19.7.1 \
	six==1.11.0 \
	pyyaml==3.12 \
	requests==2.18.4 \
	spacy==2.0.12

COPY --from=models /models /models

ADD . /app
WORKDIR /app

RUN ls ./

ENTRYPOINT ["gunicorn", "-b", ":8080", "main:app"]
