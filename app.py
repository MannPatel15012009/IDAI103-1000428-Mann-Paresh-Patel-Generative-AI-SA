"""
COACHBOT AI - Smart Fitness Assistant
Final Clean Version with Simplified Dietary Options
"""

import streamlit as st
import google.generativeai as genai
import pandas as pd
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

class CoachBotAI:
    def __init__(self):
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Try different model names for compatibility
        try:
            # Try with full path first
            self.model = genai.GenerativeModel('models/gemini-1.5-flash')
        except:
            try:
                # Fallback to shorter name
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except:
                # Ultimate fallback to older model
                self.model = genai.GenerativeModel('gemini-pro')
    
    def create_personalized_plan(self, user_data):
        """Generate complete personalized plan"""
        
        if user_data['current_injury'] != "None":
            plan = self._generate_injury_plan(user_data)
        else:
            plan = self._generate_normal_plan(user_data)
        
        return plan
    
    def _generate_normal_plan(self, user_data):
        """Generate plan for healthy athlete"""
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
        return response.text
    
    def _generate_injury_plan(self, user_data):
        """Generate injury-modified plan"""
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
        return response.text
    
    def generate_nutrition_plan(self, user_data):
        """Generate nutrition plan with dietary restrictions"""
        
        # Build dietary restrictions string from checkboxes
        dietary_info = "DIETARY RESTRICTIONS:\n"
        
        if user_data.get('dietary_restrictions'):
            for restriction in user_data['dietary_restrictions']:
                dietary_info += f"- {restriction}\n"
        else:
            dietary_info += "- No dietary restrictions\n"
        
        # Add rare allergies if specified
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
        return response.text
    
    def generate_tactical_advice(self, user_data):
        """Generate tactical advice"""
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
        return response.text

def display_sidebar():
    """Create sidebar input form"""
    with st.sidebar:
        st.title("🏃‍♂️ CoachBot AI")
        st.markdown("---")
        
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
                # Protein restrictions
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
                
                # Dairy restrictions
                if st.checkbox("No Milk"):
                    restrictions.append("No milk")
                if st.checkbox("No Cheese"):
                    restrictions.append("No cheese")
                if st.checkbox("No Yogurt"):
                    restrictions.append("No yogurt")
            
            with col2:
                # Vegetable restrictions
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
                
                # Other restrictions
                if st.checkbox("No Gluten (wheat, barley)"):
                    restrictions.append("No gluten")
                if st.checkbox("No Nuts (peanuts, almonds)"):
                    restrictions.append("No nuts")
                if st.checkbox("No Soy"):
                    restrictions.append("No soy")
                if st.checkbox("No Lentils/Beans"):
                    restrictions.append("No legumes")
            
            # Rare allergies (optional text input)
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
        
        # Add injury-specific fields if applicable
        if current_injury != "None":
            st.session_state.user_profile['injury_duration'] = injury_duration
            st.session_state.user_profile['limitations'] = limitations
        
        # Generate button
        st.markdown("---")
        generate_button = st.button("🚀 GENERATE MY PLAN", type="primary", use_container_width=True)
        
        return generate_button

def display_main_content():
    """Display main content area"""
    st.title("🏋️‍♂️ CoachBot AI - Your Personal Sports Assistant")
    st.markdown("---")
    
    # Check if profile exists
    if not st.session_state.user_profile:
        st.info("👈 Please fill in your details in the sidebar and click 'GENERATE MY PLAN' to get started!")
        
        # Display features
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
    """Display generated results"""
    user_data = st.session_state.user_profile
    
    # Create tabs for different plans
    tab1, tab2, tab3 = st.tabs(["📋 Training Plan", "🥗 Nutrition Plan", "🧠 Tactical Advice"])
    
    with tab1:
        st.subheader(f"Your Personalized {user_data['sport'].title()} Training Plan")
        
        # Check if plan already exists in session state
        plan_key = f"training_plan_{user_data['sport']}_{user_data['position']}"
        
        if plan_key not in st.session_state.generated_plans:
            with st.spinner("Creating your personalized training plan..."):
                try:
                    plan = coach.create_personalized_plan(user_data)
                    st.session_state.generated_plans[plan_key] = plan
                except Exception as e:
                    st.error(f"Error generating plan: {str(e)}")
                    return
        
        # Display the plan
        st.markdown(st.session_state.generated_plans[plan_key])
        
        # Download button
        st.download_button(
            label="📥 Download Training Plan",
            data=st.session_state.generated_plans[plan_key],
            file_name=f"training_plan_{user_data['sport']}_{user_data['position']}.txt",
            mime="text/plain"
        )
    
    with tab2:
        st.subheader(f"Your Personalized Nutrition Plan")
        
        # Check if plan already exists
        nutrition_key = f"nutrition_plan_{user_data['sport']}_{user_data['position']}"
        
        if nutrition_key not in st.session_state.generated_plans:
            with st.spinner("Creating your personalized nutrition plan..."):
                try:
                    plan = coach.generate_nutrition_plan(user_data)
                    st.session_state.generated_plans[nutrition_key] = plan
                except Exception as e:
                    st.error(f"Error generating nutrition plan: {str(e)}")
                    return
        
        # Display the plan
        st.markdown(st.session_state.generated_plans[nutrition_key])
        
        # Download button
        st.download_button(
            label="📥 Download Nutrition Plan",
            data=st.session_state.generated_plans[nutrition_key],
            file_name=f"nutrition_plan_{user_data['sport']}_{user_data['position']}.txt",
            mime="text/plain"
        )
    
    with tab3:
        st.subheader(f"Tactical Advice for {user_data['sport'].title()} {user_data['position']}")
        
        # Check if plan already exists
        tactical_key = f"tactical_advice_{user_data['sport']}_{user_data['position']}"
        
        if tactical_key not in st.session_state.generated_plans:
            with st.spinner("Generating tactical advice..."):
                try:
                    advice = coach.generate_tactical_advice(user_data)
                    st.session_state.generated_plans[tactical_key] = advice
                except Exception as e:
                    st.error(f"Error generating tactical advice: {str(e)}")
                    return
        
        # Display the advice
        st.markdown(st.session_state.generated_plans[tactical_key])
        
        # Download button
        st.download_button(
            label="📥 Download Tactical Advice",
            data=st.session_state.generated_plans[tactical_key],
            file_name=f"tactical_advice_{user_data['sport']}_{user_data['position']}.txt",
            mime="text/plain"
        )

def main():
    """Main application function"""
    # Display sidebar and get generate button state
    generate_clicked = display_sidebar()
    
    # Display main content
    profile_exists = display_main_content()
    
    # Initialize coach if needed
    if profile_exists or generate_clicked:
        try:
            coach = CoachBotAI()
            
            # If generate button was clicked or profile exists, show results
            if generate_clicked or profile_exists:
                display_results(coach)
                
        except Exception as e:
            st.error(f"Error initializing CoachBot AI: {str(e)}")
            st.info("Please check your API key configuration in Streamlit secrets.")

if __name__ == "__main__":
    main()
