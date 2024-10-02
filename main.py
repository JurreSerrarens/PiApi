from flask import Flask
import wiringpi
import json

app = Flask(__name__)
wiringpi.wiringPiSetupSys() 
wiringpi.pinMode(7,0)

@app.route('/')
def index():
        rawTemp = wiringpi.analogRead(7)
        object = ('{ "temp":"%s", "nonsense":"definetly"}' % [rawTemp])
        return json.loads(object)

if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0')