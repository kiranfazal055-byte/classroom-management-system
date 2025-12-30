import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# ======================= PAGE CONFIG & BEAUTIFUL THEME =======================
st.set_page_config(page_title="Education Management System", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main .block-container { padding: 2rem; background: linear-gradient(to bottom, #f0f9ff, #e0f2fe); }
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6, #1d4ed8);
        color: white;
        border: none;
        border-radius: 12px;
        height: 3.2em;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 6px solid;
    }
    h1, h2, h3 { color: #1e293b; font-weight: 700; }
    .stDataFrame { border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 1.1rem;
        padding: 1rem 2rem;
        background: #f1f5f9;
        border-radius: 12px 12px 0 0;
        margin-right: 0.5rem;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #3b82f6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ======================= HEADER =======================
col1, col2 = st.columns([1, 8])
with col1:
    st.image("https://images.unsplash.com/photo-1524178232363-1fb2b075b655?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80", width=130)
with col2:
    st.markdown("<h1 style='margin-top: 35px; color: #1e293b;'>Education Management System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 1.2rem;'>Professional platform for students, teachers, courses, exams, grades & registrations</p>", unsafe_allow_html=True)

st.markdown("---")

# ======================= DATABASE =======================
conn = sqlite3.connect('classroom.db', check_same_thread=False)
cursor = conn.cursor()

# Tables (no department in courses, no course_id in exams/grades, no timetable)
cursor.execute('''CREATE TABLE IF NOT EXISTS departments (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    fee REAL NOT NULL,
    duration TEXT
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, subject TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, age INTEGER, gender TEXT, phone TEXT, email TEXT UNIQUE)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_name TEXT NOT NULL,
    exam_date TEXT NOT NULL,
    exam_time TEXT NOT NULL
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

# Success message with 2-second delay
def success_message(action, item):
    st.success(f"{item} {action} successfully!")
    time.sleep(2)
    st.rerun()

# ======================= SIDEBAR =======================
with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio("Select Section", [
        "Dashboard",
        "Students",
        "Teachers",
        "Courses",
        "Departments",
        "Exams",
        "Registration Form"
    ], label_visibility="collapsed")
    st.markdown("---")
    st.caption("Professional Education Platform • 2025")

# ======================= COLORFUL DASHBOARD =======================
if page == "Dashboard":
    st.header("System Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='metric-card' style='border-left-color: #3b82f6;'>", unsafe_allow_html=True)
        st.markdown("### 👥 Students")
        st.markdown(f"<h2 style='color: #3b82f6;'>{pd.read_sql('SELECT COUNT(*) FROM students', conn).iloc[0,0]}</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card' style='border-left-color: #10b981;'>", unsafe_allow_html=True)
        st.markdown("### 👩‍🏫 Teachers")
        st.markdown(f"<h2 style='color: #10b981;'>{pd.read_sql('SELECT COUNT(*) FROM teachers', conn).iloc[0,0]}</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-card' style='border-left-color: #f59e0b;'>", unsafe_allow_html=True)
        st.markdown("### 📚 Courses")
        st.markdown(f"<h2 style='color: #f59e0b;'>{pd.read_sql('SELECT COUNT(*) FROM courses', conn).iloc[0,0]}</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='metric-card' style='border-left-color: #ef4444;'>", unsafe_allow_html=True)
        st.markdown("### 🏢 Departments")
        st.markdown(f"<h2 style='color: #ef4444;'>{pd.read_sql('SELECT COUNT(*) FROM departments', conn).iloc[0,0]}</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='metric-card' style='border-left-color: #8b5cf6;'>", unsafe_allow_html=True)
        st.markdown("### 📝 Registrations")
        st.markdown(f"<h2 style='color: #8b5cf6;'>{pd.read_sql('SELECT COUNT(*) FROM registrations', conn).iloc[0,0]}</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card' style='border-left-color: #ec4899;'>", unsafe_allow_html=True)
        st.markdown("### 📅 Scheduled Exams")
        st.markdown(f"<h2 style='color: #ec4899;'>{pd.read_sql('SELECT COUNT(*) FROM exams', conn).iloc[0,0]}</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ======================= STUDENTS =======================
elif page == "Students":
    st.header("Student Management")

    tab_view, tab_add, tab_update, tab_search, tab_delete = st.tabs(["📋 View", "➕ Add", "✏️ Update", "🔍 Search", "🗑️ Delete"])

    with tab_view:
        df_students = pd.read_sql("SELECT id, name, email, phone, age, gender FROM students", conn)
        st.dataframe(df_students, use_container_width=True)

    with tab_add:
        with st.form("add_student"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
            with col2:
                age = st.number_input("Age", min_value=1)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            submitted = st.form_submit_button("Add Student")
            if submitted and name and email:
                try:
                    cursor.execute("INSERT INTO students (name, age, gender, phone, email) VALUES (?, ?, ?, ?, ?)", (name, age, gender, phone, email))
                    conn.commit()
                    success_message("added", "Student")
                except sqlite3.IntegrityError:
                    st.error("Email already exists.")

    with tab_update:
        df_students = pd.read_sql("SELECT id, name, email, phone, age, gender FROM students", conn)
        if not df_students.empty:
            student_id = st.selectbox("Select Student ID to Update", df_students['id'])
            current = df_students[df_students['id'] == student_id].iloc[0]
            with st.form("update_student"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Full Name", value=current['name'])
                    new_email = st.text_input("Email", value=current['email'])
                    new_phone = st.text_input("Phone", value=current['phone'])
                with col2:
                    new_age = st.number_input("Age", value=current['age'], min_value=1)
                    new_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(current['gender']))
                submitted = st.form_submit_button("Update Student")
                if submitted:
                    cursor.execute("UPDATE students SET name = ?, age = ?, gender = ?, phone = ?, email = ? WHERE id = ?", 
                                   (new_name, new_age, new_gender, new_phone, new_email, student_id))
                    conn.commit()
                    success_message("updated", "Student")

    with tab_search:
        search = st.text_input("Search by name, email, or phone")
        if search:
            df_search = pd.read_sql("SELECT id, name, email, phone, age, gender FROM students WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?", conn, params=(f"%{search}%", f"%{search}%", f"%{search}%"))
            st.dataframe(df_search, use_container_width=True)

    with tab_delete:
        df_students = pd.read_sql("SELECT id, name FROM students", conn)
        if not df_students.empty:
            student_id = st.selectbox("Select Student ID to Delete", df_students['id'])
            student_name = df_students[df_students['id'] == student_id]['name'].iloc[0]
            if st.button("🛑 Permanently Delete", type="primary"):
                cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
                cursor.execute("DELETE FROM registrations WHERE student_id = ?", (student_id,))
                cursor.execute("DELETE FROM grades WHERE student_id = ?", (student_id,))
                conn.commit()
                success_message("deleted", f"Student ({student_name})")

# ======================= TEACHERS =======================
elif page == "Teachers":
    st.header("Teacher Management")

    tab_view, tab_add, tab_update, tab_search, tab_delete = st.tabs(["📋 View", "➕ Add", "✏️ Update", "🔍 Search", "🗑️ Delete"])

    with tab_view:
        df_teachers = pd.read_sql("SELECT id, name, subject FROM teachers", conn)
        st.dataframe(df_teachers, use_container_width=True)

    with tab_add:
        with st.form("add_teacher"):
            name = st.text_input("Teacher Name")
            subject = st.text_input("Subject Taught")
            submitted = st.form_submit_button("Add Teacher")
            if submitted and name:
                cursor.execute("INSERT INTO teachers (name, subject) VALUES (?, ?)", (name, subject))
                conn.commit()
                success_message("added", "Teacher")

    with tab_update:
        df_teachers = pd.read_sql("SELECT id, name, subject FROM teachers", conn)
        if not df_teachers.empty:
            teacher_id = st.selectbox("Select Teacher ID to Update", df_teachers['id'])
            current = df_teachers[df_teachers['id'] == teacher_id].iloc[0]
            with st.form("update_teacher"):
                new_name = st.text_input("Name", value=current['name'])
                new_subject = st.text_input("Subject", value=current['subject'])
                submitted = st.form_submit_button("Update Teacher")
                if submitted:
                    cursor.execute("UPDATE teachers SET name = ?, subject = ? WHERE id = ?", (new_name, new_subject, teacher_id))
                    conn.commit()
                    success_message("updated", "Teacher")

    with tab_search:
        search = st.text_input("Search by name or subject")
        if search:
            df_search = pd.read_sql("SELECT id, name, subject FROM teachers WHERE name LIKE ? OR subject LIKE ?", conn, params=(f"%{search}%", f"%{search}%"))
            st.dataframe(df_search, use_container_width=True)

    with tab_delete:
        df_teachers = pd.read_sql("SELECT id, name FROM teachers", conn)
        if not df_teachers.empty:
            teacher_id = st.selectbox("Select Teacher ID to Delete", df_teachers['id'])
            teacher_name = df_teachers[df_teachers['id'] == teacher_id]['name'].iloc[0]
            if st.button("🛑 Permanently Delete", type="primary"):
                cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
                conn.commit()
                success_message("deleted", f"Teacher ({teacher_name})")

# ======================= COURSES (NO DEPARTMENT COLUMN) =======================
elif page == "Courses":
    st.header("Course Management")

    tab_view, tab_add, tab_update, tab_search, tab_delete = st.tabs(["📋 View", "➕ Add", "✏️ Update", "🔍 Search", "🗑️ Delete"])

    with tab_view:
        df_courses = pd.read_sql("SELECT id, name, fee, duration FROM courses", conn)
        st.dataframe(df_courses, use_container_width=True)

    with tab_add:
        with st.form("add_course"):
            name = st.text_input("Course Name")
            fee = st.number_input("Course Fee", min_value=0.0)
            duration = st.text_input("Course Duration (e.g., 3 months)")
            submitted = st.form_submit_button("Add Course")
            if submitted and name:
                cursor.execute("INSERT INTO courses (name, fee, duration) VALUES (?, ?, ?)", (name, fee, duration))
                conn.commit()
                success_message("added", "Course")

    with tab_update:
        df_courses = pd.read_sql("SELECT id, name, fee, duration FROM courses", conn)
        if not df_courses.empty:
            course_id = st.selectbox("Select Course ID to Update", df_courses['id'])
            current = df_courses[df_courses['id'] == course_id].iloc[0]
            with st.form("update_course"):
                new_name = st.text_input("Course Name", value=current['name'])
                new_fee = st.number_input("Fee", value=float(current['fee']))
                new_duration = st.text_input("Duration", value=current['duration'] or "")
                submitted = st.form_submit_button("Update Course")
                if submitted:
                    cursor.execute("UPDATE courses SET name = ?, fee = ?, duration = ? WHERE id = ?", (new_name, new_fee, new_duration, course_id))
                    conn.commit()
                    success_message("updated", "Course")

    with tab_search:
        search = st.text_input("Search by name")
        if search:
            df_search = pd.read_sql("SELECT id, name, fee, duration FROM courses WHERE name LIKE ?", conn, params=(f"%{search}%",))
            st.dataframe(df_search, use_container_width=True)

    with tab_delete:
        df_courses = pd.read_sql("SELECT id, name FROM courses", conn)
        if not df_courses.empty:
            course_id = st.selectbox("Select Course ID to Delete", df_courses['id'])
            course_name = df_courses[df_courses['id'] == course_id]['name'].iloc[0]
            if st.button("🛑 Permanently Delete", type="primary"):
                cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
                conn.commit()
                success_message("deleted", f"Course ({course_name})")

# ======================= DEPARTMENTS =======================
elif page == "Departments":
    st.header("Department Management")

    tab_view, tab_add, tab_update, tab_search, tab_delete = st.tabs(["📋 View", "➕ Add", "✏️ Update", "🔍 Search", "🗑️ Delete"])

    with tab_view:
        df_depts = pd.read_sql("SELECT id, name FROM departments", conn)
        st.dataframe(df_depts, use_container_width=True)

    with tab_add:
        with st.form("add_dept"):
            name = st.text_input("Department Name")
            submitted = st.form_submit_button("Add Department")
            if submitted and name:
                try:
                    cursor.execute("INSERT INTO departments (name) VALUES (?)", (name,))
                    conn.commit()
                    success_message("added", "Department")
                except sqlite3.IntegrityError:
                    st.error("Department already exists.")

    with tab_update:
        df_depts = pd.read_sql("SELECT id, name FROM departments", conn)
        if not df_depts.empty:
            dept_id = st.selectbox("Select Department ID to Update", df_depts['id'])
            current = df_depts[df_depts['id'] == dept_id].iloc[0]
            new_name = st.text_input("Department Name", value=current['name'])
            if st.button("Update Department"):
                cursor.execute("UPDATE departments SET name = ? WHERE id = ?", (new_name, dept_id))
                conn.commit()
                success_message("updated", "Department")

    with tab_search:
        search = st.text_input("Search by name")
        if search:
            df_search = pd.read_sql("SELECT id, name FROM departments WHERE name LIKE ?", conn, params=(f"%{search}%",))
            st.dataframe(df_search, use_container_width=True)

    with tab_delete:
        df_depts = pd.read_sql("SELECT id, name FROM departments", conn)
        if not df_depts.empty:
            dept_id = st.selectbox("Select Department ID to Delete", df_depts['id'])
            dept_name = df_depts[df_depts['id'] == dept_id]['name'].iloc[0]
            if st.button("🛑 Permanently Delete", type="primary"):
                cursor.execute("DELETE FROM departments WHERE id = ?", (dept_id,))
                conn.commit()
                success_message("deleted", f"Department ({dept_name})")

# ======================= EXAMS (NO COURSE_ID) =======================
elif page == "Exams":
    st.header("Exam Management")

    tab_view, tab_add, tab_update, tab_search, tab_delete = st.tabs(["📝 View", "➕ Add", "✏️ Update", "🔍 Search", "🗑️ Delete"])

    with tab_view:
        df_exams = pd.read_sql("SELECT id, exam_name, exam_date, exam_time FROM exams", conn)
        st.dataframe(df_exams, use_container_width=True)

    with tab_add:
        with st.form("add_exam"):
            exam_name = st.text_input("Exam Name")
            exam_date = st.date_input("Exam Date")
            exam_time = st.text_input("Exam Time")
            submitted = st.form_submit_button("Add Exam")
            if submitted and exam_name:
                cursor.execute("INSERT INTO exams (exam_name, exam_date, exam_time) VALUES (?, ?, ?)", (exam_name, str(exam_date), exam_time))
                conn.commit()
                success_message("added", "Exam")

    with tab_update:
        df_exams = pd.read_sql("SELECT id, exam_name, exam_date, exam_time FROM exams", conn)
        if not df_exams.empty:
            exam_id = st.selectbox("Select Exam ID to Update", df_exams['id'])
            current = df_exams[df_exams['id'] == exam_id].iloc[0]
            with st.form("update_exam"):
                new_name = st.text_input("Exam Name", value=current['exam_name'])
                new_date = st.date_input("Exam Date", value=datetime.strptime(current['exam_date'], "%Y-%m-%d"))
                new_time = st.text_input("Exam Time", value=current['exam_time'])
                submitted = st.form_submit_button("Update Exam")
                if submitted:
                    cursor.execute("UPDATE exams SET exam_name = ?, exam_date = ?, exam_time = ? WHERE id = ?", (new_name, str(new_date), new_time, exam_id))
                    conn.commit()
                    success_message("updated", "Exam")

    with tab_search:
        search = st.text_input("Search by exam name")
        if search:
            df_search = pd.read_sql("SELECT id, exam_name, exam_date, exam_time FROM exams WHERE exam_name LIKE ?", conn, params=(f"%{search}%",))
            st.dataframe(df_search, use_container_width=True)

    with tab_delete:
        df_exams = pd.read_sql("SELECT id, exam_name FROM exams", conn)
        if not df_exams.empty:
            exam_id = st.selectbox("Select Exam ID to Delete", df_exams['id'])
            exam_name = df_exams[df_exams['id'] == exam_id]['exam_name'].iloc[0]
            if st.button("🛑 Permanently Delete", type="primary"):
                cursor.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
                conn.commit()
                success_message("deleted", f"Exam ({exam_name})")

# ======================= REGISTRATION FORM =======================
elif page == "Registration Form":
    st.header("Student Registration Form")

    students = pd.read_sql("SELECT id, name FROM students", conn)
    teachers = pd.read_sql("SELECT id, name FROM teachers", conn)
    courses = pd.read_sql("SELECT id, name, fee FROM courses", conn)

    if students.empty or teachers.empty or courses.empty:
        st.warning("Please add students, teachers, and courses first.")
    else:
        with st.form("registration_form"):
            st.subheader("Register Student in Course")
            student_name = st.selectbox("Select Student", students['name'].tolist())
            teacher_name = st.selectbox("Select Teacher", teachers['name'].tolist())
            course_name = st.selectbox("Select Course", courses['name'].tolist())

            selected_course = courses[courses['name'] == course_name].iloc[0]
            st.info(f"**Course Fee:** ${selected_course['fee']:.2f}")

            submitted = st.form_submit_button("Complete Registration")
            if submitted:
                student_id = students[students['name'] == student_name]['id'].iloc[0]
                teacher_id = teachers[teachers['name'] == teacher_name]['id'].iloc[0]
                course_id = selected_course['id']

                cursor.execute("INSERT INTO registrations (student_id, teacher_id, course_id, registration_date) VALUES (?, ?, ?, ?)",
                               (student_id, teacher_id, course_id, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                success_message("completed", "Registration")
   # Current Registrations - FIXED DISPLAY
    st.subheader("Current Registrations")
    df_reg = pd.read_sql('''
        SELECT r.id, s.name AS student, t.name AS teacher, c.name AS course, c.fee, r.registration_date
        FROM registrations r
        LEFT JOIN students s ON r.student_id = s.id
        LEFT JOIN teachers t ON r.teacher_id = t.id
        LEFT JOIN courses c ON r.course_id = c.id
    ''', conn)
    if df_reg.empty or df_reg['student'].isna().all():
        st.info("No registrations yet. Use the form above to add one.")
    else:
        st.dataframe(df_reg.dropna(subset=['student']), use_container_width=True)

    if st.button("Refresh Registrations"):
        st.rerun()
    tab_view, tab_add, tab_update, tab_search, tab_delete = st.tabs(["📋 View", "➕ Add", "✏️ Update", "🔍 Search", "🗑️ Delete"])

    # Load lookup tables
    students = pd.read_sql("SELECT id, name FROM students", conn)
    teachers = pd.read_sql("SELECT id, name FROM teachers", conn)
    courses = pd.read_sql("SELECT id, name, fee FROM courses", conn)

  with tab_view:
    df_grades = pd.read_sql('''
        SELECT g.id, s.name AS student, g.grade, g.remarks
        FROM grades g
        LEFT JOIN students s ON g.student_id = s.id
    ''', conn)
    if df_grades.empty or df_grades['student'].isna().all():
        st.info("No grades added yet.")
    else:
        st.dataframe(df_grades.dropna(subset=['student']), use_container_width=True)
    with tab_add:
        if students.empty or teachers.empty or courses.empty:
            st.warning("Please add students, teachers, and courses first.")
        else:
            with st.form("add_registration"):
                student_name = st.selectbox("Select Student", students['name'].tolist())
                teacher_name = st.selectbox("Select Teacher", teachers['name'].tolist())
                course_name = st.selectbox("Select Course", courses['name'].tolist())

                selected_course = courses[courses['name'] == course_name].iloc[0]
                st.info(f"**Course Fee:** ${selected_course['fee']:.2f}")

                submitted = st.form_submit_button("Add Registration")
                if submitted:
                    student_id = students[students['name'] == student_name]['id'].iloc[0]
                    teacher_id = teachers[teachers['name'] == teacher_name]['id'].iloc[0]
                    course_id = selected_course['id']

                    cursor.execute("INSERT INTO registrations (student_id, teacher_id, course_id, registration_date) VALUES (?, ?, ?, ?)",
                                   (student_id, teacher_id, course_id, datetime.now().strftime("%Y-%m-%d")))
                    conn.commit()
                    success_message("added", "Registration")

    with tab_update:
        df_reg = pd.read_sql('''
            SELECT r.id, s.name AS student, t.name AS teacher, c.name AS course, r.registration_date
            FROM registrations r
            LEFT JOIN students s ON r.student_id = s.id
            LEFT JOIN teachers t ON r.teacher_id = t.id
            LEFT JOIN courses c ON r.course_id = c.id
        ''', conn)
        if not df_reg.empty:
            reg_id = st.selectbox("Select Registration ID to Update", df_reg['id'])
            current = df_reg[df_reg['id'] == reg_id].iloc[0]
            with st.form("update_registration"):
                new_student = st.selectbox("Student", students['name'].tolist(), index=students[students['name'] == current['student']].index[0])
                new_teacher = st.selectbox("Teacher", teachers['name'].tolist(), index=teachers[teachers['name'] == current['teacher']].index[0])
                new_course = st.selectbox("Course", courses['name'].tolist(), index=courses[courses['name'] == current['course']].index[0])
                submitted = st.form_submit_button("Update Registration")
                if submitted:
                    new_s_id = students[students['name'] == new_student]['id'].iloc[0]
                    new_t_id = teachers[teachers['name'] == new_teacher]['id'].iloc[0]
                    new_c_id = courses[courses['name'] == new_course]['id'].iloc[0]
                    cursor.execute("UPDATE registrations SET student_id = ?, teacher_id = ?, course_id = ? WHERE id = ?", (new_s_id, new_t_id, new_c_id, reg_id))
                    conn.commit()
                    success_message("updated", "Registration")

    with tab_search:
        search = st.text_input("Search by student, teacher, or course")
        if search:
            df_search = pd.read_sql('''
                SELECT r.id, s.name AS student, t.name AS teacher, c.name AS course, c.fee, r.registration_date
                FROM registrations r
                LEFT JOIN students s ON r.student_id = s.id
                LEFT JOIN teachers t ON r.teacher_id = t.id
                LEFT JOIN courses c ON r.course_id = c.id
                WHERE s.name LIKE ? OR t.name LIKE ? OR c.name LIKE ?
            ''', conn, params=(f"%{search}%", f"%{search}%", f"%{search}%"))
            st.dataframe(df_search, use_container_width=True)

    with tab_delete:
        df_reg = pd.read_sql("SELECT id FROM registrations", conn)
        if not df_reg.empty:
            reg_id = st.selectbox("Select Registration ID to Delete", df_reg['id'])
            if st.button("🛑 Permanently Delete", type="primary"):
                cursor.execute("DELETE FROM registrations WHERE id = ?", (reg_id,))
                conn.commit()
                success_message("deleted", "Registration")




  


           

 

