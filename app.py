from flask import Flask, render_template, request, redirect, session
from firebase_config import db

app = Flask(__name__)

app.secret_key = "smart_placement_tracker_secret_key"


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# STUDENT REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()
        course = request.form["course"].strip()

        # Check whether email already exists
        users = db.collection("users").stream()

        for user in users:

            data = user.to_dict()

            if data.get("email", "").strip().lower() == email.lower():
                return "Email already registered. Please login."

        # Add student
        db.collection("users").add({
            "name": name,
            "email": email,
            "password": password,
            "course": course
        })

        return redirect("/login")

    return render_template("register.html")


# =========================================================
# STUDENT LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"].strip()

        users = db.collection("users").stream()

        for user in users:

            data = user.to_dict()

            stored_email = str(data.get("email", "")).strip()
            stored_password = str(data.get("password", "")).strip()

            if (
                stored_email.lower() == email.lower()
                and stored_password == password
            ):

                session["user_id"] = user.id
                session["user_name"] = data.get("name", "")
                session["user_email"] = data.get("email", "")

                return redirect("/dashboard")

        return "Invalid email or password"

    return render_template("login.html")


# =========================================================
# STUDENT LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    applications = []

    documents = db.collection("applications").stream()

    for document in documents:

        data = document.to_dict()

        if data.get("user_id") == user_id:

            applications.append(data)

    total_applications = len(applications)

    selected = 0
    rejected = 0
    pending = 0

    for application in applications:

        status = application.get("status", "Applied")

        if status == "Selected":

            selected += 1

        elif status == "Rejected":

            rejected += 1

        else:

            pending += 1

    # Count interviews
    interview_count = 0

    interviews = db.collection("interviews").stream()

    for interview in interviews:

        data = interview.to_dict()

        if data.get("user_id") == user_id:

            interview_count += 1

    return render_template(
        "dashboard.html",
        name=session.get("user_name"),
        total_applications=total_applications,
        selected=selected,
        rejected=rejected,
        pending=pending,
        interview_count=interview_count
    )


# =========================================================
# ADD APPLICATION - STUDENT
# =========================================================

@app.route("/add", methods=["GET", "POST"])
def add_application():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        company = request.form["company"].strip()
        position = request.form["position"].strip()
        date = request.form["date"].strip()
        package = request.form["package"].strip()
        location = request.form["location"].strip()

        # Student cannot choose status.
        # Every new application starts as Applied.
        status = "Applied"

        db.collection("applications").add({

            "user_id": session["user_id"],

            "company": company,

            "position": position,

            "date": date,

            "status": status,

            "package": package,

            "location": location

        })

        return redirect("/applications")

    return render_template("add_application.html")


# =========================================================
# VIEW STUDENT APPLICATIONS
# =========================================================

@app.route("/applications")
def applications():

    if "user_id" not in session:
        return redirect("/login")

    application_list = []

    documents = db.collection("applications").stream()

    for document in documents:

        data = document.to_dict()

        if data.get("user_id") == session["user_id"]:

            data["id"] = document.id

            application_list.append(data)

    return render_template(
        "applications.html",
        applications=application_list
    )


# =========================================================
# DELETE APPLICATION - STUDENT
# =========================================================

@app.route("/delete/<application_id>")
def delete_application(application_id):

    if "user_id" not in session:
        return redirect("/login")

    application_ref = (
        db.collection("applications")
        .document(application_id)
    )

    document = application_ref.get()

    if document.exists:

        application = document.to_dict()

        # Student can delete only own application
        if application.get("user_id") == session["user_id"]:

            application_ref.delete()

    return redirect("/applications")


# =========================================================
# ADD INTERVIEW - STUDENT
# =========================================================
# This is kept for compatibility with your existing project.
# Normally interviews should be scheduled by Admin.

# @app.route("/add_interview", methods=["GET", "POST"])
# def add_interview():

#     if "user_id" not in session:
#         return redirect("/login")

#     if request.method == "POST":

#         company = request.form["company"].strip()
#         date = request.form["date"].strip()
#         time = request.form["time"].strip()
#         interview_round = request.form["round"].strip()
#         mode = request.form["mode"].strip()

#         db.collection("interviews").add({

#             "user_id": session["user_id"],

#             "company": company,

#             "date": date,

#             "time": time,

#             "round": interview_round,

#             "mode": mode

#         })

#         return redirect("/interviews")

#     return render_template("add_interview.html")


# =========================================================
# VIEW STUDENT INTERVIEWS
# =========================================================

@app.route("/interviews")
def interviews():

    if "user_id" not in session:
        return redirect("/login")

    interview_list = []

    documents = db.collection("interviews").stream()

    for document in documents:

        data = document.to_dict()

        if data.get("user_id") == session["user_id"]:

            data["id"] = document.id

            interview_list.append(data)

    return render_template(
        "interviews.html",
        interviews=interview_list
    )


