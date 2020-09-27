from flask import Flask, request, render_template, session, redirect, url_for
from twilio.rest import Client
import mysql.connector
from datetime import date
import requests as REQUESTS

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
            return render_template("index.html.jinja", logged_in=True)
        else:
            return redirect(url_for("home_page"))
    else:
        return redirect(url_for("home_page"))


@app.route("/logout")
def get_me_out():
    session.pop("employee", None)
    session.pop("name", None)
    session.pop("phone", None)
    return render_template("index.html.jinja")

@app.route("/schedule")
def schedule():
    # Query the Appointments and display those relevant to the logged in service advisor
    if session.get("name"):
        cursor = cnx.cursor()
        today = date.today()
        stmt = "SELECT Time, ClientID, LicensePlateN, Details FROM Appointments WHERE ServiceAdvID = %s AND Day = %s"
        params = (session.get("employee"), today)
        cursor.execute(stmt, params)
        records = cursor.fetchall()
        appts = []
        for record in records:
            appt = {"time": "", "client": "", "vehicle": "", "detail": ""}
            appt["time"] = str(record[0])
            appt["client"] = record[1]
            appt["vehicle"] = record[2]
            appt["detail"] = record[3]
            appts.append(appt)

        for x in appts:
            stmt = "SELECT firstName, lastName FROM Clients WHERE idClient = %s"
            params = (x.get("client"),)
            cursor.execute(stmt, params)
            name = cursor.fetchone()
            x["client"] = name[0] + " " + name[1]
            
            stmt = "SELECT maker, model FROM Vehicles WHERE licensePlate = %s"
            params = (x.get("vehicle"),)
            cursor.execute(stmt, params)
            vehicle = cursor.fetchone()
            x["vehicle"] = vehicle[0] + " " + vehicle[1]

        stuff = []
        for x in appts:
            stuff.append(list(x.values()))
        
        if records == None:
            return render_template("schedule.html.jinja", logged_in=True, date=today)
        else:
            return render_template("schedule.html.jinja", logged_in=True, date=today, schedule=stuff)
    else:
        return render_template("index.html.jinja")


@app.route("/customer")
def customer():
    cursor = cnx.cursor()
    stmt = "SELECT * FROM Clients"
    cursor.execute(stmt)
    records = cursor.fetchall()
    return render_template("customer.html.jinja", logged_in=True, results=records)



@app.route("/notify/<license_plate>")
def test_endpoint(license_plate):
    cursor = cnx.cursor()
    #plate = get_plate()
    plate = license_plate
    stmt = "SELECT ServiceAdvID FROM Appointments WHERE licensePlateN = %s"
    params = (plate,)
    cursor.execute(stmt, params)
    advisor = cursor.fetchone()[0]
    stmt = "SELECT phone FROM ServiceAdvisors WHERE idServiceAdvisors = %s"
    params = (advisor,)
    cursor.execute(stmt, params)
    advisor_phone = cursor.fetchone()[0]
    stmt = "SELECT idClient FROM Vehicles WHERE licensePlate = %s"
    params = (plate,)
    cursor.execute(stmt, params)
    record = cursor.fetchone()
    stmt = "SELECT phone FROM Clients WHERE idClient = %s"
    params = (record[0],)
    cursor.execute(stmt, params)
    client_phone = cursor.fetchone()[0]

    client.messages.create(
        to=client_phone,
        from_=PHONE,
        body="Thank you for checking in to your appointment. Our Service Advisor will be with you shortly."
    )

    client.messages.create(
        to=advisor_phone,
        from_=PHONE,
        body="Your client is here. For more details check....."
    )
    
    return "Check phone."

def get_plate():
    r = REQUESTS.get("https://d118e4f3f480.ngrok.io/")
    return r.text