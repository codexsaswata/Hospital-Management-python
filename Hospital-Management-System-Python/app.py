import streamlit as st
import pandas as pd
from datetime import date, datetime, time
from hospital import repositories as repo

st.set_page_config(page_title="Hospital Management System", page_icon="🏥", layout="wide")

st.markdown("""
<style>
.stApp {background:#f3f6fb}
.block-container {max-width:1450px;padding-top:1.5rem}
[data-testid="stSidebar"] {background:#10243a}
[data-testid="stSidebar"] * {color:#f1f5f9}
h1,h2,h3 {color:#142b45}
div[data-testid="stMetric"] {background:white;padding:16px;border-radius:12px;border:1px solid #e3eaf2}
</style>
""", unsafe_allow_html=True)

st.title("🏥 Hospital Management System")
st.caption("Hospital operations, patient records, appointments and billing.")

with st.sidebar:
    st.title("CityCare HMS")
    page=st.radio("MAIN MENU",[
        "Dashboard","Patients","Doctors","Departments","Appointments",
        "Rooms","Services","Billing","Payments","Reports"
    ])
    st.divider()
    st.caption("Python • Streamlit • MySQL")


def table(rows):
    if rows:
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    else:
        st.info("No records found.")

def error(e):
    st.error(str(e))
    st.caption("Check the database connection, required fields and foreign-key constraints.")

def done(message):
    st.success(message)
    st.rerun()

def choose_patient():
    rows=repo.patient_options()
    if not rows:
        st.warning("Register a patient first.")
        return None
    opts={f'{x["name"]} (#{x["patient_id"]})':x["patient_id"] for x in rows}
    return opts[st.selectbox("Patient",list(opts))]

def choose_doctor():
    rows=repo.doctor_options()
    if not rows:
        st.warning("Add an active doctor first.")
        return None
    opts={f'{x["name"]} (#{x["doctor_id"]})':x["doctor_id"] for x in rows}
    return opts[st.selectbox("Doctor",list(opts))]


if page=="Dashboard":
    st.subheader("Operational overview")
    try:
        metrics=repo.dashboard_metrics()
        cols=st.columns(len(metrics))
        for col,(label,value) in zip(cols,metrics.items()):
            col.metric(label,f"₹{float(value):,.2f}" if label=="Outstanding balance" else value)
        a,b=st.columns(2)
        with a:
            st.markdown("#### Latest appointments")
            table(repo.list_appointments()[:8])
        with b:
            st.markdown("#### Outstanding bills")
            table(repo.outstanding_report()[:8])
    except Exception as e: error(e)

elif page=="Patients":
    st.subheader("Patient management")
    t1,t2,t3=st.tabs(["Patient directory","Register patient","Edit / delete"])
    with t1:
        q=st.text_input("Search name or phone")
        try: table(repo.list_patients(q))
        except Exception as e: error(e)
    with t2:
        with st.form("patient_add"):
            c1,c2=st.columns(2)
            first=c1.text_input("First name*"); last=c2.text_input("Last name*")
            dob=c1.date_input("Date of birth",date(1995,1,1),max_value=date.today())
            gender=c2.selectbox("Gender",["Male","Female","Other"])
            phone=c1.text_input("Phone*"); email=c2.text_input("Email")
            blood=c1.selectbox("Blood group",["","A+","A-","B+","B-","AB+","AB-","O+","O-"])
            address=c2.text_input("Address"); emergency=st.text_input("Emergency contact")
            if st.form_submit_button("Register patient",type="primary"):
                if not first.strip() or not last.strip() or not phone.strip():
                    st.warning("First name, last name and phone are required.")
                else:
                    try:
                        repo.add_patient((first.strip(),last.strip(),dob,gender,phone.strip(),email or None,blood or None,address or None,emergency or None))
                        done("Patient registered.")
                    except Exception as e: error(e)
    with t3:
        try:
            rows=repo.list_patients()
            if rows:
                opts={f'{x["patient_id"]} - {x["first_name"]} {x["last_name"]}':x for x in rows}
                label=st.selectbox("Select patient",list(opts)); p=opts[label]
                mode=st.radio("Operation",["Edit","Delete"],horizontal=True)
                if mode=="Edit":
                    with st.form("patient_edit"):
                        c1,c2=st.columns(2)
                        first=c1.text_input("First name",p["first_name"]); last=c2.text_input("Last name",p["last_name"])
                        dob=c1.date_input("Date of birth",p["date_of_birth"])
                        gender=c2.selectbox("Gender",["Male","Female","Other"],index=["Male","Female","Other"].index(p["gender"]))
                        phone=c1.text_input("Phone",p["phone"]); email=c2.text_input("Email",p["email"] or "")
                        bg=["","A+","A-","B+","B-","AB+","AB-","O+","O-"]
                        blood=c1.selectbox("Blood group",bg,index=bg.index(p["blood_group"] or ""))
                        address=c2.text_input("Address",p["address"] or "")
                        emergency=st.text_input("Emergency contact",p["emergency_contact"] or "")
                        if st.form_submit_button("Save changes",type="primary"):
                            try:
                                repo.update_patient(p["patient_id"],(first,last,dob,gender,phone,email or None,blood or None,address or None,emergency or None))
                                done("Patient updated.")
                            except Exception as e: error(e)
                else:
                    st.warning("Delete is permanent and may be blocked by existing appointments or bills.")
                    if st.button("Confirm patient deletion",type="primary"):
                        try: repo.delete_patient(p["patient_id"]); done("Patient deleted.")
                        except Exception as e: error(e)
            else: st.info("No patients available.")
        except Exception as e: error(e)

