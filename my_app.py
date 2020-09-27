from flask import Flask, request, render_template, session, redirect, url_for
from twilio.rest import Client
import mysql.connector

cnx = mysql.connector.connect(
    user="root",
    password="Pa11word",
    host="34.121.33.203",
    database="hansdfreespace"
)

ACT_SID = "ACabafbbcc9a4a78ae89a2cb679ac67ee2"
AUTH_TOKEN = "375113a16219fffcac8352d0315f4541"
PHONE = "9548748396"

client = Client(ACT_SID, AUTH_TOKEN)

app = Flask(__name__)
app.secret_key = "my_r@nd0m_5tr!ng"

@app.route("/")
def home_page():
    return render_template("index.html.jinja")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # compare with database
        # create session
        employee = request.form.get("empl_id")
        passwd = request.form.get("password")

        # Find record of user
        cursor = cnx.cursor()
        stmt = "SELECT firstName, password, phone FROM ServiceAdvisors WHERE idServiceAdvisors = %s"
        params = (employee,)
        cursor.execute(stmt, params)
        record = cursor.fetchone()

        # compare the passwords
        if passwd == record[1]:
            session["employee"] = employee
            session["name"] = record[0]
            session["phone"] = record[2]
            return render_template("schedule.html.jinja", logged_in=True)
        else:
            return redirect(url_for("home_page"))
    else:
        return redirect(url_for("home_page"))


@app.route("/schedule")
def schedule():
    # Query the Appointments and display those relevant to the logged in service advisor
    if session.get("name"):
        cursor = cnx.cursor()
        return ""
    else:
        return render_template("index.html.jinja")


@app.route("/customer")
def customer():
    cursor = cnx.cursor()
    stmt = "SELECT * FROM Clients"
    cursor.execute(stmt)
    records = cursor.fetchall()
    return render_template("customer.html.jinja", results=records)


@app.route("/send", methods=["GET", "POST"])
def send_message():
    if request.method == "POST":
        recipient = request.form.get("phone")
        client.messages.create(
            to=recipient,
            from_=PHONE,
            body="Sent from a annoying Shellhacks app."
        )
        return "Message sent."
    else:
        return "This page doesn't accept GET requests."