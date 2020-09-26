from flask import Flask, request, render_template
from twilio.rest import Client

ACT_SID = "ACabafbbcc9a4a78ae89a2cb679ac67ee2"
AUTH_TOKEN = "375113a16219fffcac8352d0315f4541"
PHONE = "9548748396"

client = Client(ACT_SID, AUTH_TOKEN)

"""
client.messages.create(
    to="9547026088",
    from_=PHONE,
    body="Test message"
)
"""

app = Flask(__name__)

@app.route("/")
def home_page():
    return "<html><body><button>Send Message</button></body></html>"


@app.route("/send", methods=["GET", "POST"])
def send_message():
    if request.method == "POST":
        recipient = request.form.get("recipient")
        client.messages.create(
            to=recipient,
            from_=PHONE,
            body="Sent from a annoying Shellhacks app."
        )
        return ""
    else:
        return ""