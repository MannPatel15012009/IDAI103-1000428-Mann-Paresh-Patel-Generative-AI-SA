"""
COACHBOT AI - Smart Fitness Assistant
Final Clean Version with Comprehensive Error Handling
"""

import streamlit as st
import google.generativeai as genai
import traceback
import sys
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="CoachBot AI - Smart Sports Assistant",
    page_icon="🏃‍♂️",
    layout="wide"
)

# Initialize session state
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'generated_plans' not in st.session_state:
    st.session_state.generated_plans = {}
if 'error_log' not in st.session_state:
    st.session_state.error_log = []
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

# Sport-specific data
SPORT_DATA = {
    "cricket": {
        "positions": ["Batsman", "Fast Bowler", "Spin Bowler", "Wicket-Keeper", "All-rounder"],
        "common_injuries": ["Hamstring strain", "Shoulder impingement", "Lower back pain", 
                           "Ankle sprain", "Side strain", "Rotator cuff tear"],
        "energy": {"Aerobic": 60, "Anaerobic": 30, "Power": 10}
    },
    "kabaddi": {
        "positions": ["Raider", "Corner Defender", "Cover Defender", "All-rounder"],
        "common_injuries": ["Knee ligament tear", "Ankle sprain", "Shoulder dislocation",
                           "Concussion", "Finger fracture", "Groin strain"],
        "energy": {"Aerobic": 40, "Anaerobic": 50, "Power": 10}
    },
    "volleyball": {
        "positions": ["Setter", "Outside Hitter", "Middle Blocker", "Opposite", "Libero"],
        "common_injuries": ["Jumper's knee", "Ankle sprain", "Shoulder pain",
                           "Rotator cuff injury", "Finger injury", "Back pain"],
        "energy": {"Aerobic": 50, "Anaerobic": 40, "Power": 10}
    }
}

