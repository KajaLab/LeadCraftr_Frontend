
"""daily_rate_page_NEW.py

Full‑featured Daily‑Rate (TJM) calculator page for LeadCraftr.

Drop this file next to **app_V4.py** and add, near the top of *app_V4.py*:

    from daily_rate_page import display_tjm_calculator

Then, inside the block that checks:

    if st.session_state.page == "🧮 Calculate your daily rate":

simply call:
    display_tjm_calculator()

The function will completely replace the old, simplified TJM page.
"""

import streamlit as st


def _calculate_rate(years_experience,
                    skill_level, specialization, location_type,
                    market_location, industry, certifications,
                    education, demand_level, business_impact,
                    urgency_premium, client_size, portfolio_strength):
    """Pure helper – returns an integer daily‑rate rounded to €25."""
    base_rate = 300

    experience_multipliers = {
        0: 0.6, 1: 0.7, 2: 0.8, 3: 0.9, 4: 1.0,
        5: 1.1, 6: 1.2, 7: 1.3, 8: 1.4, 9: 1.5,
        10: 1.6, 11: 1.7, 12: 1.8, 13: 1.9, 14: 2.0,
        15: 2.1, 16: 2.2, 17: 2.3, 18: 2.4, 19: 2.5, 20: 2.6
    }

    skill_adjustments = {
        "Junior": 0.8,
        "Mid-level": 1.0,
        "Senior": 1.3,
        "Expert/Lead": 1.6
    }

    specialization_adjustments = {
        "General Development": 1.0,
        "Frontend Development": 1.1,
        "Backend Development": 1.2,
        "Full-stack Development": 1.3,
        "Data Science/ML": 1.5,
        "DevOps/Cloud": 1.4,
        "Mobile Development": 1.2,
        "UI/UX Design": 1.1,
        "Project Management": 1.2,
        "Consulting": 1.4
    }

    location_adjustments = {
        "France (Paris)": 1.2,
        "France (Other cities)": 1.0,
        "Germany": 1.3,
        "UK": 1.4,
        "Netherlands": 1.3,
        "Switzerland": 1.8,
        "USA": 1.6,
        "Global/Remote": 1.1
    }

    industry_adjustments = {
        "Tech/SaaS": 1.2,
        "Finance/Banking": 1.4,
        "Healthcare": 1.1,
        "E-commerce": 1.1,
        "Media/Entertainment": 0.9,
        "Consulting": 1.3,
        "Government": 0.8,
        "General": 1.0
    }

    demand_adjustments = {
        "Low": 0.8,
        "Medium": 1.0,
        "High": 1.2,
        "Very High": 1.4
    }

    business_adjustments = {
        "Low": 0.9,
        "Medium": 1.0,
        "High": 1.2,
        "Critical": 1.4
    }

    client_adjustments = {
        "Startup": 0.8,
        "Small Business": 0.9,
        "Mid-size Company": 1.0,
        "Large Enterprise": 1.3
    }

    portfolio_adjustments = {
        "Basic": 0.9,
        "Good": 1.0,
        "Strong": 1.1,
        "Exceptional": 1.3
    }

    rate = base_rate * experience_multipliers.get(years_experience, 2.6)
    rate *= skill_adjustments[skill_level]
    rate *= specialization_adjustments[specialization]
    rate *= location_adjustments[market_location]
    rate *= industry_adjustments[industry]

    if certifications:
        rate *= 1.1

    if education in ["Master's Degree", "PhD"]:
        rate *= 1.1

    rate *= demand_adjustments[demand_level]
    rate *= business_adjustments[business_impact]

    if urgency_premium:
        rate *= 1.2

    rate *= client_adjustments[client_size]
    rate *= portfolio_adjustments[portfolio_strength]

    return int(round(rate / 25.0) * 25)


