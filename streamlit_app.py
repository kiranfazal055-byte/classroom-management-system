import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(page_title="Classroom Management System", layout="wide")

# Connect to DB
conn = sqlite3.connect('classroom.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables if not exist
cursor.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, phone TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, subject TEXT NOT NULL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS classes (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, teacher_id INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS enrollments (class_id INTEGER, student_id INTEGER, PRIMARY KEY (class_id, student_id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY AUTOINCREMENT, class_id INTEGER, student_id INTEGER, date TEXT NOT NULL, present INTEGER NOT NULL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, class_id INTEGER, student_id INTEGER, grade REAL NOT NULL, description TEXT)''')
conn.commit()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🏠 Dashboard", "👥 Students", "👩‍🏫 Teachers", "📚 Classes", "➕ Add Data"])

# ======================= DASHBOARD =======================
if page == "🏠 Dashboard":
    st.title("🏠 Classroom Dashboard")

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    total_students = pd.read_sql("SELECT COUNT(*) FROM students", conn).iloc[0,0]
    total_teachers = pd.read_sql("SELECT COUNT(*) FROM teachers", conn).iloc[0,0]
    total_classes = pd.read_sql("SELECT COUNT(*) FROM classes", conn).iloc[0,0]
    total_enrollments = pd.read_sql("SELECT COUNT(*) FROM enrollments", conn).iloc[0,0]

    col1.metric("Total Students", total_students)
    col2.metric("Total Teachers", total_teachers)
    col3.metric("Total Classes", total_classes)
    col4.metric("Total Enrollments", total_enrollments)

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Students per Class")
        df_classes = pd.read_sql('''
            SELECT c.name AS class_name, COUNT(e.student_id) AS students
            FROM classes c LEFT JOIN enrollments e ON c.id = e.class_id
            GROUP BY c.id
        ''', conn)
        if not df_classes.empty:
            fig1 = px.bar(df_classes, x='class_name', y='students', color='class_name', title="Enrolled Students by Class")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No classes yet")

    with col2:
        st.subheader("Attendance Overview (Latest Dates)")
        df_att = pd.read_sql('''
            SELECT c.name AS class_name, a.date, AVG(a.present) * 100 AS attendance_pct
            FROM attendance a JOIN classes c ON a.class_id = c.id
            GROUP BY a.class_id, a.date
            ORDER BY a.date DESC LIMIT 20
        ''', conn)
        if not df_att.empty:
            fig2 = px.line(df_att, x='date', y='attendance_pct', color='class_name', title="Attendance % Over Time")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No attendance recorded")

# ======================= STUDENTS =======================
elif page == "👥 Students":
    st.title("👥 Manage Students")

    with st.expander("Add New Student"):
        with st.form("add_student"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone (optional)")
            submitted = st.form_submit_button("Add")
            if submitted and name and email:
                try:
                    cursor.execute("INSERT INTO students (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
                    conn.commit()
                    st.success("Student added!")
                except sqlite3.IntegrityError:
                    st.error("Email already exists")

    st.subheader("All Students")
    df_students = pd.read_sql("SELECT * FROM students", conn)
    st.dataframe(df_students, use_container_width=True)
    st.subheader("Delete a Student")
student_to_delete = st.selectbox("Select Student ID to Delete", options=df_students['id'].tolist() if not df_students.empty else [])
if st.button("Delete Student") and student_to_delete:
    # Delete related records first (to avoid errors)
    cursor.execute("DELETE FROM enrollments WHERE student_id = ?", (student_to_delete,))
    cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_to_delete,))
    cursor.execute("DELETE FROM grades WHERE student_id = ?", (student_to_delete,))
    cursor.execute("DELETE FROM students WHERE id = ?", (student_to_delete,))
    conn.commit()
    st.success("Student deleted!")
    st.rerun()  # Refresh the page

# ======================= TEACHERS =======================
elif page == "👩‍🏫 Teachers":
    st.title("👩‍🏫 Manage Teachers")

    with st.expander("Add New Teacher"):
        with st.form("add_teacher"):
            name = st.text_input("Name")
            subject = st.text_input("Subject")
            submitted = st.form_submit_button("Add")
            if submitted and name and subject:
                cursor.execute("INSERT INTO teachers (name, subject) VALUES (?, ?)", (name, subject))
                conn.commit()
                st.success("Teacher added!")

    df_teachers = pd.read_sql("SELECT * FROM teachers", conn)
    st.dataframe(df_teachers, use_container_width=True)
    st.subheader("Delete a Teacher")
teacher_to_delete = st.selectbox("Select Teacher ID to Delete", options=df_teachers['id'].tolist())
if st.button("Delete Teacher") and teacher_to_delete:
    # Careful: Can't delete if they have classes
    cursor.execute("SELECT COUNT(*) FROM classes WHERE teacher_id = ?", (teacher_to_delete,))
    if cursor.fetchone()[0] > 0:
        st.error("Can't delete: Teacher has classes assigned!")
    else:
        cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_to_delete,))
        conn.commit()
        st.success("Teacher deleted!")
        st.rerun()

# ======================= CLASSES =======================
elif page == "📚 Classes":
    st.title("📚 Manage Classes")

    with st.expander("Create New Class"):
        teachers = pd.read_sql("SELECT id, name FROM teachers", conn)
        teacher_options = dict(zip(teachers.name, teachers.id))
        with st.form("add_class"):
            class_name = st.text_input("Class Name")
            teacher_name = st.selectbox("Teacher", options=list(teacher_options.keys()))
            submitted = st.form_submit_button("Create")
            if submitted and class_name:
                teacher_id = teacher_options[teacher_name]
                cursor.execute("INSERT INTO classes (name, teacher_id) VALUES (?, ?)", (class_name, teacher_id))
                conn.commit()
                st.success("Class created!")

    st.subheader("All Classes")
    df_classes = pd.read_sql('''
        SELECT c.id, c.name AS class_name, t.name AS teacher, 
               (SELECT COUNT(*) FROM enrollments e WHERE e.class_id = c.id) AS enrolled_students
        FROM classes c JOIN teachers t ON c.teacher_id = t.id
    ''', conn)
    st.dataframe(df_classes, use_container_width=True)
    with tab1:  # Enrolled Students tab
    # ... existing code ...
    st.subheader("Remove Enrollment")
    enrolled_ids = df_enrolled['id'].tolist() if not df_enrolled.empty else []
    student_to_remove = st.selectbox("Select Student ID to Remove from Class", options=enrolled_ids)
    if st.button("Remove from Class") and student_to_remove:
        cursor.execute("DELETE FROM enrollments WHERE class_id = ? AND student_id = ?", (class_id, student_to_remove))
        # Also delete their attendance/grades in this class?
        cursor.execute("DELETE FROM attendance WHERE class_id = ? AND student_id = ?", (class_id, student_to_remove))
        cursor.execute("DELETE FROM grades WHERE class_id = ? AND student_id = ?", (class_id, student_to_remove))
        conn.commit()
        st.success("Student removed from class!")
        st.rerun()

    st.subheader("Class Details & Enrollment")

    class_options = dict(zip(df_classes.class_name, df_classes.id))
    selected_class = st.selectbox("Select Class to View/Manage", options=list(class_options.keys()))

    if selected_class:
        class_id = class_options[selected_class]

        # Class info
        cursor.execute("SELECT name, teacher_id FROM classes WHERE id=?", (class_id,))
        c_name, t_id = cursor.fetchone()
        cursor.execute("SELECT name FROM teachers WHERE id=?", (t_id,))
        teacher_name = cursor.fetchone()[0]
        st.write(f"**Class:** {c_name} | **Teacher:** {teacher_name}")

        tab1, tab2, tab3, tab4 = st.tabs(["Enrolled Students", "Enroll New Student", "Attendance", "Grades"])

        with tab1:
            df_enrolled = pd.read_sql('''
                SELECT s.id, s.name, s.email FROM students s
                JOIN enrollments e ON s.id = e.student_id WHERE e.class_id=?
            ''', conn, params=(class_id,))
            st.dataframe(df_enrolled)

        with tab2:
            all_students = pd.read_sql("SELECT id, name FROM students", conn)
            enrolled_ids = pd.read_sql("SELECT student_id FROM enrollments WHERE class_id=?", conn, params=(class_id,))['student_id'].tolist()
            available_students = all_students[~all_students.id.isin(enrolled_ids)]
            student_options = dict(zip(available_students.name, available_students.id))

            if student_options:
                student_name = st.selectbox("Select Student to Enroll", options=list(student_options.keys()))
                if st.button("Enroll Student"):
                    student_id = student_options[student_name]
                    try:
                        cursor.execute("INSERT INTO enrollments (class_id, student_id) VALUES (?, ?)", (class_id, student_id))
                        conn.commit()
                        st.success(f"{student_name} enrolled!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Already enrolled")
            else:
                st.info("All students are already enrolled or no students exist")

        with tab3:
            st.write("Record Attendance")
            enrolled_students = pd.read_sql("SELECT id, name FROM students WHERE id IN (SELECT student_id FROM enrollments WHERE class_id=?)", conn, params=(class_id,))
            date = st.date_input("Date", datetime.today())
            present_dict = {}
            for _, row in enrolled_students.iterrows():
                present_dict[row['id']] = st.checkbox(row['name'], key=f"att_{row['id']}")

            if st.button("Save Attendance"):
                for sid, present in present_dict.items():
                    cursor.execute("INSERT INTO attendance (class_id, student_id, date, present) VALUES (?, ?, ?, ?)",
                                   (class_id, sid, str(date), int(present)))
                conn.commit()
                st.success("Attendance saved!")

        with tab4:
            st.write("Add Grade")
            student_grades = pd.read_sql('SELECT s.id, s.name FROM students s JOIN enrollments e ON s.id=e.student_id WHERE e.class_id=?', conn, params=(class_id,))
            if not student_grades.empty:
                student_sel = st.selectbox("Student", options=student_grades['name'].tolist())
                sid = student_grades[student_grades.name == student_sel]['id'].iloc[0]
                grade = st.number_input("Grade", min_value=0.0, max_value=100.0)
                desc = st.text_input("Description (optional)")
                if st.button("Add Grade"):
                    cursor.execute("INSERT INTO grades (class_id, student_id, grade, description) VALUES (?, ?, ?, ?)",
                                   (class_id, sid, grade, desc))
                    conn.commit()
                    st.success("Grade added!")

# ======================= ADD DATA (quick extras) =======================
elif page == "➕ Add Data":
    st.title("Quick Add: Attendance / Grade")
    # You can expand this page later

st.sidebar.markdown("---")
st.sidebar.info("Data saved in `classroom.db`")


# Close connection at end (Streamlit reruns whole script, but it's fine for SQLite)
