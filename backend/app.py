# This script manages your database connection, handles file uploads 
#(just like $_FILES in PHP), and processes CRUD requests (like your old AJAX endpoints).

from flask import Flask, request, jsonify
from flask_cors import CORS
from psycopg2.errors import UniqueViolation # Add this at the top of app.py
import psycopg2
import os
import uuid

app = Flask(__name__)
CORS(app) # Allows React to communicate with this API

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    return psycopg2.connect(
        host="localhost", database="student_db", user="postgres", password="Prof.obi1701"
    )

# CREATE (Register Student)
@app.route('/api/students', methods=['POST'])
def add_student():
    try:
        data = request.form
        image_file = request.files['image']
        
        filename = f"{uuid.uuid4()}_{image_file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(filepath)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO students (student_id, full_name, dob, class_name, arm, image_path, password) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (data['student_id'], data['full_name'], data['dob'], data['class_name'], data.get('arm', ''), filepath, data['password'])
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Student registered!"}), 201
        
    except UniqueViolation:
        return jsonify({"error": "A student with this ID already exists."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
# READ (View Students - UPDATED)
@app.route('/api/students', methods=['GET'])
def get_students():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT student_id, full_name, class_name, dob, arm FROM students")
        rows = cur.fetchall()
        conn.close()
        return jsonify([{
            "student_id": r[0], "full_name": r[1], "class_name": r[2], 
            "dob": str(r[3]), "arm": r[4]
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# UPDATE (Edit Student - NEW)
@app.route('/api/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    try:
        data = request.form
        conn = get_db_connection()
        cur = conn.cursor()
        
        if 'image' in request.files and request.files['image'].filename != '':
            img = request.files['image']
            filepath = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{img.filename}")
            img.save(filepath)
            cur.execute(
                "UPDATE students SET full_name=%s, dob=%s, class_name=%s, arm=%s, password=%s, image_path=%s WHERE student_id=%s",
                (data['full_name'], data['dob'], data['class_name'], data.get('arm', ''), data['password'], filepath, student_id)
            )
        else:
            cur.execute(
                "UPDATE students SET full_name=%s, dob=%s, class_name=%s, arm=%s, password=%s WHERE student_id=%s",
                (data['full_name'], data['dob'], data['class_name'], data.get('arm', ''), data['password'], student_id)
            )
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Student updated!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# DELETE (Remove Student)
@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)