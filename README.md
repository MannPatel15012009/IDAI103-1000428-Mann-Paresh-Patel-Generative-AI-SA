# NextGen Sports Lab
### Generative AI Powered Smart Sports Performance Assistant  
> By *Mann Paresh Patel*  

---

## Project Overview  

NextGen Sports Lab is an advanced AI-powered sports performance advisory system developed using **Streamlit** and **Gemini**.  

The application is designed to provide structured, sport-specific, and position-aware performance guidance for athletes across multiple disciplines. By collecting detailed athlete inputs and applying contextual prompt engineering techniques, the system generates comprehensive training programs, nutrition strategies, and tactical intelligence tailored to the athlete’s profile.

Unlike generic fitness applications, NextGen Sports Lab integrates sport context, competition level, injury condition, and performance goals into its decision-making process. The system dynamically adapts its recommendations based on whether the athlete is healthy or currently recovering from an injury.

The platform is structured into three core AI modules:

- 🏋️ Performance Training Module  
- 🥗 Sports Nutrition Module  
- 🧠 Tactical Intelligence Module  

Each module operates independently while maintaining consistency in athlete profiling and session-based data management.

---

## Key Features  

### 🏋️ Sport-Specific 4-Week Periodized Training Plan  

Generates a structured four-week training program customized according to:

- Selected sport and position  
- Experience level  
- Fitness level  
- Competition tier  
- Weekly training availability  
- Performance goals  

The training plan includes:

- Executive performance analysis  
- Weekly progression focus (Weeks 1–2 vs Weeks 3–4)  
- Detailed day-wise breakdown  
- Exercise drills with sets and repetitions  
- Warm-up and cool-down structure  
- Recovery protocol recommendations  

All outputs are structured in professional Markdown format for clarity and readability.

---

### 🚑 Injury-Adaptive Training Logic  

NextGen Sports Lab incorporates conditional branch logic for injury handling.

If an athlete selects an active injury:

- The AI switches to a rehabilitation-focused training structure  
- Safety instructions are injected into the AI prompt  
- Recovery and maintenance strategies are emphasized  
- High-risk exercises are avoided  

This ensures responsible and adaptive performance planning.

---

### 🥗 AI-Based 7-Day Sports Nutrition Plan  

The Nutrition Module generates a structured weekly meal plan based on:

- Height and weight  
- Gender  
- Performance goals  
- Sport-specific demands  
- Dietary restrictions  
- Allergies  

The output includes:

- Estimated calorie targets  
- Approximate macro distribution  
- 7-day meal breakdown (Breakfast, Lunch, Dinner, Snacks)  
- Pre-workout and post-workout nutrition timing  
- Complete weekly grocery shopping list  

Dietary preferences such as Vegetarian, Vegan, Gluten-Free, Lactose-Free, and custom allergies are dynamically integrated into the AI prompt.

---

### 🧠 Tactical & Game Intelligence Module  

Provides advanced position-specific tactical insights including:

- Role mastery fundamentals  
- Situational decision-making (Game IQ)  
- Mental resilience strategies  
- Common mistakes at the selected competition level  

This module adjusts outputs based on sport, position, experience, and competition tier.

---

### 📊 Multi-Sport Support Framework  

The application currently supports:

- Cricket  
- Kabaddi  
- Volleyball  
- Football  
- Basketball  

Each sport includes predefined position lists and common injury references, enabling contextual and sport-aware AI prompting.

---

### 🔄 Session-Based Plan Management  

NextGen Sports Lab utilizes Streamlit’s session state management to:

- Store generated plans  
- Prevent unnecessary regeneration  
- Improve performance efficiency  
- Maintain user context across application tabs  

Each plan is uniquely identified and cached during the session.

---

### 📥 Downloadable Training Plans  

Users can download the generated training plan in Markdown format for:

- Offline viewing  
- Printing  
- Documentation  
- Sharing with coaches or trainers  

---

### 🔐 Secure Gemini API Configuration  

The application securely integrates Google Gemini using:

- `st.secrets` configuration  
- Mandatory API key validation  
- Safe model initialization  

If the API key is missing, the system safely halts execution to prevent runtime failures.

---

### 🛠 Structured Error Logging System  

The application includes a structured debugging framework that:

- Logs timestamped errors  
- Stores execution context  
- Captures detailed traceback information  
- Maintains logs within session state  

This improves reliability and maintainability.

---

## Technologies Used  

- **Python**  
- **Streamlit**  
- **Google Generative AI (Gemini 3 Flash Preview)**  
- **Prompt Engineering Techniques**  
- **Session State Management**  
- **Markdown Rendering**  
- **Conditional Logic for Adaptive Planning**  

---

## Application Architecture  

Athlete Profile Input (Sidebar Form)  
↓  
Session State Storage  
↓  
Conditional Logic Processing (Injury & Goals)  
↓  
Role-Based Prompt Engineering  
↓  
Gemini Model Invocation  
↓  
Structured Markdown Output  
↓  
Tabbed Interface Rendering  
↓  
Optional Download  

---

## Installation & Setup  

### 1️⃣ Clone the Repository  

```bash
git clone https://github.com/MannPatel15012009/IDAI-1000428-Mann-Paresh-Patel-Generative-AI-SA.git
cd IDAI-1000428-Mann-Paresh-Patel-Generative-AI-SA
```
### 2️⃣ Install Required Dependencies  

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Gemini API Key  

Create a `.streamlit/secrets.toml` file:

```toml
GEMINI_API_KEY = "YOUR_API_KEY"
```

### 4️⃣ Run the Application  

```bash
streamlit run app.py
```

---

## Prompt Engineering Strategy  

NextGen Sports Lab uses structured role-based prompt engineering.

Each module assigns a professional persona:
- Elite Sports Performance Coach  
- Certified Sports Nutritionist  
- Veteran Tactical Strategist  

Prompts dynamically incorporate:
- Sport and position  
- Athlete demographics  
- Experience level  
- Competition tier  
- Injury condition  
- Dietary constraints  

Temperature settings are adjusted to balance structure and reasoning depth.

---

## Output Structure  

### 🏋️ Training Module  
- Executive Summary  
- Weekly Focus Strategy  
- Day-Wise Schedule  
- Warm-Up & Cool-Down  
- Recovery Protocol  

### 🥗 Nutrition Module  
- Calorie & Macro Estimation  
- 7-Day Meal Plan  
- Workout Nutrition Timing  
- Weekly Shopping List  

### 🧠 Tactical Module  
- Role Mastery  
- Situational Intelligence  
- Mental Game Strategy  
- Competition-Level Mistakes  

---

## Educational Objectives  

This project demonstrates:
- Multi-module AI system design  
- Conditional logic integration with LLMs  
- Domain-specific prompt engineering  
- Secure API configuration  
- Interactive Streamlit UI development  
- Session-based optimization  

---

## Future Improvements  

- Scientific BMI & macro logic  
- PDF export  
- Persistent athlete profiles  
- Performance analytics dashboard  
- Cloud deployment  

---

## Author  

**Mann Paresh Patel**  
Student – IDAI-1000428  
Generative AI Summative Assessment
