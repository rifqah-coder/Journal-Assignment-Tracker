import streamlit as st
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Assignment Tracker", layout="wide")

# --- SESSION STATE ---
if 'assignments' not in st.session_state:
    st.session_state.assignments = []
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# --- CSS STYLING ---
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-weight: bold;
        color: #333;
        margin-bottom: 20px;
        font-size: 2.5rem;
    }

    /* HARD Card Style */
    .hard-card {
        background-color: #ffebee;
        border: 2px solid #ef5350;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 3px 3px 5px rgba(0,0,0,0.1);
    }

    /* EASY Card Style */
    .easy-card {
        background-color: #e8f5e9;
        border: 2px solid #66bb6a;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 3px 3px 5px rgba(0,0,0,0.1);
    }

    .section-header {
        font-size: 0.85rem;
        color: #555;
        text-transform: uppercase;
        font-weight: bold;
        margin-bottom: 5px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)


# --- HELPER ---
def get_deadline_dt(assignment):
    return datetime.combine(assignment['date'], assignment['time'])


# --- APP TITLE ---
st.markdown("<h1 class='main-title'>Assignment Tracker</h1>", unsafe_allow_html=True)

# --- INPUT SECTION ---
st.divider()
st.subheader("📝 Add New Assignment")

with st.form("assignment_form", clear_on_submit=True):
    # Row 1: Title and Course
    c1, c2 = st.columns([2, 1])
    with c1:
        title = st.text_input("Assignment Title")
    with c2:
        course = st.text_input("Course")  # Changed from Module

    # Row 2: Group only (Name removed)
    c3 = st.columns(1)[0]
    with c3:
        group = st.text_input("Group Name (Leave empty for Individual)")

    # Row 3: Date, Time, Marks
    c4, c5, c6 = st.columns(3)
    with c4:
        date = st.date_input("Due Date")
    with c5:
        time = st.time_input("Time (24 hrs)")
    with c6:
        marks = st.number_input("Marks", min_value=0, value=10, step=1)

    # Row 4: Description
    description = st.text_area("Description")

    submitted = st.form_submit_button("Save Assignment")

    if submitted:
        if not title:
            st.error("Title is required!")
        else:
            new_assignment = {
                'title': title,
                'course': course,  # Changed key
                'group': group,
                # 'name' removed
                'date': date,
                'time': time,
                'marks': marks,
                'description': description
            }

            if st.session_state.edit_index is not None:
                # Handle Edit
                sorted_indices = sorted(range(len(st.session_state.assignments)),
                                        key=lambda i: get_deadline_dt(st.session_state.assignments[i]))
                original_index = sorted_indices[st.session_state.edit_index]
                st.session_state.assignments[original_index] = new_assignment
                st.session_state.edit_index = None
                st.success("Updated!")
            else:
                # Handle Add
                st.session_state.assignments.append(new_assignment)
                st.success("Added!")

            st.rerun()

# --- CANCEL EDIT ---
if st.session_state.edit_index is not None:
    if st.button("Cancel Edit"):
        st.session_state.edit_index = None
        st.rerun()

st.divider()

# --- DISPLAY SECTION LOGIC ---
# First, sort all assignments by deadline
sorted_assignments = sorted(st.session_state.assignments, key=get_deadline_dt)
now = datetime.now()


# Helper to render a single card to avoid code duplication
def render_card(assignment, original_index):
    due_dt = get_deadline_dt(assignment)
    days_left = (due_dt - now).days
    if days_left <= 0: days_left = 0.1  # Avoid div by zero

    # Calculate Score
    score = assignment['marks'] / days_left

    # Determine Hard/Easy
    if score > 10:
        status = "HARD"
        css_class = "hard-card"
        text_color = "red"
    else:
        status = "EASY"
        css_class = "easy-card"
        text_color = "green"

    # Logic: If no group, it's Individual
    display_group = assignment['group'] if assignment['group'] else "Individual Assignment"

    st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)

    # Header
    col_header, col_menu = st.columns([4, 1])
    with col_header:
        st.markdown(
            f"### {assignment['title']} <span style='color:{text_color}; font-size:0.8em; border:1px solid {text_color}; padding:2px 8px; border-radius:5px;'>{status}</span>",
            unsafe_allow_html=True)

    with col_menu:
        action = st.selectbox(
            "Menu", ["Options", "Edit", "Delete"],
            label_visibility="collapsed", key=f"menu_{original_index}"
        )
        if action == "Edit":
            st.session_state.edit_index = original_index
            st.rerun()
        elif action == "Delete":
            if st.checkbox("Confirm?", key=f"del_{original_index}"):
                del st.session_state.assignments[original_index]
                st.rerun()

    # Grid Info
    info1, info2, info3 = st.columns(3)

    with info1:
        st.markdown("<div class='section-header'>Details</div>", unsafe_allow_html=True)
        st.write(f"📚 **Course:** {assignment['course']}")
        st.write(f"👥 **Group:** {display_group}")  # Logic handled here

    with info2:
        st.markdown("<div class='section-header'>Deadline</div>", unsafe_allow_html=True)
        st.write(f"📅 {assignment['date'].strftime('%Y-%m-%d')}")
        st.write(f"⏰ {assignment['time'].strftime('%H:%M')}")
        st.write(f"⏳ {days_left} days left")

    with info3:
        st.markdown("<div class='section-header'>Stats</div>", unsafe_allow_html=True)
        st.write(f"🏆 **Marks:** {assignment['marks']}")
        st.write(f"📉 **Score:** {score:.2f}")

    if assignment['description']:
        with st.expander("See Description"):
            st.write(assignment['description'])

    st.markdown("</div>", unsafe_allow_html=True)


# --- MAIN LOOPS ---

if not sorted_assignments:
    st.info("No assignments added yet.")
else:
    # SECTION 1: Due Very Soon (<= 24 hours)
    urgent_assignments = []
    # We need to store (assignment, original_index) to handle clicks correctly
    for idx, assign in enumerate(sorted_assignments):
        due_dt = get_deadline_dt(assign)
        if (due_dt - now).total_seconds() <= 86400:  # 24 hours in seconds
            urgent_assignments.append((assign, idx))

    if urgent_assignments:
        st.subheader("🚨 Due Very Soon")
        for assign, idx in urgent_assignments:
            render_card(assign, idx)
        st.divider()

    # SECTION 2: SOON (> 24 hours)
    soon_assignments = []
    for idx, assign in enumerate(sorted_assignments):
        due_dt = get_deadline_dt(assign)
        if (due_dt - now).total_seconds() > 86400:
            soon_assignments.append((assign, idx))

    if soon_assignments:
        st.subheader("📅 SOON")
        for assign, idx in soon_assignments:
            render_card(assign, idx)