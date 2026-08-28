# TravelMind 🧭

AI-powered trip planner — type a trip in plain English, get a budget-fitted,
day-by-day itinerary that live-updates as you tweak budget/pace/group size.

Built for CODE O'CLOCK hackathon.

## Team ownership

| Person | Owns | Files |
|---|---|---|
| A — Data | Places/hotels/transport JSON, real train data | `data/` |
| B — LLM | All 4 AI prompt functions + shared wrapper | `llm/` |
| C — Optimizer | OR-Tools scheduling, budget/time/pace constraints | `optimizer/` |
| D — Frontend | Streamlit UI, wiring, live re-plan, demo | `app.py`, `weather/` |

# ✈️ TravelMind AI

### AI-Powered Personalized Travel Planning & Adaptive Trip Optimization

> **Plan less. Travel smarter. Experience more.**

TravelMind is an AI-powered travel planning platform that transforms a simple natural-language travel request into a personalized, budget-aware and preference-driven travel plan.

Instead of manually searching across multiple platforms for destinations, hotels, transportation, food, activities and weather, TravelMind brings the planning experience together into one intelligent interface.

---

## 🌍 The Problem

Planning a trip usually means switching between multiple applications for:

- Flights and trains
- Hotels
- Restaurants
- Tourist attractions
- Weather
- Maps
- Budget calculations
- Itinerary planning

This makes travel planning time-consuming, fragmented and difficult to personalize.

### 💡 Our Solution

TravelMind acts as an intelligent travel-planning layer that understands:

**Destination + Dates + Budget + Group Size + Interests + Travel Style**

and uses these requirements to create a personalized travel experience.

---

# 🧠 How TravelMind Works

```text
User's Natural Language Request
              │
              ▼
      Travel Constraint Parsing
              │
              ▼
    ┌─────────────────────────┐
    │ Destination             │
    │ Dates / Duration        │
    │ Budget                  │
    │ Group Size              │
    │ Interests               │
    │ Travel Style            │
    └────────────┬────────────┘
                 │
                 ▼
          AI Trip Planning
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
   Itinerary  Weather   Recommendations
       │         │         │
       ▼         ▼         ▼
   Transport   Hotels    Activities
       │         │         │
       └─────────┼─────────┘
                 ▼
          Optimized Trip
                 │
                 ▼
        Adaptive Re-Planning✨ Key Features
🗣️ Natural-Language Trip Planning

Users can describe their entire trip naturally.

Example:

5 days from Chennai to Goa,
₹60,000 budget for 4 people,
interested in beaches, food and nightlife.

TravelMind extracts the important travel constraints automatically.

💰 Budget-Aware Planning

The system considers the traveler's total budget while planning the trip.

Major expenses include:

Transportation
Accommodation
Food
Activities
Local travel

The objective is to keep the estimated trip cost within the specified budget.

🗓️ Intelligent Itinerary

TravelMind generates a structured day-by-day travel plan instead of simply providing a list of destinations.

Activities can be organized around appropriate times, meals and travel flow to create a more practical journey.

🌦️ Weather Intelligence

Weather information is incorporated into the travel experience to help users understand destination conditions and make better planning decisions.

🚆✈️🚌 Transportation Options

TravelMind provides transportation alternatives such as:

Flight
Train
Bus

Options can be compared based on estimated cost, convenience and travel time.

🏨 Accommodation Recommendations

The platform provides hotel/stay recommendations based on the selected destination and travel requirements.

🍴 Food & Activity Planning

TravelMind considers food and activities as part of the complete journey, including:

Breakfast
Lunch
Dinner
Local food experiences
Attractions
Activities
Relaxation
Entertainment
📍 Personalized Recommendations

Recommendations are influenced by traveler interests such as:

🏖️ Beaches
🍴 Food
🌃 Nightlife
🌿 Nature
🏛️ History
🎨 Culture
📸 Photography
🛕 Temples
😌 Relaxation
🔄 Adaptive Trip Re-Planning

Travel plans can change.

TravelMind includes an adaptive re-planning concept where travelers can provide a new constraint during their trip.

Example:

"It's raining tomorrow. Replace the outdoor activities."

The remaining itinerary can then be reconsidered around the new requirement.

Original Plan
     ↓
New Condition
     ↓
AI Re-evaluation
     ↓
Updated Itinerary
💾 Save & Revisit Trips

Generated trips can be saved so travelers can return to their plans later and continue refining them.

🏗️ Technology Stack
Frontend
HTML5
CSS3
JavaScript
Responsive UI
Backend
Python
FastAPI
Uvicorn
Pydantic
AI / Intelligence
Large Language Model integration
Natural-language constraint extraction
Personalized trip planning
Budget-aware optimization
Adaptive planning
Supporting Components
Weather integration
Travel recommendation data
Transportation planning
Accommodation recommendations
📁 Project Structure
travelmind/
│
├── api.py
├── app.py
│
├── data/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── llm/
├── optimizer/
├── weather/
│
├── requirements.txt
├── test_integration.py
├── .env.example
├── .gitignore
└── README.md
🔄 Development Workflow

TravelMind was developed progressively from the core planning engine into a complete user-facing application.

Project Setup
     ↓
Travel Constraint Extraction
     ↓
FastAPI Backend
     ↓
AI Planning Logic
     ↓
Budget & Optimization
     ↓
Weather Integration
     ↓
Itinerary Generation
     ↓
Transport & Accommodation
     ↓
Recommendations
     ↓
Adaptive Re-Planning
     ↓
Frontend Integration
     ↓
UI/UX Refinement
     ↓
Integration Testing

The system was tested locally using the FastAPI API with travel requests such as Chennai → Goa.

🧪 Example
User Input
5 days from Chennai to Goa,
₹60,000 total budget for 4 people,
I love beaches, food and nightlife.
TravelMind understands
Origin        → Chennai
Destination   → Goa
Duration      → 5 days
Budget        → ₹60,000
Travellers    → 4
Pace          → Balanced
Persona       → Balanced Explorer
Interests     → Beaches, Food, Nightlife

The system then uses these constraints to build the personalized travel experience.

👥 Team
Vishal B

AI / Full-Stack Development

Kamalesh K

Development & Implementation

Avinash K

Development & Implementation

Ajay S

Development & Implementation

🚀 Running Locally

Clone the repository:

git clone https://github.com/YOUR_USERNAME/travelmind-ai-travel-planner.git
cd travelmind-ai-travel-planner

Create a virtual environment:

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Run the FastAPI server:

uvicorn api:app --reload --port 8000

Open:

http://127.0.0.1:8000
🔐 Environment Variables

Create your local .env file using:

.env.example

Never commit API keys, passwords or other secrets to GitHub.

🔮 Future Scope

TravelMind can evolve into a fully real-time AI travel assistant with:

Live flight and train pricing
Real-time hotel availability
Restaurant recommendations
Maps and route optimization
Live location awareness
Dynamic budget reallocation
Multi-agent travel planning
Automatic itinerary changes
Real-time booking integration
Long-Term Vision
PLAN
  ↓
TRAVEL
  ↓
OBSERVE
  ↓
UNDERSTAND
  ↓
ADAPT
  ↓
RE-PLAN
  ↓
EXPERIENCE
🏆 Our Vision

TravelMind is designed to move travel planning from:

"Search for places and build the trip yourself."

to:

"Tell us how you want to travel, and let AI build the journey around you."

✈️ TravelMind
Your destination. Your budget. Your preferences. One intelligent journey.

Plan smarter. Travel better.
