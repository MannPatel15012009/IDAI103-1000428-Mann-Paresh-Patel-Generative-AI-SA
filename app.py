import streamlit as st
import google.generativeai as genai
import traceback
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="CoachBot AI - Smart Sports Assistant",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Initialization ---
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'generated_plans' not in st.session_state:
    st.session_state.generated_plans = {}
if 'error_log' not in st.session_state:
    st.session_state.error_log = []
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

# --- Sport Data Configuration ---
SPORT_DATA = {
    "cricket": {
        "positions": ["Batsman", "Fast Bowler", "Spin Bowler", "Wicket-Keeper", "All-rounder"],
        "common_injuries": ["Hamstring strain", "Shoulder impingement", "Lower back pain", "Ankle sprain", "Rotator cuff tear"],
    },
    "kabaddi": {
        "positions": ["Raider", "Corner Defender", "Cover Defender", "All-rounder"],
        "common_injuries": ["Knee ligament tear", "Ankle sprain", "Shoulder dislocation", "Concussion", "Groin strain"],
    },
    "volleyball": {
        "positions": ["Setter", "Outside Hitter", "Middle Blocker", "Opposite", "Libero"],
        "common_injuries": ["Jumper's knee", "Ankle sprain", "Shoulder pain", "Rotator cuff injury", "Finger injury"],
    },
    "football": {
        "positions": ["Forward", "Midfielder", "Defender", "Goalkeeper"],
        "common_injuries": ["ACL tear", "Hamstring strain", "Ankle sprain", "Meniscus tear"],
    },
    "basketball": {
        "positions": ["Point Guard", "Shooting Guard", "Small Forward", "Power Forward", "Center"],
        "common_injuries": ["Ankle sprain", "ACL tear", "Jumper's knee", "Achilles tendonitis"],
    }
}

