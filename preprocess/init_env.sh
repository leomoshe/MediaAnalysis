#!/bin/bash

cd ./produce_entities/produce_spacy
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt --no-index -f ./wheels/ --upgrade
deactivate
cd ../..

cd ./produce_entities/produce_dicta
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt --no-index -f ./wheels/ --upgrade
deactivate
cd ../..

cd ./produce_transcription
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt --no-index -f ./wheels/ --upgrade
deactivate
cd ..