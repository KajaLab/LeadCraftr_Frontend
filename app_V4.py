# =================================================
# LeadCraftr · DEMO front-end
# =================================================

# ====== IMPORTS & API | CONFIG | FUNCTIONS ======
import streamlit as st
import random
import requests
import time
from daily_rate_page_NEW import display_tjm_calculator

BASE_URL = "https://leadcraftr-api-cloud-623673804405.europe-west1.run.app"

def get_matches(statement_content: str, user_type: str):
    params = {"mission_statement": statement_content} # Only the content as param
    endpoint = ""
    if user_type == "freelancer":
        endpoint = "/match_freelance" # Correct endpoint for freelancers
    elif user_type == "company":
        endpoint = "/match_prospect" # Correct endpoint for companies (prospects)
    else:
        raise ValueError("Invalid user_type for get_matches.")

    response = requests.get(f"{BASE_URL}{endpoint}", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Matching error: {response.text}")

def generate_mail(freelance: dict, prospect: dict, sender_type: str, previous_mail_content: str = ""):
    """
    Generates an email via the API, including the sender_type.
    :param freelance: Dictionary representing the freelancer's data.
    :param prospect: Dictionary representing the prospect's (company) data.
    :param sender_type: A string indicating who is sending the email ('freelancer' or 'company').
    :param previous_mail_content: Optional, previous email content for regeneration.
    """
    payload = {
        "freelance": freelance,
        "prospect": prospect,
        "sender_type": sender_type,
        "previous_mail_content": previous_mail_content
    }

    endpoint = ""
    if sender_type == "freelancer":
        endpoint = "/generate_mail_freelance"
    elif sender_type == "company":
        endpoint = "/generate_mail_prospect"
    else:
        raise ValueError("Invalid sender_type for generate_mail.")

    response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
    if response.status_code == 200:
        return response.json().get("email", "")
    else:
        raise Exception(f"Email generation error: {response.text}")


# --- FONCTIONS DE SANITISATION MISES À JOUR AVEC LES DERNIERS CHAMPS ET VÉRIFICATIONS DE TYPE ---
def sanitize_freelancer_data(freelancer_dict: dict) -> dict:
    """Ensures a freelancer dictionary has all necessary fields with default values."""
    sanitized_data = freelancer_dict.copy()
    sanitized_data['name'] = sanitized_data.get('name') or "A Professional Freelancer"
    sanitized_data['title'] = sanitized_data.get('title') or "Freelancer"
    sanitized_data['main_sector'] = sanitized_data.get('main_sector') or "General Tech"

    top3_skills = sanitized_data.get('top3_skills')
    if isinstance(top3_skills, list):
        sanitized_data['top3_skills'] = ", ".join(top3_skills)
    elif not isinstance(top3_skills, str) or not top3_skills:
        sanitized_data['top3_skills'] = "Software Development, Data Analysis, Project Management"

    # Ensure daily_rate is a number
    daily_rate_val = sanitized_data.get('daily_rate')
    if isinstance(daily_rate_val, list):
        sanitized_data['daily_rate'] = daily_rate_val[0] if daily_rate_val else 500
    elif not isinstance(daily_rate_val, (int, float)):
        sanitized_data['daily_rate'] = 500

    sanitized_data['city'] = sanitized_data.get('city') or "Remote"

    original_remote = sanitized_data.get('remote')
    if isinstance(original_remote, bool):
        sanitized_data['remote'] = "Yes" if original_remote else "No"
    elif isinstance(original_remote, str):
        sanitized_data['remote'] = "Yes" if original_remote.lower() in ['yes', 'true', 'remote'] else "No"
    else:
        sanitized_data['remote'] = "No"

    sanitized_data['mission_statement'] = sanitized_data.get('mission_statement') or "Experienced professional ready to contribute to innovative projects."
    sanitized_data['preferred_tone'] = sanitized_data.get('preferred_tone') or "Professional"
    sanitized_data['preferred_style'] = sanitized_data.get('preferred_style') or "Storytelling"
    return sanitized_data

def sanitize_prospect_data(prospect_dict: dict) -> dict:
    """Ensures a prospect (company) dictionary has all necessary fields with default values."""
    sanitized_data = prospect_dict.copy()
    sanitized_data['company'] = sanitized_data.get('company') or "A Leading Company"
    sanitized_data['sector'] = sanitized_data.get('sector') or "Tech / SaaS"
    sanitized_data['main_contact'] = sanitized_data.get('main_contact') or "Valued Partner"
    sanitized_data['contact_role'] = sanitized_data.get('contact_role') or "Hiring Manager"
    sanitized_data['city'] = sanitized_data.get('city') or "Remote"
    sanitized_data['mission_statement'] = sanitized_data.get('mission_statement') or "Driving innovation and delivering value to clients."
    sanitized_data['company_size'] = sanitized_data.get('company_size') or "Mid-size"

    sanitized_data['funding_stage'] = sanitized_data.get('funding_stage') or "Undisclosed"
    sanitized_data['ticket_size_class'] = sanitized_data.get('ticket_size_class') or "Medium"

    sanitized_data['target_tone'] = sanitized_data.get('target_tone') or \
                                   sanitized_data.get('preferred_tone') or \
                                   "Professional"

    if 'preferred_tone' in sanitized_data: # Remove if it was a misnamed 'target_tone'
        del sanitized_data['preferred_tone']

    original_remote = sanitized_data.get('remote')
    if isinstance(original_remote, bool):
        sanitized_data['remote'] = original_remote
    elif isinstance(original_remote, str):
        sanitized_data['remote'] = original_remote.lower() in ['yes', 'true', 'remote']
    else:
        sanitized_data['remote'] = False

    sanitized_data['email'] = sanitized_data.get('email') or "info@example.com"

    return sanitized_data

# ====== PAGE CONFIG ======
st.set_page_config(
    page_title="LeadCraftr · Demo",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ====== SESSION INITIALISATION ======
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"
if "user_type" not in st.session_state:
    st.session_state.user_type = "freelancer" # Default user type
if "profile_created" not in st.session_state:
    st.session_state.profile_created = False # Flag for profile creation
if "user_profile_data" not in st.session_state:
    st.session_state.user_profile_data = {} # Stores all profile data
if "freelancer_tjm" not in st.session_state:
    st.session_state.freelancer_tjm = None # Stores calculated TJM
if "welcome_message_shown" not in st.session_state:
    st.session_state.welcome_message_shown = False # To show welcome message only once per session
if "time_saved" not in st.session_state: # Initialize time_saved
    st.session_state.time_saved = 0
if "money_saved" not in st.session_state: # Initialize money_saved
    st.session_state.money_saved = 0

# Initialisation des compteurs de temps et d'argent économisés
# Based on market research for time saved on personalized email drafting and value of copywriting.
if "total_time_saved" not in st.session_state:
    st.session_state.total_time_saved = 0 # in minutes
if "total_money_saved" not in st.session_state:
    st.session_state.total_money_saved = 0 # in EUR/USD


# Initialisation for matching forms
for k in ["freelancer_matches", "freelancer_form_submitted", "company_matches", "company_form_submitted"]:
    if k not in st.session_state:
        st.session_state[k] = [] if "matches" in k else False

# Stores email content, generation count, modal visibility, and sent status for each match
if "freelancer_email_sent_states" not in st.session_state:
    st.session_state.freelancer_email_sent_states = {}
if "company_email_sent_states" not in st.session_state:
    st.session_state.company_email_sent_states = {}

# --- Custom CSS for the new "Time Saved" and "Money Saved" box ---
# Removed the fixed position info-box CSS as it should only appear after landing

# Add an info message about the calculation basis, visible on pages with the nav bar
# This will appear slightly below the fixed info box, in the main content area
# Moved to Dashboard page only
# st.info("💡 *Time and Money Saved estimates are based on industry averages for personalized email drafting (5 minutes) and copywriting costs (€75) per email sent, derived from market research.*")


# ===== SIDEBAR CONTENT (Navigation and Profile Type) MOVED TO TOP =====
st.sidebar.markdown("### 👥 Profile Type")
selected_profile_type = st.sidebar.radio("I am a ...", ["Freelancer", "Company"], key="profile_type_sidebar", index=0 if st.session_state.user_type == "freelancer" else 1)
st.session_state.user_type = selected_profile_type.lower() # Update session state from sidebar

# Dynamic profile page label
profile_page_label = "📝 Create your profile"
if st.session_state.profile_created:
    profile_page_label = "👤 My Profile"

# If the selected page is 'Create your profile' but a profile exists, redirect to 'My Profile' view
# This ensures the label and content match
if st.session_state.page == "📝 Create your profile" and st.session_state.profile_created:
    st.session_state.page = "👤 My Profile"
elif st.session_state.page == "👤 My Profile" and not st.session_state.profile_created:
    st.session_state.page = "📝 Create your profile"

st.session_state.page = st.sidebar.radio(
    "Find your matches",
    ["🏠 Home", profile_page_label, "📊 Dashboard", "🧮 Calculate your daily rate"], # New sidebar option
    key="navigation_menu",
    index=["🏠 Home", profile_page_label, "📊 Dashboard", "🧮 Calculate your daily rate"].index(st.session_state.page)
)


# ====== GLOBAL CSS FOR HIDING CHROME & BUTTON STYLING ======
st.markdown("""
    <style>
    /* Hide Streamlit Chrome for initial splash */
    header[data-testid="stHeader"],
    footer[data-testid="stFooter"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    /* Sidebar will be shown explicitly later */
    section[data-testid="stSidebar"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }

    /* Custom Button Styling for "Regenerate" and "Validate" */
    .stButton > button {
        background: linear-gradient(90deg, #7B61FF, #A08AFF); /* Violet gradient */
        color: white !important; /* Text color */
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(123, 97, 255, 0.4); /* Subtle glow */
    }

    .stButton > button:hover {
        background: linear: #7B61FF; /* Reverse gradient on hover */
        box-shadow: 0 6px 20px rgba(123, 97, 255, 0.6); /* Enhanced glow on hover */
        transform: translateY(-2px); /* Slight lift effect */
    }

    /* New CSS for the "Send" button when validated/sent */
    .stButton > button.sent-button {
        background: linear-gradient(90deg, #28a745, #218838); /* Green gradient */
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.4); /* Green glow */
    }
    .stButton > button.sent-button:hover {
        background: linear: #218838, #28a745); /* Reverse green gradient on hover */
        box-shadow: 0 6px 20px rgba(40, 167, 69, 0.6); /* Enhanced green glow */
    }


    /* LANDING PAGE CSS */
    .landing-splash-section {
        height: 100vh;
        width: 100vw;
        margin-left: calc(-50vw + 50%); /* Centers for wide content */
        background: radial-gradient(circle at top center, #7B61FF, #1B103F 80%);
        background-attachment: fixed;
        background-size: cover;
        color: white; /* Default text color for the section */
        font-family: 'Poppins', sans-serif;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 20px;
        box-sizing: border-box;
    }
    .landing-title {
        font-size: 72px;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 10px;
        color: white; /* "LeadCraft" part will be white */
    }
    /* Specific styling for the (r) part: black parentheses and black 'r' */
    .r-black {
        color: black; /* Makes the text within this span black */
    }

    .landing-subtitle {
        font-size: 24px;
        color: #ccc;
        margin-top: 10px;
    }
    .scroll-indicator {
        font-size: 16px;
        color: #aaa;
        margin-top: 30px;
        animation: bounce 2s infinite;
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(5px); }
    }

    /* Ensure main container is reset for subsequent content */
    [data-testid="stAppViewContainer"] > .main {
        background: none !important;
        padding-top: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Make content wide again after the landing splash for the rest of the page */
    .st-emotion-cache-1y4qm01, .st-emotion-cache-uf99v8, .css-1y4qm01, .css-uf99v8 {
        max-width: unset !important;
        padding: 1rem !important;
    }
    </style>

    <div class="landing-splash-section">
        <div class="landing-title">
            LeadCraft<span class="r-black">(r)</span>
        </div>
        <div class="landing-subtitle">
            Smart Words. Good Leads.
        </div>
        <div class="scroll-indicator">
            ↓ Scroll to get started
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Start of Scrollable Content ---
st.markdown("<br><br>", unsafe_allow_html=True) # Add some space after the splash

# Ensure sidebar and header are visible for the scrollable part of Home
st.markdown("""
    <style>
    section[data-testid="stSidebar"],
    header[data-testid="stHeader"] {
        display: block !important;
        visibility: visible !important;
        height: auto !important;
    }
    /* Restore default padding for the main content block after the landing section */
    [data-testid="stAppViewContainer"] > .main > div > div {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    </style>
""", unsafe_allow_html=True)



# ====== PAGE CONTENT RENDERING ======
if st.session_state.page == "🏠 Home":
    # Display welcome message only once per session if profile created
    if st.session_state.profile_created and not st.session_state.welcome_message_shown:
        user_name = st.session_state.user_profile_data.get("first_name") or st.session_state.user_profile_data.get("contact_person") or "there"
        st.success(f"Welcome back, **{user_name}**! Get ready to connect and save even more time and money! 🚀") # Simplified welcome message
        st.session_state.welcome_message_shown = True # Mark as shown
        st.balloons() # Add some flair

    # Affichage des métriques de temps et d'argent économisés en haut à droite de la page Home
    # Utilisation de st.container pour regrouper et positionner
    # This replaces the fixed top-right box and is only on the Home page
    # Using st.columns to push the metrics to the right
    _, col_metrics = st.columns([0.7, 0.3]) # Adjust ratio as needed
    with col_metrics:
        st.container(border=True).markdown(f"""
            <div style='text-align: right;'>
                <h5>🕰️ Time Saved: {st.session_state.total_time_saved} min</h5>
                <h5>💰 Money Saved: €{st.session_state.total_money_saved:.2f}</h5>
            </div>
        """, unsafe_allow_html=True)


    st.markdown("### 🎯 Find your perfect match")

    # User selects their primary role - NOW REFLECTS SIDEBAR CHOICE
    # The `index` is directly tied to `st.session_state.user_type`
    # and we remove the local update of `st.session_state.user_type`
    role_options = ("A freelancer looking for a company", "A company looking for a freelancer")
    current_role_index = 0 if st.session_state.user_type == "freelancer" else 1

    # This radio button now only DISPLAYS the current user_type set by the sidebar
    # If a user changes it here, it will update st.session_state.user_type for consistency.
    role = st.radio(
        "You are …",
        role_options,
        index=current_role_index,
        horizontal=True,
        key="home_page_role_selector" # Ensure a unique key
    )
    # This line is crucial: it updates st.session_state.user_type if the user changes the radio on home page.
    # This is fine, as both sidebar and home page can influence it, but sidebar is "primary" on page load.
    st.session_state.user_type = "freelancer" if role.startswith("A freelancer") else "company"


    # Placeholder for validation message
    statement_error_placeholder = st.empty()

    # --- FREELANCER | SEARCH FORM ---
    if st.session_state.user_type == "freelancer":
        st.markdown("#### Freelancer — Find Companies")

        # Pre-fill mission statement from profile if available
        default_statement = st.session_state.user_profile_data.get('personal_statement', "")

        with st.form("freelancer_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Your name", value=st.session_state.user_profile_data.get("first_name", ""))
            mode = c2.selectbox("Preferred work mode", ["Remote", "On-site", "Hybrid"], index=["Remote", "On-site", "Hybrid"].index(st.session_state.user_profile_data.get("work_mode", "Remote")))
            c1, c2 = st.columns(2)
            job = c1.text_input("Desired job title", value=st.session_state.user_profile_data.get("desired_job_title", ""))
            sizes = c2.multiselect("Preferred company size (max 3)", ["Startup", "Small", "Mid-size", "Large"], default=st.session_state.user_profile_data.get("preferred_company_sizes", []), max_selections=3)

            # --- FIX APPLIED HERE for daily_rate type error ---
            current_daily_rate_val = st.session_state.user_profile_data.get("daily_rate", 850)
            if isinstance(current_daily_rate_val, list):
                current_daily_rate_val = int(current_daily_rate_val[0]) if current_daily_rate_val else 850
            elif isinstance(current_daily_rate_val, (int, float)):
                current_daily_rate_val = int(current_daily_rate_val)
            else:
                current_daily_rate_val = 850

            rate = st.slider("Your day rate (€)", 100, 2000, value=current_daily_rate_val, step=50)
            # --- END FIX ---

            exp = st.slider("Your experience (years)", 0, 20, value=st.session_state.user_profile_data.get("experience_years", 5))
            sector = st.selectbox("Main sector", ["FinTech", "HealthTech", "EdTech", "GreenTech", "Tech / SaaS", "MarTech", "Retail / E-com", "Gaming"], index=["FinTech", "HealthTech", "EdTech", "GreenTech", "Tech / SaaS", "MarTech", "Retail / E-com", "Gaming"].index(st.session_state.user_profile_data.get("main_sector", "Tech / SaaS")))
            skills = st.multiselect("Your skills (max 3)", ["Python", "Rust", "Solidity", "Kubernetes", "Cloud Security", "Quant Analysis", "FastAPI", "LangChain", "PostgreSQL"], default=st.session_state.user_profile_data.get("skills", []), max_selections=3)
            statement = st.text_area("Personal statement", height=110, placeholder="Please fill this box with your personal statement (at least 10 characters).", value=default_statement)

            selected_style = st.selectbox(
                "✍️ Preferred email style",
                ["Storytelling", "Direct", "Formal", "Informal", "Benefit-driven", "Technical"],
                index=["Storytelling", "Direct", "Formal", "Informal", "Benefit-driven", "Technical"].index(st.session_state.user_profile_data.get("preferred_email_style", "Storytelling")),
                key="freelancer_style_selection_home"
            )

            submitted = st.form_submit_button("🔍 Find companies")

        if submitted:
            if not statement or len(statement) < 10:
                statement_error_placeholder.error("Please fill the box with a personal statement (at least 10 characters).")
                st.session_state.freelancer_form_submitted = False
            else:
                statement_error_placeholder.empty()
                st.session_state.freelancer_form_submitted = True

                # Update profile data in session state for consistency
                st.session_state.user_profile_data.update({
                    "first_name": name,
                    "work_mode": mode,
                    "desired_job_title": job,
                    "preferred_company_sizes": sizes,
                    "daily_rate": rate,
                    "experience_years": exp,
                    "main_sector": sector,
                    "skills": skills,
                    "personal_statement": statement, # Update here
                    "preferred_email_style": selected_style
                })

                progress_bar_placeholder = st.empty()
                progress_text_placeholder = st.empty()
                progress_bar_placeholder.progress(0)
                progress_text_placeholder.text("Finding companies... 0/10")

                try:
                    matches = get_matches(statement, user_type="freelancer")
                    st.session_state.freelancer_matches = matches[:10]

                    for i in range(1, 11):
                        progress = i / 10
                        progress_bar_placeholder.progress(progress)
                        progress_text_placeholder.text(f"Finding companies... {i}/10")
                        time.sleep(0.05)

                    st.toast("🎉 Companies found!", icon="✅")
                    progress_text_placeholder.text(f"Finding companies... 10/10 - Done!")
                    st.success(f"{len(st.session_state.freelancer_matches)} companies found ✔︎")

                except Exception as e:
                    st.error(f"❌ API error: {e}")
                    st.session_state.freelancer_form_submitted = False
                    progress_bar_placeholder.empty()
                    progress_text_placeholder.empty()

        if st.session_state.freelancer_form_submitted and st.session_state.freelancer_matches:
            for m in st.session_state.freelancer_matches:
                company_id = m['company']

                if company_id not in st.session_state.freelancer_email_sent_states:
                    st.session_state.freelancer_email_sent_states[company_id] = {
                        "content": "", "count": 0, "show_modal": False, "sent": False, "show_success_message": False
                    }

                expander_key = f"expander_{company_id}"
                if expander_key not in st.session_state:
                    st.session_state[expander_key] = False

                expander_header_prefix = "✅ " if st.session_state.freelancer_email_sent_states[company_id]["sent"] else "🧩 "

                with st.expander(
                    f"{expander_header_prefix}{m['company']} — {m['mission_statement']}",
                    expanded=st.session_state[expander_key]
                ):
                    selected_tone = st.multiselect(
                        "🎙️ Choose a tone",
                        ["Warm", "Professional", "Creative", "Direct", "Empathetic"],
                        default=["Professional"],
                        key=f"tone_{company_id}",
                        max_selections=2
                    )
                    st.session_state[expander_key] = True

                    if not st.session_state.freelancer_email_sent_states[company_id]["content"] and \
                       st.session_state.freelancer_email_sent_states[company_id]["count"] == 0:
                        try:
                            # Use profile data for sender, override statement with form's current value
                            freelance_data_sender = sanitize_freelancer_data({
                                **st.session_state.user_profile_data, # Use profile as base
                                "name": name, # Override with current form input
                                "title": job,
                                "main_sector": sector,
                                "top3_skills": skills,
                                "daily_rate": rate,
                                "remote": mode == "Remote",
                                "mission_statement": statement, # Use the statement from the current form
                                "preferred_tone": ", ".join(selected_tone if selected_tone else ["Professional"]),
                                "preferred_style": selected_style
                            })
                            prospect_data_initial = sanitize_prospect_data(m)

                            initial_email = generate_mail(freelance_data_sender, prospect_data_initial, sender_type="freelancer", previous_mail_content="")
                            st.session_state.freelancer_email_sent_states[company_id]["content"] = initial_email
                            st.session_state.freelancer_email_sent_states[company_id]["count"] = 1
                        except Exception as e:
                            st.warning(f"⚠️ Initial email generation error for {company_id}: {e}")

                    st.caption("✉️ Tone-matched email")
                    st.text_area("tone_matched_email", value=st.session_state.freelancer_email_sent_states[company_id]["content"], height=180, key=f"textarea_{company_id}")

                    regen_col, validate_col = st.columns([1, 1])
                    with regen_col:
                        if st.button(f"🔄 Regenerate", key=f"regen_{company_id}"):
                            st.session_state[expander_key] = True
                            st.session_state.freelancer_email_sent_states[company_id]["show_success_message"] = False
                            if st.session_state.freelancer_email_sent_states[company_id]["count"] < 3:
                                try:
                                    # Use profile data for sender, override statement with form's current value
                                    freelance_data_sender = sanitize_freelancer_data({
                                        **st.session_state.user_profile_data, # Use profile as base
                                        "name": name, # Override with current form input
                                        "title": job,
                                        "main_sector": sector,
                                        "top3_skills": skills,
                                        "daily_rate": rate,
                                        "remote": mode == "Remote",
                                        "mission_statement": statement, # Use the statement from the current form
                                        "preferred_tone": ", ".join(selected_tone if selected_tone else ["Professional"]),
                                        "preferred_style": selected_style
                                    })
                                    prospect_data = sanitize_prospect_data(m)

                                    current_textarea_content = st.session_state.freelancer_email_sent_states[company_id]["content"]
                                    email = generate_mail(freelance_data_sender, prospect_data, sender_type="freelancer", previous_mail_content=current_textarea_content)
                                    st.session_state.freelancer_email_sent_states[company_id]["content"] = email
                                    st.session_state.freelancer_email_sent_states[company_id]["count"] += 1
                                    st.session_state.freelancer_email_sent_states[company_id]["sent"] = False
                                except Exception as e:
                                    st.warning(f"⚠️ Error: {e}")
                            else:
                                st.warning("⚠️ You’ve reached the limit of email generations. Upgrade to LeadCraftr Pro.")
                    with validate_col:
                        if st.session_state.freelancer_email_sent_states[company_id]["sent"]:
                            st.markdown(
                                f'<button class="stButton css-1y4qm01 sent-button" disabled>✅ Sent!</button>',
                                unsafe_allow_html=True
                            )
                        else:
                            if st.button(f"✅ Validate this email", key=f"validate_{company_id}"):
                                st.session_state[expander_key] = True
                                st.session_state.freelancer_email_sent_states[company_id]["show_modal"] = True
                                st.session_state.freelancer_email_sent_states[company_id]["show_success_message"] = False

                    if st.session_state.freelancer_email_sent_states[company_id]["show_modal"]:
                        st.markdown("#### ✅ Email ready to send:")
                        st.code(st.session_state.freelancer_email_sent_states[company_id]["content"], language="markdown")
                        if st.button(f"📤 Send", key=f"send_{company_id}"):
                            st.session_state[expander_key] = True
                            st.session_state.freelancer_email_sent_states[company_id]["show_modal"] = False
                            st.session_state.freelancer_email_sent_states[company_id]["sent"] = True
                            st.session_state.freelancer_email_sent_states[company_id]["show_success_message"] = True

                            # Incrémenter le temps et l'argent économisés (Freelancer)
                            st.session_state.total_time_saved += 5 # Based on research: ~5 mins saved per personalized email drafting
                            st.session_state.total_money_saved += 20 # Based on research: value of personalized copywriting

                            st.toast("Email sent! 🎉", icon="✅")
                            st.rerun()

                    if st.session_state.freelancer_email_sent_states[company_id]["sent"] and st.session_state.freelancer_email_sent_states[company_id]["show_success_message"]:
                        st.success("Your message has been sent successfully!")

    # --- COMPANY | SEARCH FORM ---
    elif st.session_state.user_type == "company":
        st.markdown("#### Company — Find Freelancers")

        # Pre-fill mission statement from profile if available
        default_mission = st.session_state.user_profile_data.get('mission_statement', "")

        with st.form("company_form"):
            c1, c2 = st.columns(2)
            comp = c1.text_input("Company name", value=st.session_state.user_profile_data.get("company_name", ""))
            csize = c2.selectbox("Company size", ["Startup", "SME", "Large Enterprise"], index=["Startup", "SME", "Large Enterprise"].index(st.session_state.user_profile_data.get("company_size", "SME")))
            c1, c2 = st.columns(2)
            title = c1.text_input("Your role/contact person title", value=st.session_state.user_profile_data.get("contact_role", ""))
            loc = c2.text_input("Company location (city)", value=st.session_state.user_profile_data.get("location", ""))
            budget = st.slider("Budget per day (€)", 100, 2000, value=st.session_state.user_profile_data.get("budget_per_day", 650), step=50)
            sector = st.selectbox("Company sector", ["FinTech", "HealthTech", "EdTech", "GreenTech", "Tech / SaaS", "MarTech", "Retail / E-com", "Gaming"], index=["FinTech", "HealthTech", "EdTech", "GreenTech", "Tech / SaaS", "MarTech", "Retail / E-com", "Gaming"].index(st.session_state.user_profile_data.get("main_sector", "Tech / SaaS")))
            req_skills = st.multiselect("Required skills (max 3)", ["Python","Rust","Solidity","Kubernetes","Cloud Security", "Quant Analysis","FastAPI","LangChain","PostgreSQL"], default=st.session_state.user_profile_data.get("required_skills", []), max_selections=3)
            mode = st.selectbox("Work mode", ["Remote", "On-site", "Hybrid"], index=["Remote", "On-site", "Hybrid"].index(st.session_state.user_profile_data.get("work_mode", "Remote")))
            mission = st.text_area("Mission statement", height=110, placeholder="Your mission statement should have at least 10 characters.", value=default_mission)
            submitted = st.form_submit_button("🔍 Find freelancers")

        if submitted:
            if not mission or len(mission) < 10:
                statement_error_placeholder.error("Please fill the box with a mission statement (at least 10 characters).")
                st.session_state.company_form_submitted = False
            else:
                statement_error_placeholder.empty()
                st.session_state.company_form_submitted = True
                # Update profile data in session state for consistency
                st.session_state.user_profile_data.update({
                    "company_name": comp,
                    "company_size": csize,
                    "contact_role": title,
                    "location": loc,
                    "budget_per_day": budget,
                    "main_sector": sector,
                    "required_skills": req_skills,
                    "work_mode": mode,
                    "mission_statement": mission # Update here
                })
                progress_bar_placeholder = st.empty()
                progress_text_placeholder = st.empty()
                progress_bar_placeholder.progress(0)
                progress_text_placeholder.text("Finding freelancers... 0/10")
                try:
                    results = get_matches(mission, user_type="company")
                    st.session_state.company_matches = results[:10]

                    for i in range(1, 11):
                        progress = i / 10
                        progress_bar_placeholder.progress(progress)
                        progress_text_placeholder.text(f"Finding freelancers... {i}/10")
                        time.sleep(0.05)

                    st.toast("🎉 Freelancers found!", icon="✅")
                    progress_text_placeholder.text(f"Finding freelancers... 10/10 - Done!")
                    st.success(f"{len(st.session_state.company_matches)} freelancers found ✔︎")

                except Exception as e:
                    st.error(f"❌ API error: {e}")
                    st.session_state.company_form_submitted = False
                    progress_bar_placeholder.empty()
                    progress_text_placeholder.empty()

        if st.session_state.company_form_submitted and st.session_state.company_matches:
            for i, f in enumerate(st.session_state.company_matches):
                freelancer_id = f.get("name", f"freelancer_{i}")
                if freelancer_id not in st.session_state.company_email_sent_states:
                    st.session_state.company_email_sent_states[freelancer_id] = {
                        "content": "", "count": 0, "show_modal": False, "sent": False, "show_success_message": False
                    }

                expander_key = f"expander_{freelancer_id}"
                if expander_key not in st.session_state:
                    st.session_state[expander_key] = False

                expander_header_prefix = "✅ " if st.session_state.company_email_sent_states[freelancer_id]["sent"] else "👤 "
                display_freelancer_name = f.get('name')
                if not display_freelancer_name:
                    display_freelancer_name = "Freelancer (Name not provided)"

                with st.expander(
                    f"{expander_header_prefix}{display_freelancer_name} — {f.get('main_sector', '')} — {f.get('city', '')}",
                    expanded=st.session_state[expander_key]
                ):
                    selected_tone = st.multiselect(
                        "🎙️ Choose a tone",
                        ["Warm", "Professional", "Creative", "Direct", "Empathetic"],
                        default=["Professional"],
                        key=f"tone_{freelancer_id}",
                        max_selections=2
                    )
                    st.session_state[expander_key] = True

                    if not st.session_state.company_email_sent_states[freelancer_id]["content"] and \
                       st.session_state.company_email_sent_states[freelancer_id]["count"] == 0:
                        try:
                            sanitized_freelance_data = sanitize_freelancer_data(f)
                            # Use profile data for sender, override statement with form's current value
                            sanitized_prospect_data_sender = sanitize_prospect_data({
                                **st.session_state.user_profile_data, # Use profile as base
                                "company": comp,
                                "company_size": csize,
                                "city": loc,
                                "sector": sector,
                                "mission_statement": mission, # Use the statement from the current form
                                "remote": mode == "Remote",
                                "contact_role": title,
                                "preferred_tone": ", ".join(selected_tone if selected_tone else ["Professional"])
                            })
                            initial_mail = generate_mail(sanitized_freelance_data, sanitized_prospect_data_sender, sender_type="company", previous_mail_content="")
                            st.session_state.company_email_sent_states[freelancer_id]["content"] = initial_mail
                            st.session_state.company_email_sent_states[freelancer_id]["count"] = 1
                        except Exception as e:
                            st.warning(f"⚠️ Initial email generation error for {display_freelancer_name}: {e}")

                    st.caption("✉️ Tone-matched email")
                    st.text_area("tone_matched_email", st.session_state.company_email_sent_states[freelancer_id]["content"], height=180, key=f"textarea_{freelancer_id}")

                    regen_col, validate_col = st.columns([1, 1])
                    with regen_col:
                        if st.button("🔄 Regenerate", key=f"regen_{freelancer_id}"):
                            st.session_state[expander_key] = True
                            st.session_state.company_email_sent_states[freelancer_id]["show_success_message"] = False
                            if st.session_state.company_email_sent_states[freelancer_id]["count"] < 3:
                                try:
                                    sanitized_freelance_data = sanitize_freelancer_data(f)
                                    # Use profile data for sender, override statement with form's current value
                                    sanitized_prospect_data_sender = sanitize_prospect_data({
                                        **st.session_state.user_profile_data, # Use profile as base
                                        "company": comp,
                                        "company_size": csize,
                                        "city": loc,
                                        "sector": sector,
                                        "mission_statement": mission, # Use the statement from the current form
                                        "remote": mode == "Remote",
                                        "contact_role": title,
                                        "preferred_tone": ", ".join(selected_tone if selected_tone else ["Professional"])
                                    })
                                    current_textarea_content = st.session_state.company_email_sent_states[freelancer_id]["content"]
                                    new_mail = generate_mail(sanitized_freelance_data, sanitized_prospect_data_sender, sender_type="company", previous_mail_content=current_textarea_content)
                                    st.session_state.company_email_sent_states[freelancer_id]["content"] = new_mail
                                    st.session_state.company_email_sent_states[freelancer_id]["count"] += 1
                                    st.session_state.company_email_sent_states[freelancer_id]["sent"] = False
                                except Exception as e:
                                    st.warning(f"⚠️ Error: {e}")
                            else:
                                st.warning("⚠️ You’ve reached the limit of email generations. Upgrade to LeadCraftr Pro.")
                    with validate_col:
                        if st.session_state.company_email_sent_states[freelancer_id]["sent"]:
                            st.markdown(
                                f'<button class="stButton css-1y4qm01 sent-button" disabled>✅ Sent!</button>',
                                unsafe_allow_html=True
                            )
                        else:
                            if st.button("✅ Validate this email", key=f"validate_{freelancer_id}"):
                                st.session_state[expander_key] = True
                                st.session_state.company_email_sent_states[freelancer_id]["show_modal"] = True
                                st.session_state.company_email_sent_states[freelancer_id]["show_success_message"] = False

                    if st.session_state.company_email_sent_states[freelancer_id]["show_modal"]:
                        st.markdown("#### ✅ Email ready to send:")
                        st.code(st.session_state.company_email_sent_states[freelancer_id]["content"], language="markdown")
                        if st.button("📤 Send", key=f"send_{freelancer_id}"):
                            st.session_state[expander_key] = True
                            st.session_state.company_email_sent_states[freelancer_id]["show_modal"] = False
                            st.session_state.company_email_sent_states[freelancer_id]["sent"] = True
                            st.session_state.company_email_sent_states[freelancer_id]["show_success_message"] = True

                            # Incrémenter le temps et l'argent économisés (Company)
                            st.session_state.total_time_saved += 5 # Based on research: ~5 mins saved per personalized email drafting
                            st.session_state.total_money_saved += 20 # Based on research: value of personalized copywriting

                            st.toast("Email sent! 🎉", icon="✅")
                            st.rerun()

                    if st.session_state.company_email_sent_states[freelancer_id]["sent"] and st.session_state.company_email_sent_states[freelancer_id]["show_success_message"]:
                        st.success("Your message has been sent successfully!")

# ====== PAGE "CREATE YOUR PROFILE" / "MY PROFILE" ======
elif st.session_state.page in ["📝 Create your profile", "👤 My Profile"]:
    # Ensure sidebar and header are visible
    st.markdown("""
        <style>
        section[data-testid="stSidebar"],
        header[data-testid="stHeader"] {
            display: block !important;
            visibility: visible !important;
            height: auto !important;
        }
        [data-testid="stAppViewContainer"] > .main .block-container {
            max-width: unset !important;
            padding: 1rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.user_type == "freelancer":
        st.markdown("### 📝 Freelancer Profile")
        with st.form("freelancer_profile_form"):
            # Pre-fill with existing data
            current_data = st.session_state.user_profile_data
            first_name = st.text_input("First Name", value=current_data.get("first_name", ""))
            last_name = st.text_input("Last Name", value=current_data.get("last_name", ""))
            email = st.text_input("Email", value=current_data.get("email", ""))
            phone = st.text_input("Phone", value=current_data.get("phone", ""))
            personal_statement = st.text_area("Personal Statement (min 10 chars)", value=current_data.get("personal_statement", ""), height=100)
            desired_job_title = st.text_input("Desired Job Title", value=current_data.get("desired_job_title", ""))
            main_sector = st.selectbox("Main Sector", ["FinTech", "HealthTech", "EdTech", "GreenTech", "Tech / SaaS", "MarTech", "Retail / E-com", "Gaming"], index=["FinTech", "HealthTech", "EdTech", "GreenTech", "Tech / SaaS", "MarTech", "Retail / E-com", "Gaming"].index(current_data.get("main_sector", "Tech / SaaS")))
            skills = st.multiselect("Skills (max 3)", ["Python", "Rust", "Solidity", "Kubernetes", "Cloud Security", "Quant Analysis", "FastAPI", "LangChain", "PostgreSQL"], default=current_data.get("skills", []), max_selections=3)
            experience_years = st.slider("Years of Experience", 0, 30, value=current_data.get("experience_years", 5))
            daily_rate = st.number_input("Desired Daily Rate (€)", min_value=0, value=current_data.get("daily_rate", 500))
            work_mode = st.selectbox("Preferred Work Mode", ["Remote", "On-site", "Hybrid"], index=["Remote", "On-site", "Hybrid"].index(current_data.get("work_mode", "Remote")))
            preferred_company_sizes = st.multiselect("Preferred Company Sizes (max 3)", ["Startup", "Small", "Mid-size", "Large"], default=current_data.get("preferred_company_sizes", []), max_selections=3)
            preferred_email_style = st.selectbox("Preferred Email Style", ["Storytelling", "Direct", "Formal", "Informal", "Benefit-driven", "Technical"], index=["Storytelling", "Direct", "Formal", "Informal", "Benefit-driven", "Technical"].index(current_data.get("preferred_email_style", "Storytelling")))
            desired_monthly_income = st.number_input("Desired Monthly Income (€)", min_value=0, value=current_data.get("desired_monthly_income", 0))
            work_days_per_month = st.slider("Working Days Per Month", 10, 30, value=current_data.get("work_days_per_month", 20))
            safety_buffer = st.slider("Safety Buffer (%)", 0, 100, value=current_data.get("safety_buffer", 20))

            submitted = st.form_submit_button("Save Profile")

            if submitted:
                if len(personal_statement) < 10:
                    st.error("Personal Statement must be at least 10 characters.")
                else:
                    st.session_state.user_profile_data.update({
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "phone": phone,
                        "personal_statement": personal_statement,
                        "desired_job_title": desired_job_title,
                        "main_sector": main_sector,
                        "skills": skills,
                        "experience_years": experience_years,
                        "daily_rate": daily_rate,
                        "work_mode": work_mode,
                        "preferred_company_sizes": preferred_company_sizes,
                        "preferred_email_style": preferred_email_style,
                        "desired_monthly_income": desired_monthly_income,
                        "work_days_per_month": work_days_per_month,
                        "safety_buffer": safety_buffer,
                        "user_type": "freelancer"
                    })
                    st.session_state.profile_created = True
                    st.success("Freelancer profile saved successfully!")
                    st.session_state.page = "👤 My Profile" # Redirect to My Profile view
                    st.rerun()

        if st.session_state.profile_created and st.session_state.user_profile_data.get("user_type") == "freelancer":
            st.markdown("#### Your Freelancer Profile:")
            for key, value in st.session_state.user_profile_data.items():
                if key not in ["user_type", "welcome_message_shown", "freelancer_matches", "freelancer_form_submitted", "company_matches", "company_form_submitted", "freelancer_email_sent_states", "company_email_sent_states", "total_time_saved", "total_money_saved"]:
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
            st.markdown("---")
            display_tjm_calculator()


    elif st.session_state.user_type == "company":
        st.markdown("### 📝 Company Profile")
        with st.form("company_profile_form"):
            # Pre-fill with existing data
            current_data = st.session_state.user_profile_data
            company_name = st.text_input("Company Name", value=current_data.get("company_name", ""))
            contact_person = st.text_input("Main Contact Person", value=current_data.get("contact_person", ""))
            contact_email = st.text_input("Contact Email", value=current_data.get("contact_email", ""))
            contact_phone = st.text_input("Contact Phone", value=current_data.get("contact_phone", ""))
            mission_statement = st.text_area("Mission Statement (min 10 chars)", value=current_data.get("mission_statement", ""), height=100)
            company_size = st.selectbox("Company Size", ["Startup", "SME", "Large Enterprise"], index=["Startup", "SME", "Large Enterprise"].index(current_data.get("company_size", "SME")))
            main_sector = st.selectbox("Main Sector", ["FinTech", "HealthTech", "EdTech", "GreenTech", "Tech / SaaS", "MarTech", "Retail / E-com", "Gaming"], index=["FinTech", "HealthTech", "EdTech", "GreenTech", "Tech / SaaS", "MarTech", "Retail / E-com", "Gaming"].index(current_data.get("main_sector", "Tech / SaaS")))
            required_skills = st.multiselect("Required Freelancer Skills (max 3)", ["Python", "Rust", "Solidity", "Kubernetes", "Cloud Security", "Quant Analysis", "FastAPI", "LangChain", "PostgreSQL"], default=current_data.get("required_skills", []), max_selections=3)
            budget_per_day = st.number_input("Budget Per Day for Freelancers (€)", min_value=0, value=current_data.get("budget_per_day", 500))
            work_mode = st.selectbox("Preferred Work Mode for Freelancers", ["Remote", "On-site", "Hybrid"], index=["Remote", "On-site", "Hybrid"].index(current_data.get("work_mode", "Remote")))
            location = st.text_input("Company Location (City)", value=current_data.get("location", ""))
            target_tone = st.selectbox("Target Email Tone", ["Warm", "Professional", "Creative", "Direct", "Empathetic"], index=["Warm", "Professional", "Creative", "Direct", "Empathetic"].index(current_data.get("target_tone", "Professional")))

            submitted = st.form_submit_button("Save Profile")

            if submitted:
                if len(mission_statement) < 10:
                    st.error("Mission Statement must be at least 10 characters.")
                else:
                    st.session_state.user_profile_data.update({
                        "company_name": company_name,
                        "contact_person": contact_person,
                        "contact_email": contact_email,
                        "contact_phone": contact_phone,
                        "mission_statement": mission_statement,
                        "company_size": company_size,
                        "main_sector": main_sector,
                        "required_skills": required_skills,
                        "budget_per_day": budget_per_day,
                        "work_mode": work_mode,
                        "location": location,
                        "target_tone": target_tone,
                        "user_type": "company"
                    })
                    st.session_state.profile_created = True
                    st.success("Company profile saved successfully!")
                    st.session_state.page = "👤 My Profile" # Redirect to My Profile view
                    st.rerun()

        if st.session_state.profile_created and st.session_state.user_profile_data.get("user_type") == "company":
            st.markdown("#### Your Company Profile:")
            for key, value in st.session_state.user_profile_data.items():
                if key not in ["user_type", "welcome_message_shown", "freelancer_matches", "freelancer_form_submitted", "company_matches", "company_form_submitted", "freelancer_email_sent_states", "company_email_sent_states", "total_time_saved", "total_money_saved"]: # Exclude internal state variables
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")

# ====== STANDALONE TJM CALCULATOR PAGE ======
elif st.session_state.page == "🧮 Calculate your daily rate":
    st.markdown("""
        <style>
        section[data-testid="stSidebar"],
        header[data-testid="stHeader"] {
            display: block !important;
            visibility: visible !important;
            height: auto !important;
        }
        [data-testid="stAppViewContainer"] > .main .block-container {
            max-width: unset !important;
            padding: 1rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    display_tjm_calculator()

# ====== DASHBOARD PAGE ======
elif st.session_state.page == "📊 Dashboard":
    st.markdown("""
        <style>
        section[data-testid="stSidebar"],
        header[data-testid="stHeader"] {
            display: block !important;
            visibility: visible !important;
            height: auto !important;
        }
        [data-testid="stAppViewContainer"] > .main .block-container {
            max-width: unset !important;
            padding: 1rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("### 📊 Your Dashboard")
    st.markdown("---")

    # Affichage des métriques globales ici aussi
    st.subheader("🚀 Overall Impact with LeadCraftr")
    col_dash1, col_dash2 = st.columns(2)
    with col_dash1:
        st.metric(label="🕰️ Total Time Saved", value=f"{st.session_state.total_time_saved} min")
    with col_dash2:
        st.metric(label="💰 Total Money Saved", value=f"€{st.session_state.total_money_saved:.2f}")
    # The info message is now ONLY on the Dashboard page
    st.info("💡 *Time and money saved estimates are based on your daily rate, assuming 8 hours of work per day."
            "Reduced weekly prospecting time from 2.5 hours to less than 20 minutes with LeadCraftr.*")

    st.subheader("✉️ Recent Interactions")

    if st.session_state.user_type == "freelancer":
        recent_interactions_count = 0
        for freelancer_id, data in st.session_state.freelancer_email_sent_states.items():
            if data["sent"]: # Check if sent
                st.success(f"✅ Email sent to **{freelancer_id}** — {time.strftime('%d %B')}")
                recent_interactions_count += 1

        if recent_interactions_count == 0:
            st.info("No recent interactions yet. Generate and send some emails to see them here!")

    elif st.session_state.user_type == "company":
        recent_interactions_count = 0
        for freelancer_id, data in st.session_state.company_email_sent_states.items():
            if data["sent"]: # Check if sent
                st.success(f"✅ Email sent to **{freelancer_id}** — {time.strftime('%d %B')}")
                recent_interactions_count += 1

        if recent_interactions_count == 0:
            st.info("No recent interactions yet. Generate and send some emails to see them here!")


    st.markdown("---")
    st.markdown("### 📈 Activity Summary")
    st.markdown("🕒 Last login: Today, 08:46 AM (Simulated)")
    st.markdown("📆 Total sessions this week: **15** (Simulated)")
    st.markdown("💼 Most contacted sector: **Tech / SaaS** (Simulated)")
    st.markdown("🎙️ Most used tone: **Professional** (Simulated)")

# ---------- FOOTER ----------
st.markdown("---")
st.caption("LeadCraftr · Demo front-end with API integration")
st.caption("Crafted with Love for freelancers & businesses · © 2025 LeadCraftr")