elif page=="Doctors":
    st.subheader("Doctor management")
    t1,t2,t3=st.tabs(["Directory","Add doctor","Edit doctor"])
    with t1:
        q=st.text_input("Search doctor or specialization")
        try: table(repo.list_doctors(q))
        except Exception as e: error(e)
    with t2:
        with st.form("doctor_add"):
            a,b=st.columns(2)
            first=a.text_input("First name*"); last=b.text_input("Last name*")
            gender=a.selectbox("Gender",["Female","Male","Other"]); phone=b.text_input("Phone")
            email=a.text_input("Email"); spec=b.text_input("Specialization*")
            fee=a.number_input("Consultation fee",min_value=0.0,step=50.0)
            hire=b.date_input("Hire date",date.today())
            if st.form_submit_button("Add doctor",type="primary"):
                if not first.strip() or not last.strip() or not spec.strip(): st.warning("Complete required fields.")
                else:
                    try: repo.add_doctor((first,last,gender,phone or None,email or None,spec,fee,hire,True)); done("Doctor added.")
                    except Exception as e: error(e)
    with t3:
        try:
            rows=repo.list_doctors()
            if rows:
                opts={f'{d["doctor_id"]} - {d["first_name"]} {d["last_name"]}':d for d in rows}
                d=opts[st.selectbox("Select doctor",list(opts))]
                with st.form("doctor_edit"):
                    a,b=st.columns(2)
                    first=a.text_input("First name",d["first_name"]); last=b.text_input("Last name",d["last_name"])
                    gender=a.selectbox("Gender",["Female","Male","Other"],index=["Female","Male","Other"].index(d["gender"]))
                    phone=b.text_input("Phone",d["phone"] or ""); email=a.text_input("Email",d["email"] or "")
                    spec=b.text_input("Specialization",d["specialization"])
                    fee=a.number_input("Consultation fee",min_value=0.0,value=float(d["consultation_fee"]))
                    hire=b.date_input("Hire date",d["hire_date"] or date.today())
                    active=st.checkbox("Active",bool(d["active"]))
                    if st.form_submit_button("Update doctor",type="primary"):
                        try: repo.update_doctor(d["doctor_id"],(first,last,gender,phone or None,email or None,spec,fee,hire,active)); done("Doctor updated.")
                        except Exception as e: error(e)
            else: st.info("No doctors found.")
        except Exception as e: error(e)

elif page=="Departments":
    st.subheader("Departments")
    try:
        table(repo.list_departments())
        with st.form("department_add"):
            name=st.text_input("Department name")
            a,b=st.columns(2); floor=a.number_input("Floor",min_value=0); phone=b.text_input("Phone")
            if st.form_submit_button("Add department",type="primary"):
                try: repo.add_department(name.strip(),int(floor),phone or None); done("Department added.")
                except Exception as e: error(e)
    except Exception as e: error(e)

elif page=="Appointments":
    st.subheader("Appointment management")
    t1,t2=st.tabs(["Appointment list","Book appointment"])
    with t1:
        q=st.text_input("Search patient, doctor or status")
        try:
            rows=repo.list_appointments(q); table(rows)
            if rows:
                opts={f'#{r["appointment_id"]} {r["patient"]} / {r["doctor"]}':r["appointment_id"] for r in rows}
                selected=opts[st.selectbox("Appointment to update",list(opts))]
                status=st.selectbox("New status",["Scheduled","Completed","Cancelled","No-Show"])
                if st.button("Update status",type="primary"):
                    repo.update_appointment_status(selected,status); done("Appointment status updated.")
        except Exception as e: error(e)
    with t2:
        try:
            with st.form("appointment_book"):
                patient=choose_patient(); doctor=choose_doctor()
                day=st.date_input("Date",date.today()); tm=st.time_input("Time",time(10,0))
                reason=st.text_input("Reason")
                if st.form_submit_button("Book appointment",type="primary"):
                    if patient is None or doctor is None: st.warning("Patient and doctor are required.")
                    else:
                        try: repo.book_appointment(patient,doctor,datetime.combine(day,tm),reason or None); done("Appointment booked.")
                        except Exception as e: error(e)
        except Exception as e: error(e)

