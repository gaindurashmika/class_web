import os
import json
import datetime
from flask import Flask, render_template, request, jsonify

# Flask app එක හදාගැනීම
app = Flask(__name__)

# දත්ත ගබඩා කරන ගොනුවේ නම
DATA_FILE = "student_data.json"

def load_data():
    """ගබඩා කර ඇති ශිෂ්‍ය දත්ත නැවත ලබා ගැනීම"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            # Check if file is empty
            if os.path.getsize(DATA_FILE) > 0:
                return json.load(f)
    return {}

def save_data(students):
    """ශිෂ්‍ය දත්ත ගොනුවේ ගබඩා කිරීම"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(students, f, indent=4, ensure_ascii=False)

# ප්‍රධාන web page එක පෙන්වන route එක
@app.route('/')
def index():
    # index.html file එක user ට පෙන්වීම
    return render_template('index.html')

# QR code scan එකක් ආවම වැඩ කරන route එක
@app.route('/scan', methods=['POST'])
def scan_student():
    data = request.get_json()
    student_id = data.get('studentId')
    
    if not student_id:
        return jsonify({'status': 'error', 'message': 'ශිෂ්‍ය අංකයක් ලැබුනේ නැත.'}), 400

    students = load_data()
    
    if student_id in students:
        student = students[student_id]
        today = datetime.date.today().strftime("%Y-%m-%d")
        
        # පැමිණීම සටහන් කිරීම
        if today not in student["attendance"]:
            student["attendance"].append(today)
            attendance_msg = f"අද දින ({today}) පැමිණීම සටහන් කරන ලදී."
        else:
            attendance_msg = f"අද දින පැමිණීම දැනටමත් සටහන් කර ඇත."

        # ගෙවීම් තත්ත්වය පරීක්ෂා කිරීම
        # Corrected to use English month name which is standard in strftime
        current_month_name = datetime.date.today().strftime("%B") # e.g., 'June'
        payment_status = student["payments"].get(current_month_name.capitalize(), "Not Paid")

        if payment_status == "Paid":
            payment_msg = f"මේ මාසය ({current_month_name}) සඳහා ගෙවා ඇත."
            payment_color = "green"
        else:
            payment_msg = f"මේ මාසය ({current_month_name}) සඳහා ගෙවීම් කර නොමැත."
            payment_color = "red"

        save_data(students)
        
        response_message = f"ආයුබෝවන්, {student['name']}!\n{attendance_msg}\n{payment_msg}"
        return jsonify({
            'status': 'success', 
            'message': response_message,
            'paymentColor': payment_color
        })
    else:
        return jsonify({'status': 'error', 'message': f"වැරදි ශිෂ්‍ය අංකයක්: {student_id}"}), 404

# Flask server එක run කිරීම
if __name__ == '__main__':
    # host='0.0.0.0' දැම්මම ඔයාගේ network එකේ අනිත් devices වලටත් access කරන්න පුළුවන්
    app.run(debug=True, host='0.0.0.0', port=5000)