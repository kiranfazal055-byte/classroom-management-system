import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(page_title="Smart Classroom Manager", layout="wide", page_icon="📚")

# Header with logo
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://cdn.vectorstock.com/i/500p/17/22/learning-management-system-template-vector-44391722.jpg", width=100)
with col2:
    st.title("📚 Smart Classroom Management System")

# Database connection
conn = sqlite3.connect('classroom.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, phone TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, subject TEXT NOT NULL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS classes (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, teacher_id INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS enrollments (class_id INTEGER, student_id INTEGER, PRIMARY KEY (class_id, student_id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY AUTOINCREMENT, class_id INTEGER, student_id INTEGER, date TEXT NOT NULL, present INTEGER NOT NULL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, class_id INTEGER, student_id INTEGER, grade REAL NOT NULL, description TEXT)''')
conn.commit()

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🏠 Dashboard", "👥 Students", "👩‍🏫 Teachers", "📚 Classes"])

# ======================= DASHBOARD =======================
if page == "🏠 Dashboard":
    st.markdown("### 📊 Overview & Insights")

    col1, col2, col3, col4 = st.columns(4)
    total_students = pd.read_sql("SELECT COUNT(*) FROM students", conn).iloc[0,0]
    total_teachers = pd.read_sql("SELECT COUNT(*) FROM teachers", conn).iloc[0,0]
    total_classes = pd.read_sql("SELECT COUNT(*) FROM classes", conn).iloc[0,0]
    total_enrollments = pd.read_sql("SELECT COUNT(*) FROM enrollments", conn).iloc[0,0]

    col1.metric("👥 Total Students", total_students)
    col2.metric("👩‍🏫 Total Teachers", total_teachers)
    col3.metric("📚 Total Classes", total_classes)
    col4.metric("📝 Total Enrollments", total_enrollments)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Students per Class")
        df_classes = pd.read_sql('''
            SELECT c.name AS class_name, COUNT(e.student_id) AS students
            FROM classes c LEFT JOIN enrollments e ON c.id = e.class_id
            GROUP BY c.id
        ''', conn)
        if not df_classes.empty:
            fig = px.bar(df_classes, x='class_name', y='students', color='class_name', title="Enrolled Students")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🥧 Distribution")
        if not df_classes.empty:
            fig = px.pie(df_classes, names='class_name', values='students', title="Student Distribution")
            st.plotly_chart(fig, use_container_width=True)

