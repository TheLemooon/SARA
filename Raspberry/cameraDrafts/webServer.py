m flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Raspberry Pi Access Point!"

if __name__ == '__main__':
    app.run(host='192.168.4.1', port=80)
