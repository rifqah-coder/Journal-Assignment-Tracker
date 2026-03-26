import streamlit as st
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(page_title="Assignment Tracker", layout="wide")

# --- SESSION STATE ---
if 'assignments' not in st.session_state:
    st.session_state.assignments = []
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# --- CSS STYLING (A+ UPGRADE) ---
st.markdown("""
<style>
    /* 1. BACKGROUND & CONTAINER */
    body {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        background-attachment: fixed;
        color: #F8FAFC;
    }
    .stApp {
        background: transparent;
    }

    /* 2. GLASS CARDS (Floating Effect) */
    .glass-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        /* The specific shadow requested */
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5); 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* 3. HOVER STATE (Lift up) */
    .glass-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.6);
        border-color: rgba(255, 255, 255, 0.2);
    }

    /* 4. GRADIENT TITLE */
    .main-title {
        text-align: center;
        font-weight: 900;
        font-size: 3.5rem;
        margin-bottom: 5px;
        background: linear-gradient(to right, #818cf8, #c084fc, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 15px rgba(129, 140, 248, 0.4));
    }

    /* 5. BUTTON STYLING (Solid Primary) */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1rem;
        width: 100%;
        padding: 12px;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.5);
        transition: 0.2s;
    }
    .stButton > button:hover {
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.8);
        transform: scale(1.02);
    }

    /* 6. INPUT FOCUS (Purple Glow) */
    input:focus, textarea:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 10px rgba(129, 140, 248, 0.5) !important;
        outline: none !important;
    }

    /* 7. PROGRESS BAR */
    .progress-container {
        width: 100%;
        background-color: rgba(255,255,255,0.1);
        border-radius: 10px;
        height: 6px;
        margin-top: 10px;
        margin-bottom: 15px;
        overflow: hidden;
    }
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    .bar-red { background: linear-gradient(90deg, #ef4444, #f87171); box-shadow: 0 0 10px #ef4444; }
    .bar-green { background: linear-gradient(90deg, #10b981, #34d399); box-shadow: 0 0 10px #10b981; }

    /* 8. ALIGNMENT & BADGES */
    .badge-hard {
        background: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border: 1px solid #ef4444;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
    }
    .badge-easy {
        background: rgba(16, 185, 129, 0.2);
        color: #6ee7b7;
        border: 1px solid #10b981;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
    }

    /* FIXING TITLE ALIGNMENT */
    h3 {
        margin: 0;
        padding: 0;
        line-height: 1.2;
    }
</style>
""", unsafe_allow_html=True)


# --- HELPER FUNCTIONS ---
def get_deadline_dt(assignment):
    return datetime.combine(assignment['date'], assignment['time'])


def get_relative_time(delta):
    """Converts timedelta to human-readable string."""
    total_seconds = int(delta.total_seconds())
    if total_seconds < 0:
        return "Overdue!"
    elif total_seconds < 60:
        return "Due < 1 min"
    elif total_seconds < 3600:
        mins = total_seconds // 60
        return f"Due in {mins} min{'s' if mins != 1 else ''}"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        return f"Due in {hours} hour{'s' if hours != 1 else ''}"
    else:
        days = total_seconds // 86400
        return f"Due in {days} day{'s' if days != 1 else ''}"


def get_urgency_progress(days_left):
    """Calculates width and color class for the progress bar."""
    # Urgency Logic: 0-1 day = 100%, 1-3 days = 75%, 3-7 days = 40%, 7+ = 15%
    if days_left <= 1:
        return 100, "bar-red"
    elif days_left <= 3:
        return 75, "bar-red"
    elif days_left <= 7:
        return 40, "bar-green"
    else:
        return 15, "bar-green"


# --- APP TITLE ---
st.markdown("<h1 class='main-title'>Assignment Tracker</h1>", unsafe_allow_html=True)

# --- INPUT SECTION ---
st.divider()
st.subheader("📝 New Assignment")

