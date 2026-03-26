import streamlit as st
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Assignment Tracker", layout="wide")

# --- SESSION STATE MANAGEMENT ---
if 'assignments' not in st.session_state:
    st.session_state.assignments = []

if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# --- CSS STYLING ---
st.markdown("""
<style>
/* HARD Style (Red Border & Bg) */
.hard-assignment {
    background-color: #ffebee;
    padding: 15px;
    border-radius: 5px;
    border-left: 5px solid red;
    margin-bottom: 10px;
}
/* EASY Style (Green Border & Bg) */
.easy-assignment {
    background-color: #e8f5e9;
    padding: 15px;
    border-radius: 5px;
    border-left: 5px solid green;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)


# --- HELPER FUNCTIONS ---
def get_deadline_dt(assignment):
    return datetime.combine(assignment['date'], assignment['time'])


# --- MAIN APP LAYOUT ---
st.title("📚 Assignment Tracker")

# --- INPUT SECTION (ADD / EDIT) ---
st.subheader("Add / Edit Assignment")

with st.form("assignment_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Assignment Title")
        date = st.date_input("Due Date")
    with col2:
        time = st.time_input("Due Time")
        marks = st.number_input("Marks (Points)", min_value=0, value=10, step=1)

    description = st.text_area("Description")

    submitted = st.form_submit_button("Save Assignment")

    if submitted:
        if not title:
            st.error("Title is required!")
        else:
            new_assignment = {
                'title': title,
                'date': date,
                'time': time,
                'marks': marks,
                'description': description
            }

            if st.session_state.edit_index is not None:
                sorted_indices = sorted(range(len(st.session_state.assignments)),
                                        key=lambda i: get_deadline_dt(st.session_state.assignments[i]))
                original_index = sorted_indices[st.session_state.edit_index]
                st.session_state.assignments[original_index] = new_assignment
                st.session_state.edit_index = None
                st.success("Assignment updated!")
            else:
                st.session_state.assignments.append(new_assignment)
                st.success("Assignment added!")

            st.rerun()

if st.session_state.edit_index is not None:
    if st.button("Cancel Edit"):
        st.session_state.edit_index = None
        st.rerun()

st.divider()

# --- DISPLAY SECTION ---
sorted_assignments = sorted(st.session_state.assignments, key=get_deadline_dt)

if not sorted_assignments:
    st.info("No assignments yet.")
else:
    st.subheader("Your Assignments")

    for i, assignment in enumerate(sorted_assignments):

        # --- LOGIC: Calculate Score and Status ---
        due_dt = get_deadline_dt(assignment)
        now_dt = datetime.now()
        delta = due_dt - now_dt
        days_left = delta.days

        if days_left <= 0:
            days_left = 0.1

        score = assignment['marks'] / days_left

        # DECISION: if score > 10?
        if score > 10:
            status = "HARD"
            css_class = "hard-assignment"
            text_color = "red"  # Fixed: Hard is Red
            status_icon = "🔥"
        else:
            status = "EASY"
            css_class = "easy-assignment"
            text_color = "green"  # Fixed: Easy is Green
            status_icon = "✅"

        # --- DISPLAY ---
        st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)

        col_content, col_menu = st.columns([3, 1])

        with col_content:
            # UPDATED: Uses dynamic text_color variable
            st.markdown(
                f"### {assignment['title']} <span style='color:{text_color}; font-weight:bold;'>[{status}]</span>",
                unsafe_allow_html=True)
            st.write(f"📅 **Due:** {assignment['date'].strftime('%Y-%m-%d')} at {assignment['time'].strftime('%H:%M')}")
            st.write(f"🏆 **Marks:** {assignment['marks']} | 📉 **Score:** {score:.2f}")

            if assignment['description']:
                with st.expander("View Description"):
                    st.write(assignment['description'])

        # MENU
        with col_menu:
            action = st.selectbox(
                "Actions",
                ["Options...", "View", "Edit", "Delete"],
                label_visibility="collapsed",
                key=f"menu_{i}"
            )

            if action == "View":
                st.info(f"**Details:**\n{assignment['description']}")
                st.rerun()

            elif action == "Edit":
                st.session_state.edit_index = i
                st.rerun()

            elif action == "Delete":
                if st.checkbox(f"Confirm delete?", key=f"confirm_{i}"):
                    sorted_indices = sorted(range(len(st.session_state.assignments)),
                                            key=lambda k: get_deadline_dt(st.session_state.assignments[k]))
                    original_index = sorted_indices[i]
                    del st.session_state.assignments[original_index]
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)