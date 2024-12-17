
## External computer
$ python3 -m venv .venv
$ source .venv/bin/activate
$ .venv/bin/python app.py
$ pip install flask
$ pip install spacy
$ pip install torch
$ pip freeze > requirements.txt
$ python -m pip download --trusted-host=pypi.org --trusted-host=files.pythonhosted.org --only-binary :all: --dest ./wheels_ubuntu --no-cache -r requirements.txt

## Internal computer
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt --no-index -f ./wheels_ubuntu/ --upgrade
