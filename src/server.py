from flask import Flask, request, Response
import jsonpickle
import os
import ocr
import functools
print = functools.partial(print, flush=True)

# Initialize the Flask application
app = Flask(__name__)

# route http posts to this method
@app.route('/api/test', methods=['POST'])
def test():
    r = request
    print(r.files,flush = True)
    file = r.files['image']
    path = os.getcwd() + '/last.jpg'
    file.save(path)
    result = ocr.ocr(path)
    response = {'ocr_result': result}
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")

# start flask app
app.run(host="0.0.0.0", port=5000)
