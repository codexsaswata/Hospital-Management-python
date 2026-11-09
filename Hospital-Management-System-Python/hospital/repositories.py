from .db import fetch_all, fetch_one, execute, call_procedure

def dashboard_metrics():
    queries = {
        "Patients": "SELECT COUNT(*) n FROM patients",
        "Active doctors": "SELECT COUNT(*) n FROM doctors WHERE active=TRUE",
        "Appointments today": "SELECT COUNT(*) n FROM appointments WHERE DATE(appointment_datetime)=CURDATE()",
        "Outstanding bills": "SELECT COUNT(*) n FROM vw_outstanding_bills WHERE balance_amount>0",
    }
    data = {k: fetch_one(q)["n"] for k, q in queries.items()}
    data["Outstanding balance"] = fetch_one(
        "SELECT COALESCE(SUM(balance_amount),0) amount FROM vw_outstanding_bills"
    )["amount"]
    return data

def list_patients(search=""):
    t=f"%{search}%"
    return fetch_all("""SELECT * FROM patients
        WHERE first_name LIKE %s OR last_name LIKE %s OR phone LIKE %s
        ORDER BY patient_id DESC""",(t,t,t))

def add_patient(d):
    return execute("""INSERT INTO patients(first_name,last_name,date_of_birth,gender,phone,email,
        blood_group,address,emergency_contact) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""",tuple(d))

def update_patient(i,d):
    return execute("""UPDATE patients SET first_name=%s,last_name=%s,date_of_birth=%s,gender=%s,
        phone=%s,email=%s,blood_group=%s,address=%s,emergency_contact=%s WHERE patient_id=%s""",
        tuple(d)+(i,))

def delete_patient(i):
    return execute("DELETE FROM patients WHERE patient_id=%s",(i,))

def list_doctors(search=""):
    t=f"%{search}%"
    return fetch_all("""SELECT * FROM doctors WHERE first_name LIKE %s OR last_name LIKE %s
        OR specialization LIKE %s ORDER BY doctor_id DESC""",(t,t,t))

def add_doctor(d):
    return execute("""INSERT INTO doctors(first_name,last_name,gender,phone,email,specialization,
        consultation_fee,hire_date,active) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""",tuple(d))

def update_doctor(i,d):
    return execute("""UPDATE doctors SET first_name=%s,last_name=%s,gender=%s,phone=%s,email=%s,
        specialization=%s,consultation_fee=%s,hire_date=%s,active=%s WHERE doctor_id=%s""",tuple(d)+(i,))

def list_departments():
    return fetch_all("SELECT * FROM departments ORDER BY department_name")

def add_department(n,f,p):
    return execute("INSERT INTO departments(department_name,floor_number,phone) VALUES(%s,%s,%s)",(n,f,p))

def patient_options():
    return fetch_all("SELECT patient_id,CONCAT(first_name,' ',last_name) name FROM patients ORDER BY name")

def doctor_options():
    return fetch_all("""SELECT doctor_id,CONCAT(first_name,' ',last_name,' - ',specialization) name
        FROM doctors WHERE active=TRUE ORDER BY name""")

def list_appointments(search=""):
    t=f"%{search}%"
    return fetch_all("""SELECT a.appointment_id,a.appointment_datetime,
        CONCAT(p.first_name,' ',p.last_name) patient,
        CONCAT(d.first_name,' ',d.last_name) doctor,a.reason,a.status,a.notes
        FROM appointments a JOIN patients p ON p.patient_id=a.patient_id
        JOIN doctors d ON d.doctor_id=a.doctor_id
        WHERE CONCAT(p.first_name,' ',p.last_name) LIKE %s
        OR CONCAT(d.first_name,' ',d.last_name) LIKE %s OR a.status LIKE %s
        ORDER BY a.appointment_datetime DESC""",(t,t,t))

def book_appointment(p,d,dt,reason):
    return call_procedure("sp_book_appointment",(p,d,dt,reason))

def update_appointment_status(i,s):
    return execute("UPDATE appointments SET status=%s WHERE appointment_id=%s",(s,i))

def list_rooms():
    return fetch_all("SELECT * FROM rooms ORDER BY room_number")

def add_room(n,t,c,s):
    return execute("INSERT INTO rooms(room_number,room_type,daily_charge,availability_status) VALUES(%s,%s,%s,%s)",(n,t,c,s))

def update_room_status(i,s):
    return execute("UPDATE rooms SET availability_status=%s WHERE room_id=%s",(s,i))

def list_services():
    return fetch_all("SELECT * FROM services ORDER BY service_name")

def add_service(n,d,c):
    return execute("INSERT INTO services(service_name,description,standard_charge) VALUES(%s,%s,%s)",(n,d,c))

def list_bills():
    return fetch_all("SELECT * FROM vw_outstanding_bills ORDER BY bill_date DESC,bill_id DESC")

def create_bill(patient_id, appointment_id, due_date, discount, tax_rate, items):
    from .db import connection
    with connection() as conn:
        cur=conn.cursor()
        cur.execute("""INSERT INTO bills(patient_id,appointment_id,due_date,discount,tax_rate)
            VALUES(%s,%s,%s,%s,%s)""",(patient_id,appointment_id or None,due_date,discount,tax_rate))
        bill_id=cur.lastrowid
        for desc,qty,price in items:
            cur.execute("INSERT INTO bill_items(bill_id,item_description,quantity,unit_price) VALUES(%s,%s,%s,%s)",
                        (bill_id,desc,qty,price))
        cur.close()
        return bill_id

def add_payment(b,a,m,r):
    return call_procedure("sp_add_payment",(b,a,m,r or None))

def list_payments():
    return fetch_all("""SELECT p.*,CONCAT(pt.first_name,' ',pt.last_name) patient
        FROM payments p JOIN bills b ON b.bill_id=p.bill_id
        JOIN patients pt ON pt.patient_id=b.patient_id ORDER BY p.payment_date DESC""")

def patient_history(i):
    return call_procedure("sp_patient_appointment_history",(i,))

def monthly_revenue():
    return fetch_all("SELECT * FROM vw_monthly_revenue ORDER BY revenue_month")

def doctor_summary():
    return fetch_all("SELECT * FROM vw_doctor_appointment_summary ORDER BY total_appointments DESC")

def outstanding_report():
    return fetch_all("SELECT * FROM vw_outstanding_bills WHERE balance_amount>0 ORDER BY balance_amount DESC")

def service_report():
    return fetch_all("""SELECT s.service_name,SUM(x.quantity) total_quantity,
        SUM(x.quantity*x.unit_price) service_revenue FROM services s
        JOIN appointment_services x ON x.service_id=s.service_id
        GROUP BY s.service_id,s.service_name ORDER BY service_revenue DESC""")
