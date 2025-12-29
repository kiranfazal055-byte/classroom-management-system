import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

# ======================= PAGE CONFIG & THEME =======================
st.set_page_config(
    page_title="Education Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Custom CSS
st.markdown("""
<style>
    /* Main container padding */
    .main .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-bottom: 4rem;
    }
    
    /* Buttons - clean and modern */
    .stButton > button {
        border-radius: 10px;
        height: 3.2em;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Card style for sections */
    .card {
        background-color: #FFFFFF;
        padding: 1.8rem;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #E5E7EB;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #111827;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    /* Dataframes */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #F9FAFB;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #1F2937;
    }
</style>
""", unsafe_allow_html=True)

# ======================= HEADER =======================
col1, col2 = st.columns([1, 8])
with col1:
    st.image("https://images.unsplash.com/photo-1524178232363-1fb2b075b655?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80", width=120)
with col2:
    st.markdown("<h1 style='margin-top: 30px; color: #111827;'>Education Management System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7280; font-size: 1.1rem;'>A modern platform for managing students, courses, departments, and fees</p>", unsafe_allow_html=True)

st.markdown("---")

# ======================= DATABASE SETUP =======================
conn = sqlite3.connect('classroom.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables
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

cursor.execute('''CREATE TABLE IF NOT EXISTS class_times (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER,
    time_slot TEXT,
    FOREIGN KEY(course_id) REFERENCES courses(id)
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
    teacher_name TEXT,
    course_id INTEGER,
    email TEXT UNIQUE NOT NULL,
    FOREIGN KEY(course_id) REFERENCES courses(id)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS enrollments (
    course_id INTEGER,
    student_id INTEGER,
    PRIMARY KEY(course_id, student_id)
)''')

conn.commit()

# ======================= SIDEBAR NAVIGATION =======================
with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio(
        "Go to",
        ["Dashboard", "Students", "Teachers", "Courses", "Departments"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("<p style='color: #6B7280; font-size: 0.9rem;'>Professional Education Platform<br>© 2025</p>", unsafe_allow_html=True)

# ======================= DASHBOARD =======================
if page == "Dashboard":
    st.header("Overview & Analytics")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_students = pd.read_sql("SELECT COUNT(*) FROM students", conn).iloc[0,0]
        st.metric("Total Students", total_students)
    with col2:
        total_teachers = pd.read_sql("SELECT COUNT(*) FROM teachers", conn).iloc[0,0]
        st.metric("Teachers", total_teachers)
    with col3:
        total_courses = pd.read_sql("SELECT COUNT(*) FROM courses", conn).iloc[0,0]
        st.metric("Active Courses", total_courses)
    with col4:
        total_depts = pd.read_sql("SELECT COUNT(*) FROM departments", conn).iloc[0,0]
        st.metric("Departments", total_depts)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Students per Course")
        df_enrollment = pd.read_sql('''
            SELECT c.name AS course, COUNT(e.student_id) AS students
            FROM courses c LEFT JOIN enrollments e ON c.id = e.course_id
            GROUP BY c.id ORDER BY students DESC
        ''', conn)
        if not df_enrollment.empty:
            fig = px.bar(df_enrollment, x='course', y='students', color='course',
                         color_discrete_sequence=px.colors.sequential.Plasma)
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No enrollment data yet.")

    with col2:
        st.subheader("Course Fee Distribution")
        df_fees = pd.read_sql("SELECT name AS course, fee FROM courses", conn)
        if not df_fees.empty:
            fig = px.pie(df_fees, names='course', values='fee', hole=0.4,
                         color_discrete_sequence=px.colors.sequential.Blues)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No courses added yet.")
    st.markdown("</div>", unsafe_allow_html=True)

# ======================= STUDENTS PAGE =======================
elif page == "Students":
    st.header("Student Management")

    # Add Student Card
    with st.expander("➕ Add New Student", expanded=False):
        courses_df = pd.read_sql("SELECT id, name, fee FROM courses", conn)
        if courses_df.empty:
            st.warning("Please add courses first in the Courses section.")
        else:
            course_options = dict(zip(courses_df['name'], courses_df['id']))
            with st.form("add_student_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Full Name")
                    email = st.text_input("Email Address")
                    phone = st.text_input("Phone Number")
                    age = st.number_input("Age", min_value=15, max_value=100)
                with col2:
                    gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
                    dob = st.date_input("Date of Birth")
                    teacher_name = st.text_input("Assigned Teacher")
                    selected_course = st.selectbox("Enroll in Course", options=list(course_options.keys()))

                submitted = st.form_submit_button("Add Student")
                if submitted:
                    if name and email and selected_course:
                        course_id = course_options[selected_course]
                        try:
                            cursor.execute("""INSERT INTO students 
                                (name, age, gender, phone, dob, teacher_name, course_id, email)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                (name, age, gender, phone, str(dob), teacher_name, course_id, email))
                            cursor.execute("INSERT OR IGNORE INTO enrollments (course_id, student_id) VALUES (?, ?)",
                                           (course_id, cursor.lastrowid))
                            conn.commit()
                            st.success(f"Student {name} added successfully!")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("Email already exists.")
                    else:
                        st.error("Please fill all required fields.")

    # Student List & Actions
    st.subheader("Current Students")
    df_students = pd.read_sql("""
        SELECT s.id, s.name, s.email, s.phone, s.age, s.gender, 
               c.name AS course, s.teacher_name
        FROM students s LEFT JOIN courses c ON s.course_id = c.id
    """, conn)

    if df_students.empty:
        st.info("No students enrolled yet.")
    else:
        st.dataframe(df_students.drop(columns=['id']), use_container_width=True)

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔄 Refresh List", use_container_width=True):
                st.rerun()

        # Search
        st.markdown("### Search Student")
        search = st.text_input("Search by name, email, or phone")
        if search:
            filtered = df_students[
                df_students['name'].str.contains(search, case=False) |
                df_students['email'].str.contains(search, case=False) |
                df_students['phone'].str.contains(search, case=False)
            ]
            st.dataframe(filtered.drop(columns=['id']), use_container_width=True)

        # Update & Delete (simple version - can expand)
        st.markdown("### Update or Delete")
        student_id = st.selectbox("Select Student ID", options=df_students['id'])
        if student_id:
            student = df_students[df_students['id'] == student_id].iloc[0]
            st.write(f"**Selected:** {student['name']} - {student['course'] or 'No course'}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Delete Student", type="secondary"):
                    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
                    cursor.execute("DELETE FROM enrollments WHERE student_id = ?", (student_id,))
                    conn.commit()
                    st.success("Student deleted.")
                    st.rerun()
            with col2:
                st.info("Update feature coming soon — or edit directly in DB for now.")

# Add similar clean, card-based layouts for Teachers, Courses, Departments pages if needed

st.markdown("---")
st.caption("Built with Streamlit • Modern Education Management • 2025")

      