# --- Helper Functions ---
def log_error(context, error):
    """Log errors to session state for debugging"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_msg = str(error)
    details = traceback.format_exc()
    st.session_state.error_log.append({
        'timestamp': timestamp,
        'context': context,
        'message': error_msg,
        'details': details
    })
    print(f"[{timestamp}] ERROR in {context}: {error_msg}")

# --- AI Core Class ---
class CoachBotAI:
    def __init__(self):
        """Initialize and Authenticate Gemini AI"""
        try:
            # 1. Get API Key from secrets
            if "GEMINI_API_KEY" not in st.secrets:
                st.error("⚠️ API Key missing! Please set GEMINI_API_KEY in .streamlit/secrets.toml")
                st.stop()
            
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)

            # 2. Select Model (Using Gemini 3 Flash Preview for speed and reliability)
            self.model_name = "gemini-3-flash-preview"
            self.model = genai.GenerativeModel(self.model_name)
            
        except Exception as e:
            log_error("AI Init", e)
            st.error("Failed to connect to AI server. Please check your API key.")
            st.stop()

    def generate_content(self, prompt, max_tokens=2000, temp=0.4):
        """Wrapper for content generation with retry logic"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temp,
                    "top_p": 0.8,
                    "max_output_tokens": max_tokens
                }
            )
            return response.text
        except Exception as e:
            log_error("Content Generation", e)
            raise Exception(f"AI Generation failed: {str(e)}")

    def create_personalized_plan(self, user_data):
        """Generate Workout Plan"""
        
        # Branch logic for injury
        if user_data.get('current_injury') and user_data['current_injury'] != "None":
            context = f"INJURED ATHLETE: {user_data['current_injury']} ({user_data.get('injury_duration')})"
            safety_instruction = "Creating a REHAB-FOCUSED plan. Avoid aggravating exercises. Focus on recovery and maintenance."
        else:
            context = "HEALTHY ATHLETE"
            safety_instruction = "Create a standard performance improvement plan."

        prompt = f"""
        Act as an elite sports performance coach. Create a 4-week training plan.
        
        **ATHLETE PROFILE:**
        - Sport: {user_data['sport'].upper()} ({user_data['position']})
        - Status: {context}
        - Age/Gender: {user_data['age']} / {user_data['gender']}
        - Experience: {user_data['experience']} years
        - Level: {user_data['fitness_level']}
        - Schedule: {user_data['training_days']} days/week
        - Goals: {', '.join(user_data['goals'])}
        
        **INSTRUCTIONS:**
        {safety_instruction}
        
        **REQUIRED OUTPUT FORMAT (Markdown):**
        1. **Executive Summary**: Brief analysis of their profile.
        2. **Weekly Focus**: What is the goal of Week 1-2 vs Week 3-4.
        3. **The Schedule**:
           - Break down Day 1, Day 2, etc. (matching {user_data['training_days']} days/week).
           - Include specific drills/exercises, sets, and reps.
           - Include Warm-up and Cool-down.
        4. **Recovery Protocol**: Specific recovery methods.
        """
        return self.generate_content(prompt, temp=0.3)

    def generate_nutrition_plan(self, user_data):
        """Generate Nutrition Plan"""
        
        # Format dietary restrictions
        restrictions = user_data.get('dietary_restrictions', [])
        if user_data.get('rare_allergies'):
            restrictions.append(f"ALLERGY: {user_data['rare_allergies']}")
        
        diet_str = ", ".join(restrictions) if restrictions else "None"

        prompt = f"""
        Act as a Sports Nutritionist. Create a 7-day meal plan.
        
        **ATHLETE PROFILE:**
        - Sport: {user_data['sport']}
        - Stats: {user_data['height']}cm, {user_data['weight']}kg, {user_data['gender']}
        - Goals: {', '.join(user_data['goals'])}
        - Dietary Restrictions: {diet_str}
        
        **REQUIREMENTS:**
        1. Calculate approximate daily Calorie and Macro targets based on stats.
        2. Provide a 7-day plan (Breakfast, Lunch, Dinner, Snacks).
        3. Specifically mention Pre-workout and Post-workout nutrition timing.
        4. Include a shopping list for the week.
        """
        return self.generate_content(prompt, temp=0.4)

    def generate_tactical_advice(self, user_data):
        """Generate Tactical Advice"""
        prompt = f"""
        Act as a veteran coach for {user_data['sport']}. Provide tactical advice for a {user_data['position']}.
        
        **CONTEXT:**
        - Experience Level: {user_data['experience']} years
        - Competition Level: {user_data['competition_level']}
        
        **PROVIDE:**
        1. **Role Mastery**: Key responsibilities of this position.
        2. **Game IQ**: Situational decision making scenarios.
        3. **Mental Game**: How to handle pressure in this specific position.
        4. **Common Mistakes**: What do players at this level usually do wrong?
        """
        return self.generate_content(prompt, temp=0.5)

# --- UI Components ---

def sidebar_form():
    """Render the input form"""
    with st.sidebar:
        st.header("👤 Athlete Profile")
        
        # 1. Sport & Position
        sport = st.selectbox("Sport", list(SPORT_DATA.keys()), format_func=lambda x: x.title())
        position = st.selectbox("Position", SPORT_DATA[sport]["positions"])
        
        # 2. Bio
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 10, 60, 20)
            height = st.text_input("Height (cm)", "175")
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            weight = st.text_input("Weight (kg)", "70")

        # 3. Stats
        experience = st.slider("Experience (Years)", 0, 20, 2)
        level = st.select_slider("Fitness Level", options=["Beginner", "Intermediate", "Advanced", "Elite"], value="Intermediate")
        training_days = st.slider("Training Days/Week", 1, 7, 4)
        comp_level = st.selectbox("Competition Level", ["Recreational", "School/College", "Amateur Club", "Semi-Pro", "Professional"])

        # 4. Goals & Health
        goals = st.multiselect("Goals", ["Strength", "Speed", "Stamina", "Muscle Gain", "Fat Loss", "Skill"], default=["Strength", "Skill"])
        
        with st.expander("🚑 Injury Status", expanded=False):
            injury_list = ["None"] + SPORT_DATA[sport]["common_injuries"] + ["Other"]
            current_injury = st.selectbox("Current Injury", injury_list)
            injury_duration = ""
            if current_injury != "None":
                injury_duration = st.selectbox("Duration", ["< 2 weeks", "1 month", "> 3 months"])
        
        with st.expander("🥗 Diet & Allergies", expanded=False):
            dietary_restrictions = []
            if st.checkbox("Vegetarian"): dietary_restrictions.append("Vegetarian")
            if st.checkbox("Vegan"): dietary_restrictions.append("Vegan")
            if st.checkbox("Gluten-Free"): dietary_restrictions.append("Gluten-Free")
            if st.checkbox("Lactose-Free"): dietary_restrictions.append("Lactose-Free")
            rare_allergies = st.text_input("Specific Allergies (e.g., Peanuts)")

        st.markdown("---")
        submitted = st.button("🚀 Generate Plan", type="primary", use_container_width=True)
        
        if submitted:
            # Save to session state
            st.session_state.user_profile = {
                'sport': sport, 'position': position, 'age': age, 'gender': gender,
                'height': height, 'weight': weight, 'experience': experience,
                'fitness_level': level, 'training_days': training_days,
                'competition_level': comp_level, 'goals': goals,
                'current_injury': current_injury, 'injury_duration': injury_duration,
                'dietary_restrictions': dietary_restrictions, 'rare_allergies': rare_allergies
            }
            return True
    return False