# ======================= STUDENTS =======================
elif page == "👥 Students":
    st.title("👥 Manage Students")

    with st.expander("➕ Add New Student"):
        with st.form("add_student"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone (optional)")
            submitted = st.form_submit_button("Add Student")
            if submitted and name and email:
                try:
                    cursor.execute("INSERT INTO students (name, email, phone) VALUES (?, ?, ?)", (name, email, phone or None))
                    conn.commit()
                    st.success("Student added!")
                except sqlite3.IntegrityError:
                    st.error("Email already exists!")

    st.subheader("📋 All Students")
    df_students = pd.read_sql("SELECT id, name, email, phone FROM students", conn)
    st.dataframe(df_students, use_container_width=True)

    # DELETE STUDENT
    st.markdown("---")
    st.subheader("🗑️ Delete a Student")
    if df_students.empty:
        st.info("No students to delete yet.")
    else:
        df_students['display'] = df_students['name'] + " (ID: " + df_students['id'].astype(str) + ")"
        student_options = dict(zip(df_students['display'], df_students['id']))
        selected = st.selectbox("Choose student to delete", options=list(student_options.keys()))
        st.warning("This will delete the student and ALL their enrollments, attendance, and grades!")
        if st.button("🛑 Permanently Delete Student", type="primary"):
            sid = student_options[selected]
            cursor.execute("DELETE FROM enrollments WHERE student_id = ?", (sid,))
            cursor.execute("DELETE FROM attendance WHERE student_id = ?", (sid,))
            cursor.execute("DELETE FROM grades WHERE student_id = ?", (sid,))
            cursor.execute("DELETE FROM students WHERE id = ?", (sid,))
            conn.commit()
            st.success("Student deleted successfully!")
            st.rerun()

# ======================= TEACHERS =======================
elif page == "👩‍🏫 Teachers":
    st.title("👩‍🏫 Manage Teachers")

    with st.expander("➕ Add New Teacher"):
        with st.form("add_teacher"):
            name = st.text_input("Name")
            subject = st.text_input("Subject")
            submitted = st.form_submit_button("Add Teacher")
            if submitted and name and subject:
                cursor.execute("INSERT INTO teachers (name, subject) VALUES (?, ?)", (name, subject))
                conn.commit()
                st.success("Teacher added!")

    st.subheader("📋 All Teachers")
    df_teachers = pd.read_sql("SELECT id, name, subject FROM teachers", conn)
    st.dataframe(df_teachers, use_container_width=True)

    # DELETE TEACHER
    st.markdown("---")
    st.subheader("🗑️ Delete a Teacher")
    if df_teachers.empty:
        st.info("No teachers to delete.")
    else:
        df_teachers['display'] = df_teachers['name'] + " - " + df_teachers['subject'] + " (ID: " + df_teachers['id'].astype(str) + ")"
        teacher_options = dict(zip(df_teachers['display'], df_teachers['id']))
        selected = st.selectbox("Choose teacher to delete", options=list(teacher_options.keys()))
        cursor.execute("SELECT COUNT(*) FROM classes WHERE teacher_id = ?", (teacher_options[selected],))
        if cursor.fetchone()[0] > 0:
            st.error("Cannot delete: This teacher has classes assigned. Delete classes first.")
        else:
            if st.button("🛑 Permanently Delete Teacher", type="primary"):
                cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_options[selected],))
                conn.commit()
                st.success("Teacher deleted!")
                st.rerun()