def display_tjm_calculator():
    """Render the rich Daily‑Rate calculator as a full page."""

    if st.session_state.get("user_type", "freelancer") != "freelancer":
        st.warning("This tool is designed for freelancers. Switch to freelancer mode in your profile settings.")
        return

    st.markdown("## 💰 Daily‑Rate (TJM) Calculator")
    st.markdown("Calculate your optimal daily rate based on your experience, skills, and market conditions.")

    with st.form("rate_calculator_full", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Experience & Skills")
            years_experience = st.slider("Years of Experience", 0, 20, 5)
            skill_level = st.selectbox("Skill Level", ["Junior", "Mid-level", "Senior", "Expert/Lead"], index=2)
            specialization = st.selectbox(
                "Specialization",
                ["General Development", "Frontend Development", "Backend Development", "Full-stack Development",
                 "Data Science/ML", "DevOps/Cloud", "Mobile Development", "UI/UX Design",
                 "Project Management", "Consulting"], index=0)
            education = st.selectbox(
                "Education Level",
                ["High School", "Bachelor's Degree", "Master's Degree", "PhD", "Self-taught"], index=1)
            certifications = st.checkbox("Professional Certifications")

        with col2:
            st.markdown("### Market & Location")
            location_type = st.selectbox("Work Location", ["Remote", "On-site", "Hybrid"], index=0)
            market_location = st.selectbox(
                "Target Market",
                ["France (Paris)", "France (Other cities)", "Germany", "UK", "Netherlands",
                 "Switzerland", "USA", "Global/Remote"], index=0)
            industry = st.selectbox(
                "Industry Focus",
                ["Tech/SaaS", "Finance/Banking", "Healthcare", "E-commerce", "Media/Entertainment",
                 "Consulting", "Government", "General"], index=0)
            project_type = st.selectbox(
                "Typical Project Type",
                ["Short-term (< 3 months)", "Medium-term (3-6 months)", "Long-term (6+ months)"], index=1)
            demand_level = st.selectbox("Skills Demand Level", ["Low", "Medium", "High", "Very High"], index=2)

        st.markdown("### Additional Factors")
        col3, col4 = st.columns(2)

        with col3:
            business_impact = st.selectbox("Business Impact", ["Low", "Medium", "High", "Critical"], index=2)
            urgency_premium = st.checkbox("Urgency Premium", help="Often work on urgent projects?")

        with col4:
            client_size = st.selectbox("Typical Client Size",
                                       ["Startup", "Small Business", "Mid-size Company", "Large Enterprise"], index=2)
            portfolio_strength = st.selectbox("Portfolio Strength",
                                              ["Basic", "Good", "Strong", "Exceptional"], index=2)

        submitted = st.form_submit_button("Calculate My Daily Rate")

    if submitted:
        tjm = _calculate_rate(years_experience, skill_level, specialization,
                              location_type, market_location, industry,
                              certifications, education, demand_level,
                              business_impact, urgency_premium,
                              client_size, portfolio_strength)

        st.session_state["freelancer_tjm"] = tjm

        if st.session_state.get("profile_created") and "daily_rate" in st.session_state.get("user_profile_data", {}):
            st.session_state.user_profile_data["daily_rate"] = tjm

    if st.session_state.get("freelancer_tjm"):
        tjm = st.session_state.freelancer_tjm
        st.markdown("---")
        st.markdown("### 📊 Your Calculated Rate")
        st.metric("Recommended Daily Rate", f"€{tjm}")
        st.metric("Monthly (20 d)", f"€{tjm * 20:,}")
        st.metric("Yearly (11 m)", f"€{tjm * 20 * 11:,}")
        st.caption("*Figures assume 20 billable days/month & 11 working months/year.*")

         # Rate range recommendation
        st.markdown("### 💡 Rate Range Recommendation")

        min_rate = int(st.session_state.freelancer_tjm * 0.8)
        max_rate = int(st.session_state.freelancer_tjm * 1.2)

        st.info(f"""
        **Suggested Rate Range: €{min_rate} - €{max_rate} per day**

        - **Minimum Rate (€{min_rate})**: For long-term projects, preferred clients, or when building relationships
        - **Standard Rate (€{st.session_state.freelancer_tjm})**: Your go-to rate for most projects
        - **Premium Rate (€{max_rate})**: For urgent projects, complex work, or high-value clients
        """)

        # Tips section
        st.markdown("### 📈 Tips to Increase Your Rate")

        tips = [
            "📚 **Continuous Learning**: Stay updated with latest technologies and trends",
            "🏆 **Build Strong Portfolio**: Showcase your best work and case studies",
            "🎯 **Specialize**: Become an expert in high-demand, high-value skills",
            "💼 **Target Premium Clients**: Focus on clients who value quality over price",
            "📊 **Track Results**: Document the business impact of your work",
            "🤝 **Network**: Build relationships in your industry",
            "💬 **Testimonials**: Collect and showcase client testimonials",
            "⚡ **Efficiency**: Improve your speed and quality of delivery"
        ]
        for tip in tips:
            st.markdown(f"- {tip}")
