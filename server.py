from flask import Flask
import flask
import sys, time
app = Flask(__name__)

serverVector = [[10, 55], [2, 10], [5, 30], [7, 40], [5, 30]]

serverName = sys.argv[1]
serverNum = int(serverName[-1])

@app.route('/')
def hello():
    Headers = flask.request.headers
    if('Nic' in Headers):
        toWait = int(Headers['Nic'])/serverVector[serverNum-1][0]
        print("Req takes ", toWait, " time.")
        #time.sleep(toWait)
    return serverName

if __name__ == '__main__':
    app.run(port=sys.argv[2])