# =========================================================
# STUDENT PROFILE
# =========================================================

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    if request.method == "POST":

        resume = request.form["resume"].strip()
        linkedin = request.form["linkedin"].strip()
        portfolio = request.form["portfolio"].strip()

        db.collection("profiles").document(user_id).set({

            "user_id": user_id,

            "resume": resume,

            "linkedin": linkedin,

            "portfolio": portfolio

        })

        return redirect("/profile")

    profile_ref = (
        db.collection("profiles")
        .document(user_id)
    )

    profile_document = profile_ref.get()

    profile_data = {}

    if profile_document.exists:

        profile_data = profile_document.to_dict()

    return render_template(
        "profile.html",
        profile=profile_data
    )


# =========================================================
# =========================================================
#                    ADMIN MODULE
# =========================================================
# =========================================================


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"].strip()

        admins = db.collection("admins").stream()

        for admin in admins:

            data = admin.to_dict()

            stored_email = str(
                data.get("email", "")
            ).strip()

            stored_password = str(
                data.get("password", "")
            ).strip()

            if (
                stored_email.lower() == email.lower()
                and stored_password == password
            ):

                session["admin_id"] = admin.id

                session["admin_name"] = data.get(
                    "name",
                    "Admin"
                )

                session["admin_email"] = stored_email

                return redirect("/admin/dashboard")

        return "Invalid Admin Email or Password"

    return render_template("admin_login.html")


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin_id", None)
    session.pop("admin_name", None)
    session.pop("admin_email", None)

    return redirect("/admin/login")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin/dashboard")
def admin_dashboard():

    if "admin_id" not in session:
        return redirect("/admin/login")

    # -----------------------------------------------------
    # TOTAL STUDENTS
    # -----------------------------------------------------

    students = list(
        db.collection("users").stream()
    )

    total_students = len(students)

    # -----------------------------------------------------
    # TOTAL APPLICATIONS
    # -----------------------------------------------------

    applications = list(
        db.collection("applications").stream()
    )

    total_applications = len(applications)

    # -----------------------------------------------------
    # STATUS COUNTS
    # -----------------------------------------------------

    selected = 0
    rejected = 0
    shortlisted = 0
    interview_scheduled = 0

    for application in applications:

        data = application.to_dict()

        status = data.get(
            "status",
            "Applied"
        )

        if status == "Selected":

            selected += 1

        elif status == "Rejected":

            rejected += 1

        elif status == "Shortlisted":

            shortlisted += 1

        elif status == "Interview Scheduled":

            interview_scheduled += 1

    # -----------------------------------------------------
    # TOTAL INTERVIEWS
    # -----------------------------------------------------

    interviews = list(
        db.collection("interviews").stream()
    )

    total_interviews = len(interviews)

    # -----------------------------------------------------
    # DISPLAY ADMIN DASHBOARD
    # -----------------------------------------------------

    return render_template(

        "admin_dashboard.html",

        admin_name=session.get(
            "admin_name",
            "Admin"
        ),

        total_students=total_students,

        total_applications=total_applications,

        selected=selected,

        rejected=rejected,

        shortlisted=shortlisted,

        interview_scheduled=interview_scheduled,

        total_interviews=total_interviews

    )


# =========================================================
# ADMIN - VIEW ALL STUDENTS
# =========================================================

@app.route("/admin/students")
def admin_students():

    if "admin_id" not in session:
        return redirect("/admin/login")

    student_list = []

    students = db.collection("users").stream()

    for student in students:

        data = student.to_dict()

        data["id"] = student.id

        student_list.append(data)

    return render_template(
        "admin_students.html",
        students=student_list
    )


# =========================================================
# ADMIN - VIEW ALL APPLICATIONS
# =========================================================

@app.route("/admin/applications")
def admin_applications():

    if "admin_id" not in session:
        return redirect("/admin/login")

    application_list = []

    applications = db.collection("applications").stream()

    for application in applications:

        data = application.to_dict()

        # -------------------------------------------------
        # Store Firestore document ID
        # -------------------------------------------------

        data["id"] = application.id

        # -------------------------------------------------
        # Default student information
        # -------------------------------------------------

        data["student_name"] = "Unknown Student"
        data["student_email"] = ""

        # -------------------------------------------------
        # Get user_id
        # -------------------------------------------------

        user_id = data.get("user_id")

        # -------------------------------------------------
        # If user_id exists
        # -------------------------------------------------

        if user_id:

            try:

                student_ref = (
                    db.collection("users")
                    .document(user_id)
                )

                student_document = student_ref.get()

                if student_document.exists:

                    student_data = (
                        student_document.to_dict()
                    )

                    data["student_name"] = (
                        student_data.get(
                            "name",
                            "Unknown Student"
                        )
                    )

                    data["student_email"] = (
                        student_data.get(
                            "email",
                            ""
                        )
                    )

                else:

                    data["student_name"] = (
                        "Student Not Found"
                    )

            except Exception as e:

                print(
                    "Error getting student:",
                    e
                )

                data["student_name"] = (
                    "Student Not Found"
                )

        # -------------------------------------------------
        # Old application without user_id
        # -------------------------------------------------

        else:

            data["student_name"] = (
                "Old Application"
            )

            data["student_email"] = ""

        application_list.append(data)

    return render_template(
        "admin_applications.html",
        applications=application_list
    )


