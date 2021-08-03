import logging
import os

from flask import Flask, request
from flask_cors import CORS

from nowc import main

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def get():
    return {'usage': '/nowc?lat=35.68&lon=139.77&page=5'}, 200

@app.route('/nowc', methods=['GET'])
def get_nowc():
    if request.args.get('lat') is not None:
        lat = float(request.args.get('lat'))
    else:
        lat = 35.681236

    if request.args.get('lon') is not None:
        lon = float(request.args.get('lon'))
    else:
        lon = 139.76712

    if request.args.get('page') is not None:
        page = int(request.args.get('page'))
    else:
        page = 13

    result = main(lat, lon, page, False)
    logger.info(result)
    return result, 200

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    app.run(host=host, port=port, debug=True)
