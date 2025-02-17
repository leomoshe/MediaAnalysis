#!/bin/bash

<<comment

comment

echo "Have you done the following steps?"
echo "1) Run sudo apt-get install ffmpeg"
echo "2) Download he_ner_news_trf-3.2.1-py3-none-any.whl and change the path in this file"
echo "3) Install the recommended 'Python' extension from Microsoft for the Python language?"
echo "4) Remove the irrelevant '_internal' or '_external' postfixs from thepp.json files"

read -p "(Y/N): " res
res=${res^^}  # Uppercase

if [[ "$res" != "Y" ]]; then
    echo "Finish the script."
    exit 1
fi

cd ./produce_entities/produce_spacy
python3 -m venv .venv
source .venv/bin/activate
pip install numpy==1.21.6
pip install spacy==3.2.2
pip install file:///home/leoz/Public/dev/MediaAnalysis/packages/he_ner_news_trf-3.2.1-py3-none-any.whl
pip install flask
deactivate
cd ../..

cd ./produce_entities/produce_dicta
python3 -m venv .venv
source .venv/bin/activate
pip install flask
pip install torch
pip install  transformers
deactivate
cd ../..

cd ./produce_transcription
python3 -m venv .venv
source .venv/bin/activate
pip install flask
pip install faster_whisper
deactivate
cd ..
