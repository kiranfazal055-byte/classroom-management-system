import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ======================= PAGE CONFIG & BEAUTIFUL THEME =======================
st.set_page_config(page_title="Education Management System", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main .block-container { padding: 2rem; background: linear-gradient(to bottom, #f8fafc, #f1f5f9); }
    .stButton > button {
        background: linear-gradient(90deg, #4f46e5, #7c3aed);
        color: white;
        border: none;
        border-radius: 12px;
        height: 3.2em;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.4);
    }
    .card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
        border-left: 5px solid #4f46e5;
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
        background: #4f46e5;
        color: white;
    }
    .success-msg { background: #ecfdf5; color: #065f46; padding: 1rem; border-radius: 12px; border-left: 5px solid #10b981; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ======================= HEADER =======================
col1, col2 = st.columns([1, 8])
with col1:
    st.image("https://images.unsplash.com/photo-1524178232363-1fb2b075b655?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80", width=130)
with col2:
    st.markdown("<h1 style='margin-top: 35px; color: #1e293b;'>Education Management System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 1.2rem;'>Complete platform for managing students, teachers, courses, departments, timetable, exams, grades & registrations</p>", unsafe_allow_html=True)

st.markdown("---")

# ======================= DATABASE =======================
conn = sqlite3.connect('classroom.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS departments (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department_id INTEGER,
    fee REAL NOT NULL,
    duration TEXT,
    FOREIGN KEY(department_id) REFERENCES departments(id)
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, subject TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, age INTEGER, gender TEXT, phone TEXT, email TEXT UNIQUE)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS timetable (id INTEGER PRIMARY KEY AUTOINCREMENT, course_id INTEGER, day TEXT NOT NULL, time_slot TEXT NOT NULL, FOREIGN KEY(course_id) REFERENCES courses(id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS exams (id INTEGER PRIMARY KEY AUTOINCREMENT, course_id INTEGER, exam_name TEXT NOT NULL, exam_date TEXT NOT NULL, exam_time TEXT NOT NULL, FOREIGN KEY(course_id) REFERENCES courses(id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, course_id INTEGER, grade REAL NOT NULL, remarks TEXT, FOREIGN KEY(student_id) REFERENCES students(id), FOREIGN KEY(course_id) REFERENCES courses(id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS registrations (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, teacher_id INTEGER, course_id INTEGER, registration_date TEXT, FOREIGN KEY(student_id) REFERENCES students(id), FOREIGN KEY(teacher_id) REFERENCES teachers(id), FOREIGN KEY(course_id) REFERENCES courses(id))''')
conn.commit()

# Success message
def success_message(action, item):
    st.markdown(f"<div class='success-msg'><strong>Success!</strong> {item} {action} successfully!</div>", unsafe_allow_html=True)

# ======================= SIDEBAR - CORRECT ORDER =======================
with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio("Select Section", [
        "Dashboard",
        "Students",
        "Teachers",
        "Courses",
        "Departments",
        "Timetable",
        "Exams",
        "Grades",
        "Registration Form"
    ], label_visibility="collapsed")
    st.markdown("---")
    st.caption("Professional Education Platform • 2025")

# ======================= DASHBOARD =======================
if page == "Dashboard":
    st.header("System Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Students", pd.read_sql("SELECT COUNT(*) FROM students", conn).iloc[0,0])
    col2.metric("Teachers", pd.read_sql("SELECT COUNT(*) FROM teachers", conn).iloc[0,0])
    col3.metric("Courses", pd.read_sql("SELECT COUNT(*) FROM courses", conn).iloc[0,0])
    col4.metric("Departments", pd.read_sql("SELECT COUNT(*) FROM departments", conn).iloc[0,0])
    st.metric("Registrations", pd.read_sql("SELECT COUNT(*) FROM registrations", conn).iloc[0,0])
    st.metric("Scheduled Exams", pd.read_sql("SELECT COUNT(*) FROM exams", conn).iloc[0,0])

# ======================= STUDENTS =======================
elif page == "Students":
    st.header("Student Management")

    tab_view, tab_add, tab_update, tab_search, tab_delete = st.tabs(["📋 View", "➕ Add", "✏️ Update", "🔍 Search", "🗑️ Delete"])

    with tab_view:
        df_students = pd.read_sql("SELECT id, name, email, phone, age, gender FROM students", conn)
        st.dataframe(df_students, use_container_width=True)
        if st.button("➕ Add New Student", use_container_width=True):
            st.rerun()

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
                    st.rerun()
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
                    st.rerun()
        else:
            st.info("No students to update.")

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
                conn.commit()
                success_message("deleted", f"Student ({student_name})")
                st.rerun()

# ======================= TEACHERS =======================
elif page == "Teachers":
    st.header("Teacher Management")

    tab_view, tab_add, tab_update, tab_search, tab_delete = st.tabs(["📋 View", "➕ Add", "✏️ Update", "🔍 Search", "🗑️ Delete"])

    with tab_view:
        df_teachers = pd.read_sql("SELECT id, name, subject FROM teachers", conn)
        st.dataframe(df_teachers, use_container_width=True)
        if st.button("➕ Add New Teacher", use_container_width=True):
            st.rerun()

    with tab_add:
        with st.form("add_teacher"):
            name = st.text_input("Teacher Name")
            subject = st.text_input("Subject Taught")
            submitted = st.form_submit_button("Add Teacher")
            if submitted and name:
                cursor.execute("INSERT INTO teachers (name, subject) VALUES (?, ?)", (name, subject))
                conn.commit()
                success_message("added", "Teacher")
                st.rerun()

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
                    st.rerun()
        else:
            st.info("No teachers to update.")

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
                st.rerun()

# ======================= COURSES =======================
elif page == "Courses":
    st.header("Course Management")

    tab_view, tab_add, tab_update, tab_search, tab_delete = st.tabs(["📋 View", "➕ Add", "✏️ Update", "🔍 Search", "🗑️ Delete"])

    with tab_view:
        df_courses = pd.read_sql('''
            SELECT c.id, c.name, d.name AS department, c.fee, c.duration
            FROM courses c LEFT JOIN departments d ON c.department_id = d.id
        ''', conn)
        st.dataframe(df_courses, use_container_width=True)
        if st.button("➕ Add New Course", use_container_width=True):
            st.rerun()

    with tab_add:
        depts = pd.read_sql("SELECT id, name FROM departments", conn)
        with st.form("add_course"):
            name = st.text_input("Course Name")
            dept = st.selectbox("Department", depts['name'].tolist()) if not depts.empty else st.warning("Add department first")
            fee = st.number_input("Course Fee", min_value=0.0)
            duration = st.text_input("Course Duration (e.g., 3 months)")
            submitted = st.form_submit_button("Add Course")
            if submitted and name and not depts.empty:
                dept_id = depts[depts['name'] == dept]['id'].iloc[0]
                cursor.execute("INSERT INTO courses (name, department_id, fee, duration) VALUES (?, ?, ?, ?)", (name, dept_id, fee, duration))
                conn.commit()
                success_message("added", "Course")
                st.rerun()

    with tab_update:
        df_courses = pd.read_sql('''
            SELECT c.id, c.name, d.name AS department, c.fee, c.duration
            FROM courses c LEFT JOIN departments d ON c.department_id = d.id
        ''', conn)
        if not df_courses.empty:
            course_id = st.selectbox("Select Course ID to Update", df_courses['id'])
            current = df_courses[df_courses['id'] == course_id].iloc[0]
            depts = pd.read_sql("SELECT id, name FROM departments", conn)
            with st.form("update_course"):
                new_name = st.text_input("Course Name", value=current['name'])
                new_dept = st.selectbox("Department", depts['name'].tolist(), index=depts[depts['name'] == current['department']].index[0] if current['department'] else 0)
                new_fee = st.number_input("Fee", value=float(current['fee']))
                new_duration = st.text_input("Duration", value=current['duration'] or "")
                submitted = st.form_submit_button("Update Course")
                if submitted:
                    new_dept_id = depts[depts['name'] == new_dept]['id'].iloc[0]
                    cursor.execute("UPDATE courses SET name = ?, department_id = ?, fee = ?, duration = ? WHERE id = ?", (new_name, new_dept_id, new_fee, new_duration, course_id))
                    conn.commit()
                    success_message("updated", "Course")
                    st.rerun()
        else:
            st.info("No courses to update.")

    with tab_search:
        search = st.text_input("Search by name")
        if search:
            df_search = pd.read_sql('''
                SELECT c.id, c.name, d.name AS department, c.fee, c.duration
                FROM courses c LEFT JOIN departments d ON c.department_id = d.id
                WHERE c.name LIKE ?
            ''', conn, params=(f"%{search}%",))
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
                st.rerun()

# ======================= DEPARTMENTS =======================
elif page == "Departments":
    st.header("Department Management")

    tab_view, tab_add, tab_update, tab_search, tab_delete = st.tabs(["📋 View", "➕ Add", "✏️ Update", "🔍 Search", "🗑️ Delete"])

    with tab_view:
        df_depts = pd.read_sql("SELECT id, name FROM departments", conn)
        st.dataframe(df_depts, use_container_width=True)
        if st.button("➕ Add New Department", use_container_width=True):
            st.rerun()

    with tab_add:
        with st.form("add_dept"):
            name = st.text_input("Department Name")
            submitted = st.form_submit_button("Add Department")
            if submitted and name:
                try:
                    cursor.execute("INSERT INTO departments (name) VALUES (?)", (name,))
                    conn.commit()
                    success_message("added", "Department")
                    st.rerun()
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
                st.rerun()
        else:
            st.info("No departments to update.")

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
                st.rerun()

# ======================= TIMETABLE =======================
elif page == "Timetable":
    st.header("Timetable Management")

    tab_view, tab_add, tab_update, tab_search, tab_delete = st.tabs(["📅 View", "➕ Add", "✏️ Update", "🔍 Search", "🗑️ Delete"])

    with tab_view:
        df_timetable = pd.read_sql('''
            SELECT t.id, c.name AS course, t.day, t.time_slot
            FROM timetable t JOIN courses c ON t.course_id = c.id
        ''', conn)
        st.dataframe(df_timetable, use_container_width=True)
        if st.button("➕ Add New Schedule", use_container_width=True):
            st.rerun()

    with tab_add:
        courses = pd.read_sql("SELECT id, name FROM courses", conn)
        if courses.empty:
            st.warning("Add courses first.")
        else:
            with st.form("add_timetable"):
                course = st.selectbox("Course", courses['name'])
                day = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                time_slot = st.text_input("Time Slot (e.g., 9:00 AM - 11:00 AM)")
                submitted = st.form_submit_button("Add Schedule")
                if submitted:
                    course_id = courses[courses['name'] == course]['id'].iloc[0]
                    cursor.execute("INSERT INTO timetable (course_id, day, time_slot) VALUES (?, ?, ?)", (course_id, day, time_slot))
                    conn.commit()
                    success_message("added", "Timetable entry")
                    st.rerun()

    with tab_update:
        df_timetable = pd.read_sql('''
            SELECT t.id, c.name AS course, t.day, t.time_slot
            FROM timetable t JOIN courses c ON t.course_id = c.id
        ''', conn)
        if not df_timetable.empty:
            entry_id = st.selectbox("Select Entry ID to Update", df_timetable['id'])
            current = df_timetable[df_timetable['id'] == entry_id].iloc[0]
            courses = pd.read_sql("SELECT id, name FROM courses", conn)
            with st.form("update_timetable"):
                new_course = st.selectbox("Course", courses['name'], index=courses[courses['name'] == current['course']].index[0])
                new_day = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], index=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(current['day']))
                new_time = st.text_input("Time Slot", value=current['time_slot'])
                submitted = st.form_submit_button("Update Schedule")
                if submitted:
                    new_course_id = courses[courses['name'] == new_course]['id'].iloc[0]
                    cursor.execute("UPDATE timetable SET course_id = ?, day = ?, time_slot = ? WHERE id = ?", (new_course_id, new_day, new_time, entry_id))
                    conn.commit()
                    success_message("updated", "Timetable entry")
                    st.rerun()
        else:
            st.info("No timetable entries to update.")

    with tab_search:
        search = st.text_input("Search by course or day")
        if search:
            df_search = pd.read_sql('''
                SELECT t.id, c.name AS course, t.day, t.time_slot
                FROM timetable t JOIN courses c ON t.course_id = c.id
                WHERE c.name LIKE ? OR t.day LIKE ?
            ''', conn, params=(f"%{search}%", f"%{search}%"))
            st.dataframe(df_search, use_container_width=True)

    with tab_delete:
        df_timetable = pd.read_sql("SELECT id FROM timetable", conn)
        if not df_timetable.empty:
            entry_id = st.selectbox("Select Entry ID to Delete", df_timetable['id'])
            if st.button("🛑 Permanently Delete", type="primary"):
                cursor.execute("DELETE FROM timetable WHERE id = ?", (entry_id,))
                conn.commit()
                success_message("deleted", "Timetable entry")
                st.rerun()

# ======================= EXAMS =======================
elif page == "Exams":
    st.header("Exam Management")

    tab_view, tab_add, tab_update, tab_search, tab_delete = st.tabs(["📝 View", "➕ Add", "✏️ Update", "🔍 Search", "🗑️ Delete"])

    with tab_view:
        df_exams = pd.read_sql('''
            SELECT e.id, c.name AS course, e.exam_name, e.exam_date, e.exam_time
            FROM exams e JOIN courses c ON e.course_id = c.id
        ''', conn)
        st.dataframe(df_exams, use_container_width=True)
        if st.button("➕ Add New Exam", use_container_width=True):
            st.rerun()

    with tab_add:
        courses = pd.read_sql("SELECT id, name FROM courses", conn)
        if courses.empty:
            st.warning("Add courses first.")
        else:
            with st.form("add_exam"):
                course = st.selectbox("Course", courses['name'])
                exam_name = st.text_input("Exam Name")
                exam_date = st.date_input("Exam Date")
                exam_time = st.text_input("Exam Time")
                submitted = st.form_submit_button("Add Exam")
                if submitted:
                    course_id = courses[courses['name'] == course]['id'].iloc[0]
                    cursor.execute("INSERT INTO exams (course_id, exam_name, exam_date, exam_time) VALUES (?, ?, ?, ?)", (course_id, exam_name, str(exam_date), exam_time))
                    conn.commit()
                    success_message("added", "Exam")
                    st.rerun()

    with tab_update:
        df_exams = pd.read_sql('''
            SELECT e.id, c.name AS course, e.exam_name, e.exam_date, e.exam_time
            FROM exams e JOIN courses c ON e.course_id = c.id
        ''', conn)
        if not df_exams.empty:
            exam_id = st.selectbox("Select Exam ID to Update", df_exams['id'])
            current = df_exams[df_exams['id'] == exam_id].iloc[0]
            courses = pd.read_sql("SELECT id, name FROM courses", conn)
            with st.form("update_exam"):
                new_course = st.selectbox("Course", courses['name'], index=courses[courses['name'] == current['course']].index[0])
                new_name = st.text_input("Exam Name", value=current['exam_name'])
                new_date = st.date_input("Exam Date", value=datetime.strptime(current['exam_date'], "%Y-%m-%d"))
                new_time = st.text_input("Exam Time", value=current['exam_time'])
                submitted = st.form_submit_button("Update Exam")
                if submitted:
                    new_course_id = courses[courses['name'] == new_course]['id'].iloc[0]
                    cursor.execute("UPDATE exams SET course_id = ?, exam_name = ?, exam_date = ?, exam_time = ? WHERE id = ?", (new_course_id, new_name, str(new_date), new_time, exam_id))
                    conn.commit()
                    success_message("updated", "Exam")
                    st.rerun()
        else:
            st.info("No exams to update.")

    with tab_search:
        search = st.text_input("Search by course or exam name")
        if search:
            df_search = pd.read_sql('''
                SELECT e.id, c.name AS course, e.exam_name, e.exam_date, e.exam_time
                FROM exams e JOIN courses c ON e.course_id = c.id
                WHERE c.name LIKE ? OR e.exam_name LIKE ?
            ''', conn, params=(f"%{search}%", f"%{search}%"))
            st.dataframe(df_search, use_container_width=True)

    with tab_delete:
        df_exams = pd.read_sql("SELECT id FROM exams", conn)
        if not df_exams.empty:
            exam_id = st.selectbox("Select Exam ID to Delete", df_exams['id'])
            if st.button("🛑 Permanently Delete", type="primary"):
                cursor.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
                conn.commit()
                success_message("deleted", "Exam")
                st.rerun()

# ======================= GRADES =======================
elif page == "Grades":
    st.header("Grades Management")

    tab_view, tab_add, tab_update, tab_search, tab_delete = st.tabs(["📊 View", "➕ Add", "✏️ Update", "🔍 Search", "🗑️ Delete"])

    with tab_view:
        df_grades = pd.read_sql('''
            SELECT g.id, s.name AS student, c.name AS course, g.grade, g.remarks
            FROM grades g JOIN students s ON g.student_id = s.id JOIN courses c ON g.course_id = c.id
        ''', conn)
        st.dataframe(df_grades, use_container_width=True)
        if st.button("➕ Add New Grade", use_container_width=True):
            st.rerun()

    with tab_add:
        students = pd.read_sql("SELECT id, name FROM students", conn)
        courses = pd.read_sql("SELECT id, name FROM courses", conn)
        if students.empty or courses.empty:
            st.warning("Add students and courses first.")
        else:
            with st.form("add_grade"):
                student = st.selectbox("Student", students['name'])
                course = st.selectbox("Course", courses['name'])
                grade = st.number_input("Grade (0-100)", min_value=0.0, max_value=100.0)
                remarks = st.text_area("Remarks (optional)")
                submitted = st.form_submit_button("Add Grade")
                if submitted:
                    s_id = students[students['name'] == student]['id'].iloc[0]
                    c_id = courses[courses['name'] == course]['id'].iloc[0]
                    cursor.execute("INSERT INTO grades (student_id, course_id, grade, remarks) VALUES (?, ?, ?, ?)", (s_id, c_id, grade, remarks or None))
                    conn.commit()
                    success_message("added", "Grade")
                    st.rerun()

    with tab_update:
        df_grades = pd.read_sql('''
            SELECT g.id, s.name AS student, c.name AS course, g.grade, g.remarks
            FROM grades g JOIN students s ON g.student_id = s.id JOIN courses c ON g.course_id = c.id
        ''', conn)
        if not df_grades.empty:
            grade_id = st.selectbox("Select Grade ID to Update", df_grades['id'])
            current = df_grades[df_grades['id'] == grade_id].iloc[0]
            students = pd.read_sql("SELECT id, name FROM students", conn)
            courses = pd.read_sql("SELECT id, name FROM courses", conn)
            with st.form("update_grade"):
                new_student = st.selectbox("Student", students['name'], index=students[students['name'] == current['student']].index[0])
                new_course = st.selectbox("Course", courses['name'], index=courses[courses['name'] == current['course']].index[0])
                new_grade = st.number_input("Grade", value=float(current['grade']), min_value=0.0, max_value=100.0)
                new_remarks = st.text_area("Remarks", value=current['remarks'] or "")
                submitted = st.form_submit_button("Update Grade")
                if submitted:
                    new_s_id = students[students['name'] == new_student]['id'].iloc[0]
                    new_c_id = courses[courses['name'] == new_course]['id'].iloc[0]
                    cursor.execute("UPDATE grades SET student_id = ?, course_id = ?, grade = ?, remarks = ? WHERE id = ?", (new_s_id, new_c_id, new_grade, new_remarks, grade_id))
                    conn.commit()
                    success_message("updated", "Grade")
                    st.rerun()
        else:
            st.info("No grades to update.")

    with tab_search:
        search = st.text_input("Search by student or course")
        if search:
            df_search = pd.read_sql('''
                SELECT g.id, s.name AS student, c.name AS course, g.grade, g.remarks
                FROM grades g JOIN students s ON g.student_id = s.id JOIN courses c ON g.course_id = c.id
                WHERE s.name LIKE ? OR c.name LIKE ?
            ''', conn, params=(f"%{search}%", f"%{search}%"))
            st.dataframe(df_search, use_container_width=True)

    with tab_delete:
        df_grades = pd.read_sql("SELECT id FROM grades", conn)
        if not df_grades.empty:
            grade_id = st.selectbox("Select Grade ID to Delete", df_grades['id'])
            if st.button("🛑 Permanently Delete", type="primary"):
                cursor.execute("DELETE FROM grades WHERE id = ?", (grade_id,))
                conn.commit()
                success_message("deleted", "Grade")
                st.rerun()

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
        st.warning("Please add students, teachers, and courses first.")
    else:
        with st.form("registration_form"):
            st.subheader("Register Student in Course")
            student_name = st.selectbox("Select Student", students['name'].tolist())
            teacher_name = st.selectbox("Select Teacher", teachers['name'].tolist())
            course_name = st.selectbox("Select Course", courses['name'].tolist())

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
                success_message("completed", "Registration")
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

st.caption("Built with Streamlit • Beautiful & Professional Education Management • 2025")
  

        
     
              
      
             
               
              
               
  