# ======================= CLASSES =======================
elif page == "📚 Classes":
    st.title("📚 Manage Classes")

    with st.expander("➕ Create New Class"):
        teachers_df = pd.read_sql("SELECT id, name FROM teachers", conn)
        if teachers_df.empty:
            st.warning("Add at least one teacher first!")
        else:
            teacher_options = dict(zip(teachers_df['name'], teachers_df['id']))
            with st.form("add_class"):
                class_name = st.text_input("Class Name")
                teacher_name = st.selectbox("Assign Teacher", options=list(teacher_options.keys()))
                submitted = st.form_submit_button("Create Class")
                if submitted and class_name:
                    cursor.execute("INSERT INTO classes (name, teacher_id) VALUES (?, ?)", (class_name, teacher_options[teacher_name]))
                    conn.commit()
                    st.success("Class created!")

    st.subheader("📋 All Classes")
    df_classes = pd.read_sql('''
        SELECT c.id, c.name AS class_name, t.name AS teacher,
               (SELECT COUNT(*) FROM enrollments e WHERE e.class_id = c.id) AS students
        FROM classes c JOIN teachers t ON c.teacher_id = t.id
    ''', conn)
    st.dataframe(df_classes, use_container_width=True)

    # DELETE CLASS
    st.markdown("---")
    st.subheader("🗑️ Delete a Class")
    if df_classes.empty:
        st.info("No classes to delete.")
    else:
        class_options = dict(zip(df_classes['class_name'] + " (Teacher: " + df_classes['teacher'] + ")", df_classes['id']))
        selected_class = st.selectbox("Choose class to delete", options=list(class_options.keys()))
        st.warning("This will delete the class and ALL enrollments, attendance, and grades for it!")
        if st.button("🛑 Permanently Delete Class", type="primary"):
            cid = class_options[selected_class]
            cursor.execute("DELETE FROM enrollments WHERE class_id = ?", (cid,))
            cursor.execute("DELETE FROM attendance WHERE class_id = ?", (cid,))
            cursor.execute("DELETE FROM grades WHERE class_id = ?", (cid,))
            cursor.execute("DELETE FROM classes WHERE id = ?", (cid,))
            conn.commit()
            st.success("Class deleted!")
            st.rerun()

    # CLASS DETAILS
    st.markdown("---")
    st.subheader("🔍 Class Details & Management")
    if not df_classes.empty:
        selected_class_name = st.selectbox("Select a class to manage", options=df_classes['class_name'])
        class_id = df_classes[df_classes['class_name'] == selected_class_name]['id'].iloc[0]

        cursor.execute("SELECT name, teacher_id FROM classes WHERE id=?", (class_id,))
        c_name, t_id = cursor.fetchone()
        cursor.execute("SELECT name FROM teachers WHERE id=?", (t_id,))
        teacher_name = cursor.fetchone()[0]
        st.write(f"**Class:** {c_name} | **Teacher:** {teacher_name}")

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["👥 Enrolled", "➕ Enroll", "📅 Attendance", "⭐ Grades", "🗑️ Delete Records"])

        with tab1:
            df_enrolled = pd.read_sql('SELECT s.id, s.name, s.email FROM students s JOIN enrollments e ON s.id = e.student_id WHERE e.class_id=?', conn, params=(class_id,))
            st.dataframe(df_enrolled)

            # UNENROLL STUDENT
            st.markdown("#### Remove Student from Class")
            if not df_enrolled.empty:
                unenroll_options = dict(zip(df_enrolled['name'] + " (ID: " + df_enrolled['id'].astype(str) + ")", df_enrolled['id']))
                to_unenroll = st.selectbox("Select student to remove", options=list(unenroll_options.keys()))
                if st.button("Remove from Class"):
                    sid = unenroll_options[to_unenroll]
                    cursor.execute("DELETE FROM enrollments WHERE class_id=? AND student_id=?", (class_id, sid))
                    cursor.execute("DELETE FROM attendance WHERE class_id=? AND student_id=?", (class_id, sid))
                    cursor.execute("DELETE FROM grades WHERE class_id=? AND student_id=?", (class_id, sid))
                    conn.commit()
                    st.success("Student removed!")
                    st.rerun()

        with tab2:
            all_students = pd.read_sql("SELECT id, name FROM students", conn)
            enrolled_ids = pd.read_sql("SELECT student_id FROM enrollments WHERE class_id=?", conn, params=(class_id,))['student_id'].tolist()
            available = all_students[~all_students.id.isin(enrolled_ids)]
            if not available.empty:
                avail_options = dict(zip(available['name'], available['id']))
                to_enroll = st.selectbox("Student to enroll", options=list(avail_options.keys()))
                if st.button("Enroll Student"):
                    cursor.execute("INSERT OR IGNORE INTO enrollments (class_id, student_id) VALUES (?, ?)", (class_id, avail_options[to_enroll]))
                    conn.commit()
                    st.success("Enrolled!")
                    st.rerun()
            else:
                st.info("No more students to enroll.")

        with tab3:
            df_att = pd.read_sql('SELECT id, student_id, date, present FROM attendance WHERE class_id=? ORDER BY date DESC', conn, params=(class_id,))
            if not df_att.empty:
                st.dataframe(df_att)
                att_to_delete = st.selectbox("Select Attendance Record ID to delete", options=df_att['id'].tolist())
                if st.button("Delete Attendance Record"):
                    cursor.execute("DELETE FROM attendance WHERE id=?", (att_to_delete,))
                    conn.commit()
                    st.success("Record deleted!")
                    st.rerun()

        with tab4:
            df_grades = pd.read_sql('SELECT id, student_id, grade, description FROM grades WHERE class_id=?', conn, params=(class_id,))
            if not df_grades.empty:
                st.dataframe(df_grades)
                grade_to_delete = st.selectbox("Select Grade Record ID to delete", options=df_grades['id'].tolist())
                if st.button("Delete Grade Record"):
                    cursor.execute("DELETE FROM grades WHERE id=?", (grade_to_delete,))
                    conn.commit()
                    st.success("Grade deleted!")
                    st.rerun()

st.sidebar.info("All changes are live and shared!")

