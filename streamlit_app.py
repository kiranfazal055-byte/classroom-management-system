import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ======================= PAGE CONFIG & PROFESSIONAL CSS =======================
st.set_page_config(
    page_title="Education Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main .block-container {
        padding: 2rem;
    }
    .stButton > button {
        border-radius: 10px;
        height: 3.2em;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .card {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #E5E7EB;
    }
    h1, h2, h3 {
        color: #111827;
        font-weight: 700;
    }
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ======================= HEADER =======================
col1, col2 = st.columns([1, 8])
with col1:
    st.image("https://images.unsplash.com/photo-1524178232363-1fb2b075b655?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80", width=120)
with col2:
    st.markdown("<h1 style='margin-top: 30px;'>Education Management System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7280;'>Manage departments, courses, teachers, students, and registrations professionally</p>", unsafe_allow_html=True)

st.markdown("---")

# ======================= DATABASE =======================
conn = sqlite3.connect('classroom.db', check_same_thread=False)
cursor = conn.cursor()

# Tables
cursor.execute('''CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department_id INTEGER,
    fee REAL NOT NULL,
    FOREIGN KEY(department_id) REFERENCES departments(id)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    subject TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    phone TEXT,
    dob TEXT,
    email TEXT UNIQUE
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    teacher_id INTEGER,
    course_id INTEGER,
    registration_date TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(teacher_id) REFERENCES teachers(id),
    FOREIGN KEY(course_id) REFERENCES courses(id)
)''')

conn.commit()

# ======================= SIDEBAR =======================
with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio(
        "Select Section",
        ["Dashboard", "Departments", "Courses", "Teachers", "Students", "Registration Form"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("Professional Education Platform • 2025")

# ======================= DASHBOARD =======================
if page == "Dashboard":
    st.header("System Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Departments", pd.read_sql("SELECT COUNT(*) FROM departments", conn).iloc[0,0])
    col2.metric("Courses", pd.read_sql("SELECT COUNT(*) FROM courses", conn).iloc[0,0])
    col3.metric("Teachers", pd.read_sql("SELECT COUNT(*) FROM teachers", conn).iloc[0,0])
    col4.metric("Students", pd.read_sql("SELECT COUNT(*) FROM students", conn).iloc[0,0])

    st.metric("Total Registrations", pd.read_sql("SELECT COUNT(*) FROM registrations", conn).iloc[0,0])

# ======================= DEPARTMENTS =======================
elif page == "Departments":
    st.header("Manage Departments")

    with st.expander("Add New Department"):
        with st.form("add_dept"):
            name = st.text_input("Department Name")
            submitted = st.form_submit_button("Add Department")
            if submitted and name:
                try:
                    cursor.execute("INSERT INTO departments (name) VALUES (?)", (name,))
                    conn.commit()
                    st.success("Department added!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Department already exists.")

    st.subheader("All Departments")
    df_depts = pd.read_sql("SELECT id, name FROM departments", conn)
    st.dataframe(df_depts, use_container_width=True)

    if not df_depts.empty and st.button("Refresh"):
        st.rerun()

# ======================= COURSES =======================
elif page == "Courses":
    st.header("Manage Courses")

    depts = pd.read_sql("SELECT id, name FROM departments", conn)

    with st.expander("Add New Course"):
        with st.form("add_course"):
            name = st.text_input("Course Name")
            dept = st.selectbox("Department", depts['name'].tolist()) if not depts.empty else st.warning("Add a department first")
            fee = st.number_input("Course Fee", min_value=0.0)
            submitted = st.form_submit_button("Add Course")
            if submitted and name and not depts.empty:
                dept_id = depts[depts['name'] == dept]['id'].iloc[0]
                cursor.execute("INSERT INTO courses (name, department_id, fee) VALUES (?, ?, ?)", (name, dept_id, fee))
                conn.commit()
                st.success("Course added!")
                st.rerun()

    st.subheader("All Courses")
    df_courses = pd.read_sql('''
        SELECT c.id, c.name, d.name AS department, c.fee
        FROM courses c JOIN departments d ON c.department_id = d.id
    ''', conn)
    st.dataframe(df_courses, use_container_width=True)

    if st.button("Refresh Courses"):
        st.rerun()

# ======================= TEACHERS =======================
elif page == "Teachers":
    st.header("Manage Teachers")

    with st.expander("Add New Teacher"):
        with st.form("add_teacher"):
            name = st.text_input("Teacher Name")
            subject = st.text_input("Subject Taught")
            submitted = st.form_submit_button("Add Teacher")
            if submitted and name:
                cursor.execute("INSERT INTO teachers (name, subject) VALUES (?, ?)", (name, subject))
                conn.commit()
                st.success("Teacher added!")
                st.rerun()

    st.subheader("All Teachers")
    df_teachers = pd.read_sql("SELECT id, name, subject FROM teachers", conn)
    st.dataframe(df_teachers, use_container_width=True)

    if st.button("Refresh Teachers"):
        st.rerun()

# ======================= STUDENTS =======================
with st.expander("Add New Student"):
    with st.form("add_student"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
        with col2:
            age = st.number_input("Age", min_value=1)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            dob = st.date_input(
                "Date of Birth",
                value=datetime(2000, 1, 1),
                min_value=datetime(1900, 1, 1),
                max_value=datetime(2100, 1, 1)
            )
        submitted = st.form_submit_button("Add Student")
        if submitted and name and email:
            try:
                cursor.execute("INSERT INTO students (name, age, gender, phone, dob, email) VALUES (?, ?, ?, ?, ?, ?)",
                               (name, age, gender, phone, str(dob), email))
                conn.commit()
                st.success("Student added!")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("Email already exists.")


# ======================= REGISTRATION FORM =======================
elif page == "Registration Form":
    st.header("Student Registration Form")

    students = pd.read_sql("SELECT id, name FROM students", conn)
    teachers = pd.read_sql("SELECT id, name FROM teachers", conn)
    courses = pd.read_sql('''
        SELECT c.id, c.name, d.name AS dept, c.fee
        FROM courses c JOIN departments d ON c.department_id = d.id
    ''', conn)

    if students.empty or teachers.empty or courses.empty:
        st.warning("Please add students, teachers, and courses first before registering.")
    else:
        with st.form("registration_form"):
            st.subheader("Register Student in Course")

            student_name = st.selectbox("Select Student", students['name'].tolist())
            teacher_name = st.selectbox("Select Teacher", teachers['name'].tolist())
            course_name = st.selectbox("Select Course", courses['name'].tolist())

            # Auto-fill department and fee
            selected_course = courses[courses['name'] == course_name].iloc[0]
            st.info(f"**Department:** {selected_course['dept']}")
            st.info(f"**Course Fee:** ${selected_course['fee']:.2f}")

            submitted = st.form_submit_button("Complete Registration")
            if submitted:
                student_id = students[students['name'] == student_name]['id'].iloc[0]
                teacher_id = teachers[teachers['name'] == teacher_name]['id'].iloc[0]
                course_id = selected_course['id']

                cursor.execute("INSERT INTO registrations (student_id, teacher_id, course_id, registration_date) VALUES (?, ?, ?, ?)",
                               (student_id, teacher_id, course_id, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                st.success(f"Registration complete! {student_name} enrolled in {course_name} under {teacher_name}.")
                st.balloons()

    st.subheader("Current Registrations")
    df_reg = pd.read_sql('''
        SELECT r.id, s.name AS student, t.name AS teacher, c.name AS course, d.name AS department, c.fee
        FROM registrations r
        JOIN students s ON r.student_id = s.id
        JOIN teachers t ON r.teacher_id = t.id
        JOIN courses c ON r.course_id = c.id
        JOIN departments d ON c.department_id = d.id
    ''', conn)
    st.dataframe(df_reg, use_container_width=True)

    if st.button("Refresh Registrations"):
        st.rerun()

st.caption("Built with Streamlit • Professional Education Management • 2025")


