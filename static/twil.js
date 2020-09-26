function send_message() {
    // Get form data
    // POST to python end point
    // Need phone number

    var f = document.getElementById("phone_form");
    var form_data = new FormData(f);

    var r = new XMLHttpRequest();
    r.open("POST", "http://localhost:5000/send");
    r.send(form_data);
}