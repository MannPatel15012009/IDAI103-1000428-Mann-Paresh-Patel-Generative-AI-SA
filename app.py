import streamlit as st
import google.generativeai as genai
import traceback
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="NextGen Sports Lab - Smart Sports Assistant",
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
class NextGen_Sports_Lab:
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
        calorie_goal = user_data.get('calorie_goal', 'Calculate based on stats')

        prompt = f"""
        Act as a Sports Nutritionist. Create a 7-day meal plan.
        
        **ATHLETE PROFILE:**
        - Sport: {user_data['sport']}
        - Stats: {user_data['height']}cm, {user_data['weight']}kg, {user_data['gender']}
        - Goals: {', '.join(user_data['goals'])}
        - Dietary Restrictions & Allergies: {diet_str}
        - Target Daily Calories: {calorie_goal} kcal
        
        **REQUIREMENTS:**
        1. Base the meal plan on the target daily calories ({calorie_goal} kcal) and calculate appropriate Macro targets.
        2. Provide a 7-day plan (Breakfast, Lunch, Dinner, Snacks) strictly adhering to the dietary restrictions: {diet_str}.
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
    def generate_warmup_cooldown(self, user_data):
        """Generate Warm-up and Cooldown Routine"""
        prompt = f"""
        Act as an athletic trainer. Generate a personalized warm-up and cooldown routine for a {user_data['sport']} {user_data['position']}.
        
        **CONTEXT:**
        - Current Injury: {user_data['current_injury']}
        - Training Intensity Preference: {user_data.get('intensity', 'Moderate')}
        
        **PROVIDE:**
        1. A 15-minute dynamic warm-up specific to the movements of a {user_data['position']}.
        2. A 10-minute cooldown focusing on injury prevention and flexibility.
        Ensure all exercises are safe considering the athlete's current injury status.
        """
        return self.generate_content(prompt, temp=0.3)

    def generate_mental_focus(self, user_data):
        """Generate Mental Focus and Visualization Strategy"""
        prompt = f"""
        Act as a Sports Psychologist. Create a mental focus and pre-match visualization routine for a {user_data['sport']} {user_data['position']}.
        
        **CONTEXT:**
        - Competition Level: {user_data['competition_level']}
        - Experience: {user_data['experience']} years
        
        **PROVIDE:**
        1. Pre-match visualization techniques specifically for a {user_data['position']}.
        2. Breathing exercises to manage tournament anxiety.
        3. Strategies to maintain focus after making a mistake during a game.
        """
        return self.generate_content(prompt, temp=0.6)

    def generate_hydration_strategy(self, user_data):
        """Generate Hydration and Electrolyte Strategy"""
        prompt = f"""
        Act as a Sports Nutritionist. Provide a daily hydration and electrolyte strategy for a {user_data['sport']} athlete.
        
        **CONTEXT:**
        - Weight: {user_data['weight']}kg
        - Training Days: {user_data['training_days']} days/week
        - Training Style: {user_data.get('style', 'Standard')}
        
        **PROVIDE:**
        1. Daily baseline water intake recommendations.
        2. Pre-, intra-, and post-training hydration schedule.
        3. Natural electrolyte replacement suggestions suitable for a youth athlete.
        """
        return self.generate_content(prompt, temp=0.4)    

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
        st.markdown("---")
        st.subheader("⚙️ Training Preferences")
        intensity = st.select_slider("Training Intensity", options=["Low", "Moderate", "High", "Maximum"])
        style = st.selectbox("Training Style", ["Endurance Focus", "Explosive Power", "Hypertrophy", "Agility & Speed"])
        # 4. Goals & Health
        goals = st.multiselect("Goals", ["Strength", "Speed", "Stamina", "Muscle Gain", "Fat Loss", "Skill"], default=["Strength", "Skill"])
        
        with st.expander("🚑 Injury Status", expanded=False):
            injury_list = ["None"] + SPORT_DATA[sport]["common_injuries"] + ["Other"]
            current_injury = st.selectbox("Current Injury", injury_list)
            injury_duration = ""
            if current_injury != "None":
                injury_duration = st.selectbox("Duration", ["< 2 weeks", "1 month", "> 3 months"])
        
        with st.expander("🥗 Diet & Allergies", expanded=False):
            calorie_goal = st.number_input("Daily Calorie Goal (kcal)", min_value=1200, max_value=5000, value=2500, step=100)
            dietary_restrictions = []
            if st.checkbox("Vegetarian"): dietary_restrictions.append("Vegetarian")
            if st.checkbox("Vegan"): dietary_restrictions.append("Vegan")
            if st.checkbox("Gluten-Free"): dietary_restrictions.append("Gluten-Free")
            if st.checkbox("Lactose-Free"): dietary_restrictions.append("Lactose-Free")
            rare_allergies = st.text_input("Specific Allergies (e.g., Peanuts)")
        st.markdown("---")
        st.subheader("💬 Custom AI Request (Optional)")
        st.write("Test specific scenarios for your assignment.")
        
        # The 15 Sample Prompts
       sample_prompts = 
       [
            "✏️ Write my own custom prompt...",
            "Design a 4-week explosive power program for a Basketball Power Forward entering the pre-season.",
            "Create a 3-week agility and speed routine for a Football Midfielder focusing on quick directional changes.",
            "Suggest a modified Volleyball workout that avoids aggravating a rotator cuff injury while maintaining cardiovascular endurance.",
            "Outline a safe return-to-play progression for a Kabaddi Raider recovering from a mild ankle sprain.",
            "Provide a pre-match routine focusing on anxiety management for a Football Goalkeeper facing a high-pressure tournament.",
            "Recommend visualization techniques and focus strategies for a Cricket Batsman struggling with early-innings nerves.",
            "Outline a game-day hydration strategy for a Cricket Fast Bowler playing in hot and humid conditions.",
            "Suggest a tournament-day nutrition timeline for a Volleyball Middle Blocker playing three matches in one weekend.",
            "What are the best drills to improve reaction time for a Kabaddi Corner Defender with beginner-level experience?",
            "Break down advanced spatial awareness and off-ball movement tactics for a Basketball Point Guard.",
            "Create a 3000 kcal daily meal plan for a Football Defender strictly following a vegan diet.",
            "Develop a high-protein, gluten-free meal plan for a Volleyball Setter aiming to build muscle mass.",
            "Generate a 15-minute dynamic warm-up routine focusing on hip mobility and hamstring activation for a Football Striker.",
            "Design a 10-minute post-match cooldown routine focusing on shoulder flexibility and recovery for a Cricket Spin Bowler.",
            "Combine a high-intensity stamina workout with a post-workout recovery meal plan for a Basketball Shooting Guard."
        ]
        
        selected_prompt = st.selectbox("Choose a structured prompt:", sample_prompts)
        
        if selected_prompt == "✏️ Write my own custom prompt...":
            final_custom_prompt = st.text_area(
                "Enter your custom prompt:", 
                placeholder="e.g., 'A 14-year-old female midfielder...'"
            )
        else:
            final_custom_prompt = selected_prompt
            st.info(f"**Selected:** {final_custom_prompt}")    

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
                'dietary_restrictions': dietary_restrictions, 'rare_allergies': rare_allergies,
                'intensity': intensity, 'style': style, 'calorie_goal': calorie_goal,
                'custom_prompt': final_custom_prompt
            }
        return True
    return False

def main():
    st.title("🏃‍♂️ NextGen Sports Lab")
    st.caption(f"Powered by Google Gemini 1.5 Flash • {datetime.now().strftime('%Y')}")

    # Render Sidebar
    generate_clicked = sidebar_form()
    
    # Welcome Screen if no profile
    if not st.session_state.user_profile:
        st.info("👈 Please fill out your profile in the sidebar to get started.")
        st.markdown("""
        ### What can NextGen Sports Lab do?
        * **🏋️ Training:** Periodized workout plans specific to your sport.
        * **🚑 Rehab:** Modified plans if you are currently injured.
        * **🥦 Nutrition:** Meal plans tailored to your body type and preferences.
        * **🧠 Tactics:** Strategic advice for your specific position on the field.
        """)
        return

    # Initialize AI
    coach = NextGen_Sports_Lab()

    # Create Tabs
  # Create Tabs
    tab_train, tab_food, tab_tactics, tab_warmup, tab_mental, tab_hydro, tab_custom = st.tabs([
        "🏋️ Training", "🥦 Nutrition", "🧠 Tactics", "🧘 Warm-up", "🧘‍♂️ Mental Focus", "💧 Hydration", "💬 Custom Prompt"
    ])
    
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
        # Create a string representation of the diets and allergies to make the cache ID unique
        diet_str = "_".join(profile.get('dietary_restrictions', []))
        allergy_str = profile.get('rare_allergies', '').replace(" ", "_")
        
        # Update the ID to include diets, allergies, and calorie goal
        nutri_id = f"nutri_{profile['sport']}_{profile['weight']}_{diet_str}_{allergy_str}_{profile.get('calorie_goal', '')}"
        
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
    # --- Tab 4: Warm-up & Cooldown ---
    with tab_warmup:
        warmup_id = f"warmup_{profile['sport']}_{profile['position']}_{profile['current_injury']}"
        
        if st.button("Generate Warm-up Routine", key="btn_warmup") or (generate_clicked and warmup_id not in st.session_state.generated_plans):
            with st.spinner("Designing safe warm-up and cooldown..."):
                try:
                    plan = coach.generate_warmup_cooldown(profile)
                    st.session_state.generated_plans[warmup_id] = plan
                except Exception as e:
                    st.error(f"Error generating routine: {e}")

        if warmup_id in st.session_state.generated_plans:
            st.markdown(st.session_state.generated_plans[warmup_id])

    # --- Tab 5: Mental Focus ---
    with tab_mental:
        mental_id = f"mental_{profile['sport']}_{profile['position']}"
        
        if st.button("Generate Mental Strategy", key="btn_mental") or (generate_clicked and mental_id not in st.session_state.generated_plans):
            with st.spinner("Preparing visualization techniques..."):
                try:
                    plan = coach.generate_mental_focus(profile)
                    st.session_state.generated_plans[mental_id] = plan
                except Exception as e:
                    st.error(f"Error generating mental strategy: {e}")

        if mental_id in st.session_state.generated_plans:
            st.markdown(st.session_state.generated_plans[mental_id])

    # --- Tab 6: Hydration ---
    with tab_hydro:
        hydro_id = f"hydro_{profile['weight']}_{profile['training_days']}"
        
        if st.button("Generate Hydration Plan", key="btn_hydro") or (generate_clicked and hydro_id not in st.session_state.generated_plans):
            with st.spinner("Calculating fluid requirements..."):
                try:
                    plan = coach.generate_hydration_strategy(profile)
                    st.session_state.generated_plans[hydro_id] = plan
                except Exception as e:
                    st.error(f"Error generating hydration plan: {e}")

        if hydro_id in st.session_state.generated_plans:
            st.markdown(st.session_state.generated_plans[hydro_id])
  # --- Tab 7: Custom Prompt ---
    with tab_custom:
        custom_query = profile.get('custom_prompt', "")
        
        # Create a unique ID for this specific prompt so we don't re-generate it unnecessarily
        custom_id = f"custom_{hash(custom_query)}" 
        
        if custom_query and custom_query != "✏️ Write my own custom prompt...":
            if st.button("Generate Custom Response", key="btn_custom") or (generate_clicked and custom_id not in st.session_state.generated_plans):
                with st.spinner("Analyzing custom request..."):
                    try:
                        context_str = f"""
                        **SYSTEM INSTRUCTION:** You are NextGen Sports Lab. Respond to the user's prompt below. 
                        Ensure your advice aligns with their specific sport, age, injury status, and goals.
                        
                        **USER PROMPT:** {custom_query}
                        """
                        # Generate the response
                        plan = coach.generate_content(context_str, temp=0.5)
                        st.session_state.generated_plans[custom_id] = plan
                    except Exception as e:
                        st.error(f"Error generating response: {e}")

            if custom_id in st.session_state.generated_plans:
                st.markdown("### 💬 NextGen Sports Lab's Custom Response")
                st.success(f"**Your Prompt:** {custom_query}")
                st.markdown(st.session_state.generated_plans[custom_id])
        else:
            st.info("👈 Please enter or select a custom prompt in the sidebar, then click 'Generate Plan' to see the response here.")       
    # --- Debug Footer ---
    if st.session_state.debug_mode:
        with st.expander("Debug Logs"):
            st.write(st.session_state.error_log)
            
   
if __name__ == "__main__":
    main()
