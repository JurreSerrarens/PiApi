from flask import Flask
import json

app = Flask(__name__)

@app.route('/')
def index():
        object = '{ "name":"John", "age":30, "city":"New York"}'
        return json.loads(object)

if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0')