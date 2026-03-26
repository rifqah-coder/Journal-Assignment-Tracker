
import streamlit as st
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Assignment Tracker", layout="wide")

# --- SESSION STATE MANAGEMENT ---
# Initialize assignments list in session state if it doesn't exist
if 'assignments' not in st.session_state:
    st.session_state.assignments = []

# Helper variable to track if we are editing an existing assignment
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# --- CSS STYLING ---
# Custom CSS to highlight the closest deadline in Red
st.markdown("""
<style>
.urgent-assignment {
    background-color: #ffebee;
    padding: 15px;
    border-radius: 5px;
    border-left: 5px solid red;
    margin-bottom: 10px;
}
.normal-assignment {
    background-color: #f0f2f6;
    padding: 15px;
    border-radius: 5px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---


def get_deadline_dt(assignment):
    """Combines date and time for sorting."""
    return datetime.combine(assignment['date'], assignment['time'])


# --- MAIN APP LAYOUT ---
st.title("📚 Assignment Tracker")

# --- INPUT SECTION (ADD / EDIT) ---
st.subheader("Add / Edit Assignment")

# Use a form to prevent the app from reloading on every keystroke
with st.form("assignment_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Assignment Title")
        date = st.date_input("Due Date")
    with col2:
        time = st.time_input("Due Time")

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
                'description': description
            }

            if st.session_state.edit_index is not None:
                # LOGIC: Update existing assignment
                # Note: We need to find the original index in the unsorted list or handle IDs.
                # For simplicity, we will replace the item at the specific index of the SORTED list
                # which requires us to sort first.
                sorted_indices = sorted(range(len(st.session_state.assignments)),
                                        key=lambda i: get_deadline_dt(st.session_state.assignments[i]))
                original_index = sorted_indices[st.session_state.edit_index]
                st.session_state.assignments[original_index] = new_assignment
                st.session_state.edit_index = None  # Reset edit mode
                st.success("Assignment updated!")
            else:
                # LOGIC: SAVE assignment
                st.session_state.assignments.append(new_assignment)
                st.success("Assignment added!")

            st.rerun()

# Cancel Edit Button
if st.session_state.edit_index is not None:
    if st.button("Cancel Edit"):
        st.session_state.edit_index = None
        st.rerun()

st.divider()

# --- DISPLAY SECTION ---
# LOGIC: SORT assignments by closest deadline
sorted_assignments = sorted(st.session_state.assignments, key=get_deadline_dt)

if not sorted_assignments:
    st.info("No assignments yet. Add one above!")
else:
    st.subheader("Your Assignments")

    # FOR each assignment
    for i, assignment in enumerate(sorted_assignments):

        # LOGIC: IF assignment is closest deadline THEN SET color = red
        if i == 0:
            st.markdown(f"<div class='urgent-assignment'>", unsafe_allow_html=True)
            urgency_label = "🔴 CLOSEST DEADLINE"
        else:
            st.markdown(f"<div class='normal-assignment'>", unsafe_allow_html=True)
            urgency_label = ""

        # Display Content
        col_content, col_menu = st.columns([3, 1])

        with col_content:
            st.markdown(f"### {assignment['title']} {urgency_label}")
            st.write(f"📅 **Due:** {assignment['date'].strftime('%Y-%m-%d')} at {assignment['time'].strftime('%H:%M')}")
            if assignment['description']:
                with st.expander("View Description"):
                    st.write(assignment['description'])

        # LOGIC: DISPLAY assignment list with 3-dot menu
        # In Streamlit, we simulate a "Menu" using a selectbox or columns of buttons.
        # Here we use a Selectbox for the "3-dot" feel.
        with col_menu:
            # We use a unique key for every selectbox
            action = st.selectbox(
                "Actions",
                ["Options...", "View", "Edit", "Delete"],
                label_visibility="collapsed",
                key=f"menu_{i}"
            )

            if action == "View":
                st.info(f"**Details:**\n{assignment['description']}")
                # Reset selectbox immediately so it doesn't stay stuck on "View"
                st.rerun()

            elif action == "Edit":
                # LOGIC: EDIT assignment details
                st.session_state.edit_index = i
                st.rerun()

            elif action == "Delete":
                # LOGIC: DISPLAY confirmation popup
                if st.checkbox(f"Confirm delete '{assignment['title']}?", key=f"confirm_{i}"):
                    # Remove from the main list (need to find original index)
                    sorted_indices = sorted(range(len(st.session_state.assignments)),
                key= lambda k: get_deadline_dt(st.session_state.assignments[k]))
                original_index = sorted_indices[i]

                # LOGIC: REMOVE assignment
                del st.session_state.assignments[original_index]
                st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
