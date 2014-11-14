from flask import Flask
app = Flask(__name__)

@app.route('/hello')
def helloWorld():
    return 'Hello world!'

@app.route('/hello2')
def hiyaWorld():
    return 'Hi biatch.'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
