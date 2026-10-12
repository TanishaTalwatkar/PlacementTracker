from flask import Flask, render_template, request, redirect, session
from firebase_config import db


app = Flask(__name__)

app.secret_key = "placement_tracker_secret_key"
# ---------------- HOME PAGE ----------------

@app.route("/")
def home():

    return render_template("index.html")


# ---------------- ADD APPLICATION ----------------

@app.route("/add", methods=["GET", "POST"])
def add_application():
    if "user_id" not in session:
     redirect("/login")

    if request.method == "POST":

        company = request.form["company"]

        position = request.form["position"]

        date = request.form["date"]

        status = request.form["status"]

        package = request.form["package"]

        location = request.form["location"]


        # Save data to Firebase Firestore
        db.collection("applications").add({

             "company": company,

             "position": position,

             "date": date,

             "status": status,

             "package": package,

             "location": location,

             "user_id": session["user_id"]

         })


        # After saving, go to applications page

        return redirect("/applications")


    return render_template("add_application.html")


# ---------------- VIEW APPLICATIONS ----------------

@app.route("/applications")
def view_applications():

    applications = []


    documents = db.collection("applications").stream()


    for document in documents:

        data = document.to_dict()

        data["id"] = document.id

        applications.append(data)


    return render_template(
        "applications.html",
        applications=applications
    )

# ---------------- RUN APPLICATION ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]

        email = request.form["email"]

        password = request.form["password"]

        course = request.form["course"]


        db.collection("users").add({

            "name": name,

            "email": email,

            "password": password,

            "course": course

        })


        return redirect("/login")


    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]


        users = db.collection("users").stream()


        for user in users:

            data = user.to_dict()


            if data["email"] == email and data["password"] == password:

                session["user_id"] = user.id

                session["user_name"] = data["name"]

                session["user_email"] = data["email"]

                return redirect("/dashboard")


        return "Invalid email or password"


    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/add_interview", methods=["GET", "POST"])
def add_interview():

    if request.method == "POST":

        company = request.form["company"]

        date = request.form["date"]

        time = request.form["time"]

        interview_round = request.form["round"]

        mode = request.form["mode"]


        db.collection("interviews").add({

            "company": company,

            "date": date,

            "time": time,

            "round": interview_round,

            "mode": mode,

            "user_id": session["user_id"]

        })


        return redirect("/interviews")


    return render_template("add_interview.html")


@app.route("/interviews")
def interviews():

    interviews = []

    documents = db.collection("interviews").stream()


    for document in documents:

        data = document.to_dict()

        if data.get("user_id") == session.get("user_id"):

            interviews.append(data)


    return render_template(
        "interviews.html",
        interviews=interviews
    )

@app.route("/edit/<application_id>", methods=["GET", "POST"])
def edit_application(application_id):

    application_ref = db.collection("applications").document(application_id)


    if request.method == "POST":

        new_status = request.form["status"]


        application_ref.update({

            "status": new_status

        })


        return redirect("/applications")


    return render_template(
        "edit_application.html"
    )

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if request.method == "POST":

        resume = request.form["resume"]

        linkedin = request.form["linkedin"]

        portfolio = request.form["portfolio"]


        db.collection("profiles").document(
            session["user_id"]
        ).set({

            "resume": resume,

            "linkedin": linkedin,

            "portfolio": portfolio,

            "user_id": session["user_id"]

        })


        return redirect("/dashboard")


    return render_template("profile.html")

if __name__ == "__main__":

    app.run(debug=True)

