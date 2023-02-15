from flask import Flask, request

app = Flask(__name__)

@app.route("/alice", methods=["POST"])
def main():
    text = request.json.get('request', {}).get('command')
    response_text = "aaa"
    if(text.lower() == "привет"):
        response_text="пошел нафиг"
    else:
        response_text="привет"
    response = {
        'response':
            {
                'text': response_text,
                'end_session': False
            },
        'version': '1.0'
    }
    return response


app.run('0.0.0.0', port=5000, debug=True)