def log_error(error_message, error_details):
    """Log errors for debugging"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.error_log.append({
        'timestamp': timestamp,
        'message': error_message,
        'details': error_details
    })

class CoachBotAI:
    def __init__(self):
        """Initialize CoachBot AI with comprehensive error handling"""
        try:
            # Step 1: Check if API key exists
            if "GEMINI_API_KEY" not in st.secrets:
                raise KeyError("GEMINI_API_KEY not found in Streamlit secrets. Please add it to .streamlit/secrets.toml")
            
            api_key = st.secrets["GEMINI_API_KEY"]
            if not api_key or len(api_key.strip()) == 0:
                raise ValueError("GEMINI_API_KEY is empty in Streamlit secrets")
            
            # Step 2: Configure Gemini
            try:
                genai.configure(api_key=api_key)
                log_error("API Configuration", "Successfully configured Gemini API")
            except Exception as e:
                raise Exception(f"Failed to configure Gemini API: {str(e)}")
            
            # Step 3: List available models to debug
            try:
                available_models = list(genai.list_models())
                model_names = [m.name for m in available_models]
                log_error("Available Models", f"Found {len(available_models)} models: {model_names}")
                
                # Store in session state for debugging
                st.session_state.available_models = [
                    {
                        'name': m.name,
                        'display_name': m.display_name,
                        'methods': m.supported_generation_methods
                    }
                    for m in available_models
                ]
            except Exception as e:
                log_error("List Models Error", f"Could not list models: {str(e)}")
                st.session_state.available_models = []
            
            # Step 4: Try different model names
            model_attempts = [
                'gemini-pro',
                'models/gemini-pro',
                'gemini-1.5-pro',
                'models/gemini-1.5-pro',
                'gemini-1.5-flash',
                'models/gemini-1.5-flash',
                'gemini-1.0-pro',
                'models/gemini-1.0-pro'
            ]
            
            self.model = None
            last_error = None
            
            for model_name in model_attempts:
                try:
                    log_error("Model Attempt", f"Trying model: {model_name}")
                    test_model = genai.GenerativeModel(model_name)
                    
                    # Test the model with a simple prompt
                    test_response = test_model.generate_content(
                        "Respond with only the word 'OK'",
                        generation_config={
                            "temperature": 0.1,
                            "max_output_tokens": 10
                        }
                    )
                    
                    if test_response and test_response.text:
                        self.model = test_model
                        log_error("Model Success", f"Successfully connected using: {model_name}")
                        break
                    else:
                        raise Exception("Model test failed - no response")
                        
                except Exception as e:
                    last_error = e
                    log_error("Model Failed", f"Model {model_name} failed: {str(e)}")
                    continue
            
            # Step 5: Check if any model worked
            if self.model is None:
                error_msg = f"No working model found. Last error: {str(last_error)}"
                log_error("Initialization Failed", error_msg)
                raise Exception(error_msg)
            
        except Exception as e:
            error_details = traceback.format_exc()
            log_error("CoachBotAI Initialization Error", error_details)
            st.error(f"❌ **CoachBotAI Initialization Failed**")
            st.error(f"Error: {str(e)}")
            st.error("Please check the debug section below for details.")
            raise e
    
    def create_personalized_plan(self, user_data):
        """Generate complete personalized plan with error handling"""
        try:
            # Validate user data
            required_fields = ['sport', 'position', 'age', 'experience', 'training_days', 'goals', 'fitness_level', 'current_injury']
            for field in required_fields:
                if field not in user_data:
                    raise KeyError(f"Missing required field: {field}")
            
            if user_data['current_injury'] != "None":
                plan = self._generate_injury_plan(user_data)
            else:
                plan = self._generate_normal_plan(user_data)
            
            return plan
            
        except Exception as e:
            error_details = traceback.format_exc()
            log_error("Create Plan Error", error_details)
            raise Exception(f"Failed to create plan: {str(e)}")
    
    def _generate_normal_plan(self, user_data):
        """Generate plan for healthy athlete with error handling"""
        try:
            prompt = f"""
            Create a COMPLETE 4-week training program for:
            
            SPORT: {user_data['sport'].upper()}
            POSITION: {user_data['position']}
            AGE: {user_data['age']} years
            EXPERIENCE: {user_data['experience']} years
            TRAINING DAYS: {user_data['training_days']}/week
            GOALS: {', '.join(user_data['goals'])}
            FITNESS LEVEL: {user_data['fitness_level']}
            
            The program MUST include:
            
            WEEK 1-2: BASE BUILDING
            - Sport-specific skill drills
            - Strength foundation
            - Aerobic conditioning
            - Mobility work
            
            WEEK 3-4: INTENSIFICATION
            - Power development
            - High-intensity intervals
            - Technical refinement
            - Mental preparation
            
            For EACH week provide:
            1. Daily workout schedule
            2. Specific exercises with sets/reps
            3. Recovery protocols
            4. Nutrition timing advice
            5. Progress tracking metrics
            
            Make it SPECIFIC to {user_data['sport']} {user_data['position']}.
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "max_output_tokens": 1500
                }
            )
            
            if not response or not response.text:
                raise Exception("Empty response from model")
            
            return response.text
            
        except Exception as e:
            error_details = traceback.format_exc()
            log_error("Generate Normal Plan Error", error_details)
            raise Exception(f"Failed to generate normal plan: {str(e)}")
    
    def _generate_injury_plan(self, user_data):
        """Generate injury-modified plan with error handling"""
        try:
            prompt = f"""
            Create a SAFE, injury-modified training program for:
            
            SPORT: {user_data['sport'].upper()}
            POSITION: {user_data['position']}
            INJURY: {user_data['current_injury']}
            INJURY DURATION: {user_data.get('injury_duration', 'Recent')}
            LIMITATIONS: {user_data.get('limitations', 'Pain during activity')}
            AGE: {user_data['age']} years
            
            IMPORTANT SAFETY RULES:
            1. DO NOT recommend exercises that could worsen {user_data['current_injury']}
            2. Focus on rehabilitation and safe alternatives
            3. Include gradual progression
            4. Add warning signs to watch for
            
            Create a 3-PHASE RECOVERY PROGRAM:
            
            PHASE 1 (Week 1-2): REHABILITATION
            - Pain management
            - Range of motion
            - Very light activity
            
            PHASE 2 (Week 3-4): MODIFIED TRAINING
            - Sport-specific movements at reduced intensity
            - Strength without aggravating injury
            - Controlled progression
            
            PHASE 3 (Week 5-6): RETURN PREPARATION
            - Sport-specific drills
            - Gradual intensity increase
            - Performance testing
            
            For each phase provide:
            1. Daily exercise plan
            2. Modifications for {user_data['sport']}
            3. Progression criteria
            4. Safety precautions
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "top_p": 0.7,
                    "max_output_tokens": 800
                }
            )
            
            if not response or not response.text:
                raise Exception("Empty response from model")
            
            return response.text
            
        except Exception as e:
            error_details = traceback.format_exc()
            log_error("Generate Injury Plan Error", error_details)
            raise Exception(f"Failed to generate injury plan: {str(e)}")
    
    def generate_nutrition_plan(self, user_data):
        """Generate nutrition plan with error handling"""
        try:
            # Build dietary restrictions string
            dietary_info = "DIETARY RESTRICTIONS:\n"
            
            if user_data.get('dietary_restrictions'):
                for restriction in user_data['dietary_restrictions']:
                    dietary_info += f"- {restriction}\n"
            else:
                dietary_info += "- No dietary restrictions\n"
            
            if user_data.get('rare_allergies'):
                dietary_info += f"\nRARE ALLERGIES:\n- {user_data['rare_allergies']}\n"
            
            prompt = f"""
            Create a DETAILED 7-day nutrition plan for a {user_data['sport']} athlete.
            
            ATHLETE PROFILE:
            - Sport: {user_data['sport']}
            - Position: {user_data['position']}
            - Age: {user_data['age']} years
            - Weight: {user_data.get('weight', 'Not specified')} kg
            - Height: {user_data.get('height', 'Not specified')} cm
            - Gender: {user_data['gender']}
            - Training: {user_data['training_days']} days/week
            - Goals: {', '.join(user_data['goals'])}
            
            {dietary_info}
            
            NUTRITIONAL REQUIREMENTS:
            - High protein for muscle repair
            - Complex carbs for sustained energy
            - Healthy fats for hormone balance
            - Adequate hydration
            
            Create a COMPLETE meal plan with:
            
            FOR EACH DAY (Monday-Sunday):
            1. BREAKFAST (with portion sizes)
            2. MID-MORNING SNACK
            3. LUNCH (main protein + carbs + veggies)
            4. PRE-WORKOUT SNACK (1-2 hours before training)
            5. POST-WORKOUT MEAL (within 30 minutes after)
            6. DINNER
            7. BEDTIME SNACK (if needed)
            
            Include for each meal:
            - Ingredients with quantities (grams/cups)
            - Simple cooking instructions
            - Macronutrient breakdown
            - Approximate calories
            
            ADDITIONAL SECTIONS:
            1. Weekly Grocery Shopping List
            2. Hydration Schedule (when & how much to drink)
            3. Meal Prep Tips
            4. Budget-Friendly Alternatives
            
            IMPORTANT: Strictly respect all dietary restrictions listed above.
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.4,
                    "top_p": 0.8,
                    "max_output_tokens": 2000
                }
            )
            
            if not response or not response.text:
                raise Exception("Empty response from model")
            
            return response.text
            
        except Exception as e:
            error_details = traceback.format_exc()
            log_error("Generate Nutrition Plan Error", error_details)
            raise Exception(f"Failed to generate nutrition plan: {str(e)}")
    
    def generate_tactical_advice(self, user_data):
        """Generate tactical advice with error handling"""
        try:
            prompt = f"""
            Provide detailed tactical coaching advice for:
            
            SPORT: {user_data['sport'].upper()}
            POSITION: {user_data['position']}
            EXPERIENCE: {user_data['experience']} years
            LEVEL: {user_data['competition_level']}
            
            Cover these areas:
            1. Position-specific responsibilities
            2. Game reading and decision making
            3. Technical skill improvements
            4. Mental preparation strategies
            5. Match day routines
            6. Opponent analysis methods
            7. Communication with teammates
            8. Common mistakes to avoid
            
            Provide SPECIFIC examples for {user_data['sport']} {user_data['position']}.
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.5,
                    "top_p": 0.85,
                    "max_output_tokens": 1000
                }
            )
            
            if not response or not response.text:
                raise Exception("Empty response from model")
            
            return response.text
            
        except Exception as e:
            error_details = traceback.format_exc()
            log_error("Generate Tactical Advice Error", error_details)
            raise Exception(f"Failed to generate tactical advice: {str(e)}")

def display_sidebar():
    """Create sidebar input form"""
    with st.sidebar:
        st.title("🏃‍♂️ CoachBot AI")
        st.markdown("---")
        
        # Debug mode toggle
        st.session_state.debug_mode = st.checkbox("🔧 Debug Mode", value=st.session_state.debug_mode)
        
        # Sport Selection
        sport = st.selectbox(
            "Select Your Sport",
            ["cricket", "kabaddi", "volleyball"],
            format_func=lambda x: x.capitalize()
        )
        
        # Position
        position = st.selectbox("Your Position", SPORT_DATA[sport]["positions"])
        
        # Personal Details
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 12, 40, 18, step=1)
            height = st.text_input("Height (cm)", placeholder="e.g., 175")
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            weight = st.text_input("Weight (kg)", placeholder="e.g., 65.5")
        
        experience = st.slider(f"{sport.capitalize()} Experience (years)", 0, 20, 3)
        training_days = st.slider("Training Days per Week", 1, 7, 4)
        fitness_level = st.selectbox("Current Fitness Level", 
                                   ["Beginner", "Intermediate", "Advanced", "Elite"])
        
        # Goals
        goals = st.multiselect(
            "Training Goals",
            ["Strength", "Speed", "Endurance", "Skill", "Injury Prevention", "Weight Management", "Competition"],
            default=["Strength", "Skill"]
        )
        
        # Injury Section
        st.subheader("Injury Information")
        injury_options = ["None"] + SPORT_DATA[sport]["common_injuries"]
        current_injury = st.selectbox("Current Injury", injury_options)
        
        injury_duration = None
        limitations = None
        if current_injury != "None":
            injury_duration = st.selectbox("Injury Duration", 
                                         ["< 2 weeks", "2-4 weeks", "1-3 months", "> 3 months"])
            limitations = st.text_area("Current Limitations", "Pain during certain movements")
        
        # Simplified Dietary Section
        with st.expander("🍽️ Dietary Restrictions"):
            st.write("Select all that apply:")
            
            col1, col2 = st.columns(2)
            restrictions = []
            
            with col1:
                if st.checkbox("No Red Meat (beef, lamb)"):
                    restrictions.append("No red meat")
                if st.checkbox("No Pork"):
                    restrictions.append("No pork")
                if st.checkbox("No Poultry (chicken, turkey)"):
                    restrictions.append("No poultry")
                if st.checkbox("No Fish"):
                    restrictions.append("No fish")
                if st.checkbox("No Seafood (shrimp, crab)"):
                    restrictions.append("No seafood")
                if st.checkbox("No Eggs"):
                    restrictions.append("No eggs")
                if st.checkbox("No Milk"):
                    restrictions.append("No milk")
                if st.checkbox("No Cheese"):
                    restrictions.append("No cheese")
                if st.checkbox("No Yogurt"):
                    restrictions.append("No yogurt")
            
            with col2:
                if st.checkbox("No Onions"):
                    restrictions.append("No onions")
                if st.checkbox("No Garlic"):
                    restrictions.append("No garlic")
                if st.checkbox("No Potatoes"):
                    restrictions.append("No potatoes")
                if st.checkbox("No Root Vegetables/Tubers"):
                    restrictions.append("No root vegetables (carrots, beets, etc.)")
                if st.checkbox("No Mushrooms"):
                    restrictions.append("No mushrooms")
                if st.checkbox("No Gluten (wheat, barley)"):
                    restrictions.append("No gluten")
                if st.checkbox("No Nuts (peanuts, almonds)"):
                    restrictions.append("No nuts")
                if st.checkbox("No Soy"):
                    restrictions.append("No soy")
                if st.checkbox("No Lentils/Beans"):
                    restrictions.append("No legumes")
            
            rare_allergies = st.text_input(
                "Any rare allergies? (optional)",
                placeholder="e.g., avocado, sesame seeds, etc."
            )
        
        competition_level = st.selectbox("Competition Level",
                                       ["Recreational", "School", "Club", "State", "National", "Professional"])
        
        # Store profile in session state
        st.session_state.user_profile = {
            'sport': sport,
            'position': position,
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'experience': experience,
            'training_days': training_days,
            'fitness_level': fitness_level,
            'goals': goals,
            'current_injury': current_injury,
            'competition_level': competition_level,
            'dietary_restrictions': restrictions,
            'rare_allergies': rare_allergies if rare_allergies else None
        }
        
        if current_injury != "None":
            st.session_state.user_profile['injury_duration'] = injury_duration
            st.session_state.user_profile['limitations'] = limitations
        
        st.markdown("---")
        generate_button = st.button("🚀 GENERATE MY PLAN", type="primary", use_container_width=True)
        
        return generate_button

def display_debug_info():
    """Display debug information"""
    if st.session_state.debug_mode:
        with st.expander("🔧 Debug Information", expanded=True):
            st.subheader("Error Log")
            if st.session_state.error_log:
                for error in st.session_state.error_log[-5:]:  # Show last 5 errors
                    st.write(f"**{error['timestamp']}**")
                    st.write(f"Message: {error['message']}")
                    if st.checkbox(f"Show details for {error['timestamp']}"):
                        st.code(error['details'])
                    st.markdown("---")
            else:
                st.write("No errors logged yet")
            
            st.subheader("Available Models")
            if hasattr(st.session_state, 'available_models'):
                for model in st.session_state.available_models:
                    st.write(f"- **{model['display_name']}** (`{model['name']}`)")
                    st.write(f"  Methods: {model['methods']}")
            else:
                st.write("No model information available")
            
            st.subheader("User Profile")
            st.json(st.session_state.user_profile)
            
            if st.button("Clear Error Log"):
                st.session_state.error_log = []
                st.rerun()

def display_main_content():
    """Display main content area"""
    st.title("🏋️‍♂️ CoachBot AI - Your Personal Sports Assistant")
    st.markdown("---")
    
    # Display debug info if enabled
    display_debug_info()
    
    # Check if profile exists
    if not st.session_state.user_profile:
        st.info("👈 Please fill in your details in the sidebar and click 'GENERATE MY PLAN' to get started!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("📋 Personalized Training")
            st.write("Get custom workout plans tailored to your sport, position, and goals")
        with col2:
            st.subheader("🥗 Nutrition Guidance")
            st.write("Receive meal plans that respect your dietary restrictions and preferences")
        with col3:
            st.subheader("🧠 Tactical Advice")
            st.write("Learn position-specific strategies and game intelligence")
        
        return False
    
    return True

def display_results(coach):
    """Display generated results with error handling"""
    user_data = st.session_state.user_profile
    
    tab1, tab2, tab3 = st.tabs(["📋 Training Plan", "🥗 Nutrition Plan", "🧠 Tactical Advice"])
    
    with tab1:
        st.subheader(f"Your Personalized {user_data['sport'].title()} Training Plan")
        
        plan_key = f"training_plan_{user_data['sport']}_{user_data['position']}"
        
        if plan_key not in st.session_state.generated_plans:
            with st.spinner("Creating your personalized training plan..."):
                try:
                    plan = coach.create_personalized_plan(user_data)
                    st.session_state.generated_plans[plan_key] = plan
                    st.success("✅ Training plan generated successfully!")
                except Exception as e:
                    error_details = traceback.format_exc()
                    log_error("Display Results - Training Plan", error_details)
                    st.error(f"❌ **Error generating training plan:**")
                    st.error(f"Error type: {type(e).__name__}")
                    st.error(f"Error message: {str(e)}")
                    if st.session_state.debug_mode:
                        st.code(error_details)
                    return
        
        st.markdown(st.session_state.generated_plans[plan_key])
        
        st.download_button(
            label="📥 Download Training Plan",
            data=st.session_state.generated_plans[plan_key],
            file_name=f"training_plan_{user_data['sport']}_{user_data['position']}.txt",
            mime="text/plain"
        )
    
    with tab2:
        st.subheader(f"Your Personalized Nutrition Plan")
        
        nutrition_key = f"nutrition_plan_{user_data['sport']}_{user_data['position']}"
        
        if nutrition_key not in st.session_state.generated_plans:
            with st.spinner("Creating your personalized nutrition plan..."):
                try:
                    plan = coach.generate_nutrition_plan(user_data)
                    st.session_state.generated_plans[nutrition_key] = plan
                    st.success("✅ Nutrition plan generated successfully!")
                except Exception as e:
                    error_details = traceback.format_exc()
                    log_error("Display Results - Nutrition Plan", error_details)
                    st.error(f"❌ **Error generating nutrition plan:**")
                    st.error(f"Error type: {type(e).__name__}")
                    st.error(f"Error message: {str(e)}")
                    if st.session_state.debug_mode:
                        st.code(error_details)
                    return
        
        st.markdown(st.session_state.generated_plans[nutrition_key])
        
        st.download_button(
            label="📥 Download Nutrition Plan",
            data=st.session_state.generated_plans[nutrition_key],
            file_name=f"nutrition_plan_{user_data['sport']}_{user_data['position']}.txt",
            mime="text/plain"
        )
    
    with tab3:
        st.subheader(f"Tactical Advice for {user_data['sport'].title()} {user_data['position']}")
        
        tactical_key = f"tactical_advice_{user_data['sport']}_{user_data['position']}"
        
        if tactical_key not in st.session_state.generated_plans:
            with st.spinner("Generating tactical advice..."):
                try:
                    advice = coach.generate_tactical_advice(user_data)
                    st.session_state.generated_plans[tactical_key] = advice
                    st.success("✅ Tactical advice generated successfully!")
                except Exception as e:
                    error_details = traceback.format_exc()
                    log_error("Display Results - Tactical Advice", error_details)
                    st.error(f"❌ **Error generating tactical advice:**")
                    st.error(f"Error type: {type(e).__name__}")
                    st.error(f"Error message: {str(e)}")
                    if st.session_state.debug_mode:
                        st.code(error_details)
                    return
        
        st.markdown(st.session_state.generated_plans[tactical_key])
        
        st.download_button(
            label="📥 Download Tactical Advice",
            data=st.session_state.generated_plans[tactical_key],
            file_name=f"tactical_advice_{user_data['sport']}_{user_data['position']}.txt",
            mime="text/plain"
        )

def main():
    """Main application function"""
    try:
        # Display sidebar and get generate button state
        generate_clicked = display_sidebar()
        
        # Display main content
        profile_exists = display_main_content()
        
        # Initialize coach if needed
        if profile_exists or generate_clicked:
            try:
                coach = CoachBotAI()
                
                if generate_clicked or profile_exists:
                    display_results(coach)
                    
            except Exception as e:
                error_details = traceback.format_exc()
                log_error("Main - Coach Initialization", error_details)
                st.error("❌ **Failed to initialize CoachBot AI**")
                st.error(f"Error: {str(e)}")
                if st.session_state.debug_mode:
                    st.subheader("Full Error Details")
                    st.code(error_details)
                    st.subheader("Troubleshooting Steps")
                    st.markdown("""
                    1. **Check your API key** in `.streamlit/secrets.toml`
                    2. **Verify API key format** - It should start with "AIza..."
                    3. **Enable the API** at https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
                    4. **Check billing** - Some models require billing enabled
                    """)
    
    except Exception as e:
        error_details = traceback.format_exc()
        log_error("Main - Fatal Error", error_details)
        st.error("❌ **A fatal error occurred**")
        st.error(f"Error: {str(e)}")
        if st.session_state.debug_mode:
            st.code(error_details)

if __name__ == "__main__":
    main()