elif page=="Rooms":
    st.subheader("Room management")
    try:
        table(repo.list_rooms())
        with st.expander("Add room"):
            with st.form("room_add"):
                number=st.text_input("Room number")
                kind=st.selectbox("Room type",["General","Semi-Private","Private","ICU"])
                charge=st.number_input("Daily charge",min_value=0.0,step=100.0)
                status=st.selectbox("Availability",["Available","Occupied","Maintenance"])
                if st.form_submit_button("Add room"):
                    try: repo.add_room(number,kind,charge,status); done("Room added.")
                    except Exception as e: error(e)
        rows=repo.list_rooms()
        if rows:
            opts={f'{r["room_number"]} (ID {r["room_id"]})':r["room_id"] for r in rows}
            rid=opts[st.selectbox("Room",list(opts))]
            status=st.selectbox("Set availability",["Available","Occupied","Maintenance"])
            if st.button("Update room"): repo.update_room_status(rid,status); done("Room updated.")
    except Exception as e: error(e)

elif page=="Services":
    st.subheader("Hospital services")
    try:
        table(repo.list_services())
        with st.form("service_add"):
            name=st.text_input("Service name"); desc=st.text_input("Description")
            charge=st.number_input("Standard charge",min_value=0.0,step=50.0)
            if st.form_submit_button("Add service"):
                try: repo.add_service(name,desc,charge); done("Service added.")
                except Exception as e: error(e)
    except Exception as e: error(e)

elif page=="Billing":
    st.subheader("Billing")
    t1,t2=st.tabs(["Bills","Create bill"])
    with t1:
        try: table(repo.list_bills())
        except Exception as e: error(e)
    with t2:
        try:
            with st.form("bill_create"):
                patient=choose_patient()
                due=st.date_input("Due date",date.today())
                discount=st.number_input("Discount",min_value=0.0,step=50.0)
                tax=st.number_input("Tax rate (%)",min_value=0.0,max_value=100.0,value=5.0)
                desc=st.text_input("Bill item description")
                qty=st.number_input("Quantity",min_value=1,value=1)
                price=st.number_input("Unit price",min_value=0.0,step=50.0)
                if st.form_submit_button("Create bill",type="primary"):
                    if patient is None or not desc.strip(): st.warning("Select a patient and enter a description.")
                    else:
                        try:
                            bill=repo.create_bill(patient,None,due,discount,tax,[(desc,int(qty),price)])
                            st.success(f"Bill #{bill} created."); st.rerun()
                        except Exception as e: error(e)
        except Exception as e: error(e)

elif page=="Payments":
    st.subheader("Payments")
    t1,t2=st.tabs(["Payment history","Record payment"])
    with t1:
        try: table(repo.list_payments())
        except Exception as e: error(e)
    with t2:
        try:
            bills=[b for b in repo.list_bills() if float(b["balance_amount"])>0]
            if bills:
                opts={f'Bill #{b["bill_id"]} | {b["patient_name"]} | ₹{float(b["balance_amount"]):,.2f} due':b for b in bills}
                with st.form("payment_add"):
                    label=st.selectbox("Outstanding bill",list(opts)); bill=opts[label]
                    amount=st.number_input("Payment amount",min_value=0.01,max_value=float(bill["balance_amount"]),step=100.0)
                    method=st.selectbox("Method",["Cash","Card","UPI","Net Banking","Insurance"])
                    ref=st.text_input("Transaction reference")
                    if st.form_submit_button("Record payment",type="primary"):
                        try: repo.add_payment(bill["bill_id"],amount,method,ref); done("Payment recorded.")
                        except Exception as e: error(e)
            else: st.info("No outstanding bills.")
        except Exception as e: error(e)

elif page=="Reports":
    st.subheader("Reports & analytics")
    choice=st.selectbox("Report",["Monthly revenue","Doctor appointment summary","Outstanding bills","Service usage","Patient appointment history"])
    try:
        if choice=="Monthly revenue":
            rows=repo.monthly_revenue(); table(rows)
            if rows:
                df=pd.DataFrame(rows); df["collected_revenue"]=pd.to_numeric(df["collected_revenue"])
                st.bar_chart(df.set_index("revenue_month")["collected_revenue"])
        elif choice=="Doctor appointment summary": table(repo.doctor_summary())
        elif choice=="Outstanding bills":
            rows=repo.outstanding_report(); table(rows)
            if rows:
                df=pd.DataFrame(rows); st.bar_chart(df.set_index("patient_name")["balance_amount"])
        elif choice=="Service usage": table(repo.service_report())
        else:
            patients=repo.patient_options()
            if patients:
                opts={f'{p["name"]} (#{p["patient_id"]})':p["patient_id"] for p in patients}
                pid=opts[st.selectbox("Patient",list(opts))]
                if st.button("Generate history"): table(repo.patient_history(pid))
            else: st.info("No patients available.")
    except Exception as e: error(e)