def main():
    st.title("🏃‍♂️ CoachBot AI")
    st.caption(f"Powered by Google Gemini 1.5 Flash • {datetime.now().strftime('%Y')}")

    # Render Sidebar
    generate_clicked = sidebar_form()
    
    # Welcome Screen if no profile
    if not st.session_state.user_profile:
        st.info("👈 Please fill out your profile in the sidebar to get started.")
        st.markdown("""
        ### What can CoachBot do?
        * **🏋️ Training:** Periodized workout plans specific to your sport.
        * **🚑 Rehab:** Modified plans if you are currently injured.
        * **🥦 Nutrition:** Meal plans tailored to your body type and preferences.
        * **🧠 Tactics:** Strategic advice for your specific position on the field.
        """)
        return

    # Initialize AI
    coach = CoachBotAI()

    # Create Tabs
    tab_train, tab_food, tab_tactics = st.tabs(["🏋️ Training", "🥦 Nutrition", "🧠 Tactics"])
    
    profile = st.session_state.user_profile
    
    # --- Tab 1: Training ---
    with tab_train:
        plan_id = f"train_{profile['sport']}_{profile['position']}_{profile['current_injury']}"
        
        # Generate if clicked or not exists
        if generate_clicked or plan_id not in st.session_state.generated_plans:
            with st.spinner("Analyzing profile and building workout routine..."):
                try:
                    plan = coach.create_personalized_plan(profile)
                    st.session_state.generated_plans[plan_id] = plan
                except Exception as e:
                    st.error(f"Error generating plan: {e}")
        
        if plan_id in st.session_state.generated_plans:
            st.markdown(st.session_state.generated_plans[plan_id])
            st.download_button("📥 Download Plan", st.session_state.generated_plans[plan_id], file_name="training_plan.md")

    # --- Tab 2: Nutrition ---
    with tab_food:
        nutri_id = f"nutri_{profile['sport']}_{profile['weight']}"
        
        if st.button("Generate Nutrition Plan", key="btn_nutri") or (generate_clicked and nutri_id not in st.session_state.generated_plans):
            with st.spinner("Calculating macros and meal planning..."):
                try:
                    plan = coach.generate_nutrition_plan(profile)
                    st.session_state.generated_plans[nutri_id] = plan
                except Exception as e:
                    st.error(f"Error generating nutrition: {e}")

        if nutri_id in st.session_state.generated_plans:
            st.markdown(st.session_state.generated_plans[nutri_id])

    # --- Tab 3: Tactics ---
    with tab_tactics:
        tac_id = f"tac_{profile['sport']}_{profile['position']}"
        
        if st.button("Generate Tactical Advice", key="btn_tac") or (generate_clicked and tac_id not in st.session_state.generated_plans):
            with st.spinner("Analyzing game strategies..."):
                try:
                    plan = coach.generate_tactical_advice(profile)
                    st.session_state.generated_plans[tac_id] = plan
                except Exception as e:
                    st.error(f"Error generating tactics: {e}")

        if tac_id in st.session_state.generated_plans:
            st.markdown(st.session_state.generated_plans[tac_id])

    # --- Debug Footer ---
    if st.session_state.debug_mode:
        with st.expander("Debug Logs"):
            st.write(st.session_state.error_log)

if __name__ == "__main__":
    main()
