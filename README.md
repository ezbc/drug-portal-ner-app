Web app for processing free text in drug adverse events

https://drug-portal.appspot.com/

# Overview

This repo is for a demo web application. The app uses
an entity extraction model service trained with the Python spacy library to 
reduce the time spent manufacturers code adverse event reports by automatically tagging
report text.

For more details read [this blog post](https://ezbc.me/2018/08/07/drug-adverse-event-entity-extraction).

# Getting Started

Clone the repo and change directories to the repo

```bash
git clone git@github.com:ezbc/drug-portal-ner-app.git
cd drug-portal-ner-app
```

Start in Docker 

```bash
docker-compose up
```

Visit in browser at default port 8085.