with st.form("assignment_form", clear_on_submit=True):
    # Form styling container
    st.markdown(
        "<div style='background: rgba(15, 23, 42, 0.5); padding: 20px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05);'>",
        unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        title = st.text_input("Assignment Title")
    with c2:
        course = st.text_input("Course")

    c3 = st.columns(1)[0]
    with c3:
        group = st.text_input("Group Name (Optional)")

    c4, c5, c6 = st.columns(3)
    with c4:
        date = st.date_input("Due Date")
    with c5:
        time = st.time_input("Time (24 hrs)")
    with c6:
        marks = st.number_input("Marks", min_value=0, value=10, step=1)

    description = st.text_area("Description")

    st.markdown("</div>", unsafe_allow_html=True)  # Close form container

    submitted = st.form_submit_button("Save Assignment")

    if submitted:
        if not title:
            st.error("Title is required!")
        else:
            new_assignment = {
                'title': title,
                'course': course,
                'group': group,
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
                st.success("Updated!")
            else:
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
sorted_assignments = sorted(st.session_state.assignments, key=get_deadline_dt)
now = datetime.now()


def render_card(assignment, original_index):
    due_dt = get_deadline_dt(assignment)
    delta = due_dt - now
    days_left = delta.days

    # Hidden calc for Hard/Easy logic
    if days_left <= 0:
        days_left_calc = 0.1
    else:
        days_left_calc = days_left

    score = assignment['marks'] / days_left_calc

    # Determine Style
    if score > 10:
        status = "HARD"
        badge_class = "badge-hard"
    else:
        status = "EASY"
        badge_class = "badge-easy"

    # Progress Bar Calc
    progress_width, progress_color = get_urgency_progress(days_left)
    relative_time = get_relative_time(delta)

    # Start HTML
    st.markdown(f"<div class='glass-card'>", unsafe_allow_html=True)

    # Header (Flexbox alignment logic)
    col_header, col_menu = st.columns([4, 1])

    with col_header:
        # Title + Badge
        st.markdown(
            f"<h3>{assignment['title']} <span class='{badge_class}'>{status}</span></h3>",
            unsafe_allow_html=True
        )

        # The New Progress Bar
        st.markdown(f"""
            <div class='progress-container'>
                <div class='progress-bar {progress_color}' style='width: {progress_width}%;'></div>
            </div>
        """, unsafe_allow_html=True)

    with col_menu:
        # Options Dropdown
        # Added padding-top in a div to visually align it better with the title
        st.markdown("<div style='padding-top: 5px;'>", unsafe_allow_html=True)
        action = st.selectbox(
            "Menu", ["Options", "Edit", "Delete"],
            label_visibility="collapsed", key=f"menu_{original_index}"
        )
        st.markdown("</div>", unsafe_allow_html=True)

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
        st.markdown(
            "<span style='font-size:0.75rem; color:#94a3b8; font-weight:700; letter-spacing:1px;'>DETAILS</span>",
            unsafe_allow_html=True)
        st.write(f"📚 **Course:** {assignment['course']}")
        if assignment['group']:
            st.write(f"👥 **Group:** {assignment['group']}")

    with info2:
        st.markdown(
            "<span style='font-size:0.75rem; color:#94a3b8; font-weight:700; letter-spacing:1px;'>DEADLINE</span>",
            unsafe_allow_html=True)
        st.write(f"📅 {assignment['date'].strftime('%Y-%m-%d')}")
        st.write(f"⏰ {assignment['time'].strftime('%H:%M')}")
        # Smart Relative Time
        st.write(f"🏃 {relative_time}")

    with info3:
        st.markdown("<span style='font-size:0.75rem; color:#94a3b8; font-weight:700; letter-spacing:1px;'>STATS</span>",
                    unsafe_allow_html=True)
        st.write(f"🏆 **Marks:** {assignment['marks']}")

    if assignment['description']:
        with st.expander("See Description"):
            st.write(assignment['description'])

    st.markdown("</div>", unsafe_allow_html=True)


# --- MAIN LOOPS ---

if not sorted_assignments:
    st.info("No assignments added yet.")
else:
    # SECTION 1: Due Very Soon
    urgent_assignments = []
    for idx, assign in enumerate(sorted_assignments):
        due_dt = get_deadline_dt(assign)
        if (due_dt - now).total_seconds() <= 86400:
            urgent_assignments.append((assign, idx))

    if urgent_assignments:
        st.subheader("🚨 Due Very Soon")
        for assign, idx in urgent_assignments:
            render_card(assign, idx)
        st.divider()
    else:
        # Empty State
        st.success("You're all caught up! 🚀")

    # SECTION 2: SOON
    soon_assignments = []
    for idx, assign in enumerate(sorted_assignments):
        due_dt = get_deadline_dt(assign)
        if (due_dt - now).total_seconds() > 86400:
            soon_assignments.append((assign, idx))

    if soon_assignments:
        st.subheader("📅 SOON")
        for assign, idx in soon_assignments:
            render_card(assign, idx)
    else:
        # Empty State (only shows if 'urgent' was also empty technically, or if no upcoming items)
        if not urgent_assignments:
            pass  # Already showed "Caught up"