# =========================================================
# ADMIN - MANAGE APPLICATION STATUS
# =========================================================

@app.route(
    "/admin/manage/<application_id>",
    methods=["GET", "POST"]
)
def admin_manage_application(application_id):

    if "admin_id" not in session:
        return redirect("/admin/login")

    # -----------------------------------------------------
    # Get application
    # -----------------------------------------------------

    application_ref = (
        db.collection("applications")
        .document(application_id)
    )

    document = application_ref.get()

    if not document.exists:

        return "Application not found"

    application = document.to_dict()

    # -----------------------------------------------------
    # Get student ID
    # -----------------------------------------------------

    user_id = application.get("user_id")

    # -----------------------------------------------------
    # Handle old application
    # -----------------------------------------------------

    if not user_id:

        return """
        <h2>Old Application</h2>
        <p>This application does not have a linked student.</p>
        <p>Please create a new application after student login.</p>
        <a href="/admin/applications">
            Back to Applications
        </a>
        """

    # -----------------------------------------------------
    # Get student
    # -----------------------------------------------------

    student_ref = (
        db.collection("users")
        .document(user_id)
    )

    student_document = student_ref.get()

    student = {}

    if student_document.exists:

        student = student_document.to_dict()

    # -----------------------------------------------------
    # Update status
    # -----------------------------------------------------

    if request.method == "POST":

        new_status = request.form["status"]

        application_ref.update({

            "status": new_status

        })

        return redirect(
            "/admin/applications"
        )

    # -----------------------------------------------------
    # Display manage page
    # -----------------------------------------------------

    return render_template(

        "admin_manage_application.html",

        application=application,

        student=student

    )


# =========================================================
# ADMIN - SCHEDULE INTERVIEW
# =========================================================

@app.route(
    "/admin/interview/<application_id>",
    methods=["GET", "POST"]
)
def admin_interview(application_id):

    if "admin_id" not in session:
        return redirect("/admin/login")

    # -----------------------------------------------------
    # Get application
    # -----------------------------------------------------

    application_ref = (
        db.collection("applications")
        .document(application_id)
    )

    application_document = application_ref.get()

    if not application_document.exists:

        return "Application not found"

    application = application_document.to_dict()

    # -----------------------------------------------------
    # Get student ID
    # -----------------------------------------------------

    user_id = application.get("user_id")

    # -----------------------------------------------------
    # Handle old application
    # -----------------------------------------------------

    if not user_id:

        return """
        <h2>Old Application</h2>
        <p>This application does not have a linked student.</p>
        <p>You cannot schedule an interview for this application.</p>
        <a href="/admin/applications">
            Back to Applications
        </a>
        """

    # -----------------------------------------------------
    # Get student
    # -----------------------------------------------------

    student_ref = (
        db.collection("users")
        .document(user_id)
    )

    student_document = student_ref.get()

    student = {}

    if student_document.exists:

        student = student_document.to_dict()

    # -----------------------------------------------------
    # Schedule interview
    # -----------------------------------------------------

    if request.method == "POST":

        date = request.form["date"].strip()

        time = request.form["time"].strip()

        interview_round = (
            request.form["round"].strip()
        )

        mode = request.form["mode"].strip()

        # -------------------------------------------------
        # Save interview
        # -------------------------------------------------

        db.collection("interviews").add({

            "user_id": user_id,

            "company": application.get(
                "company",
                ""
            ),

            "position": application.get(
                "position",
                ""
            ),

            "date": date,

            "time": time,

            "round": interview_round,

            "mode": mode,

            "application_id": application_id

        })

        # -------------------------------------------------
        # Automatically update application status
        # -------------------------------------------------

        application_ref.update({

            "status": "Interview Scheduled"

        })

        # Go back to application list
        return redirect(
            "/admin/applications"
        )

    # -----------------------------------------------------
    # Display interview form
    # -----------------------------------------------------

    return render_template(

        "admin_interviews.html",

        application=application,

        student=student

    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)