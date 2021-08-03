# py -m venv seleenv
python -m venv seleenv

# seleenv\Scripts\activate
source seleenv/bin/activate

python -m pip install --upgrade pip
python -m pip install selenium Pillow Flask gunicorn flask-cors
python -m pip install pyderman

python app.py
