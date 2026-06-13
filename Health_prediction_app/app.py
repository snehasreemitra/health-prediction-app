from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret"

DB_NAME = "patients.db"


# ----------------------------
# DATABASE
# ----------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            dob TEXT NOT NULL,
            email TEXT NOT NULL,
            glucose REAL NOT NULL,
            haemoglobin REAL NOT NULL,
            cholesterol REAL NOT NULL,
            remarks TEXT
        )
    """)

    conn.commit()
    conn.close()


# ----------------------------
# AI PREDICTION
# ----------------------------
def predict_health(glucose, haemoglobin, cholesterol):

    if glucose > 180:
        return "High Diabetes Risk"

    elif cholesterol > 240:
        return "High Cardiac Risk"

    elif haemoglobin < 10:
        return "Possible Anaemia"

    else:
        return "Healthy"


# ----------------------------
# VALIDATION
# ----------------------------
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)


# ----------------------------
# HOME
# ----------------------------
@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    conn.close()

    return render_template('index.html', patients=patients)


# ----------------------------
# ADD
# ----------------------------
@app.route('/add', methods=['GET', 'POST'])
def add_patient():

    if request.method == 'POST':

        full_name = request.form['full_name']
        dob = request.form['dob']
        email = request.form['email']
        glucose = request.form['glucose']
        haemoglobin = request.form['haemoglobin']
        cholesterol = request.form['cholesterol']

        if not validate_email(email):
            flash("Invalid email")
            return redirect(url_for('add_patient'))

        if datetime.strptime(dob, "%Y-%m-%d").date() > datetime.today().date():
            flash("DOB cannot be future date")
            return redirect(url_for('add_patient'))

        try:
            glucose = float(glucose)
            haemoglobin = float(haemoglobin)
            cholesterol = float(cholesterol)
        except:
            flash("Blood values must be numeric")
            return redirect(url_for('add_patient'))

        remarks = predict_health(
            glucose,
            haemoglobin,
            cholesterol
        )

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO patients
        (
        full_name,
        dob,
        email,
        glucose,
        haemoglobin,
        cholesterol,
        remarks
        )
        VALUES(?,?,?,?,?,?,?)
        """,
        (
            full_name,
            dob,
            email,
            glucose,
            haemoglobin,
            cholesterol,
            remarks
        ))

        conn.commit()
        conn.close()

        flash("Patient Added Successfully")
        return redirect(url_for('index'))

    return render_template('add_patient.html')


# ----------------------------
# EDIT
# ----------------------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if request.method == 'POST':

        full_name = request.form['full_name']
        dob = request.form['dob']
        email = request.form['email']
        glucose = float(request.form['glucose'])
        haemoglobin = float(request.form['haemoglobin'])
        cholesterol = float(request.form['cholesterol'])

        remarks = predict_health(
            glucose,
            haemoglobin,
            cholesterol
        )

        cursor.execute("""
        UPDATE patients
        SET
        full_name=?,
        dob=?,
        email=?,
        glucose=?,
        haemoglobin=?,
        cholesterol=?,
        remarks=?
        WHERE id=?
        """,
        (
            full_name,
            dob,
            email,
            glucose,
            haemoglobin,
            cholesterol,
            remarks,
            id
        ))

        conn.commit()
        conn.close()

        flash("Patient Updated")
        return redirect(url_for('index'))

    cursor.execute(
        "SELECT * FROM patients WHERE id=?",
        (id,)
    )

    patient = cursor.fetchone()

    conn.close()

    return render_template(
        'edit_patient.html',
        patient=patient
    )


# ----------------------------
# DELETE
# ----------------------------
@app.route('/delete/<int:id>')
def delete_patient(id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM patients WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash("Patient Deleted")

    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)