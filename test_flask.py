from flask import Flask

test_app = Flask(__name__)

@test_app.route("/")
def test():
    return "FLASK IS WORKING!"

if __name__ == "__main__":
    test_app.run(host="127.0.0.1", port=5050, debug=False)