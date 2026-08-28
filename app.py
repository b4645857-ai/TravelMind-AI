import json
import os
import streamlit as st
from dotenv import load_dotenv

from llm.parse_constraints import parse_constraints
from llm.recommend_destination import recommend_destination
from llm.generate_guide_blurbs import generate_guide_blurbs
from llm.generate_packing_tips import generate_packing_tips
from optimizer.model import solve_itinerary
from optimizer.trip_score import compute_trip_score, compute_per_person_cost
from weather.weather_check import get_daily_weather, filter_places_for_weather
from data.train_data import get_transport_options

load_dotenv()

st.set_page_config(
    page_title="TravelMind AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family:'Inter',sans-serif; }
.stApp { background:linear-gradient(135deg,#f7f9fc 0%,#eef3f8 100%) !important; color:#0f172a !important; }
.block-container { max-width:1400px; padding-top:2rem; padding-bottom:4rem; }

.stApp p, .stApp span, .stApp label, .stApp li,
.stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stText"],
.stApp [data-testid="stCaptionContainer"] { color:#172033 !important; }

h1,h2,h3,h4,h5,h6 { color:#0f172a !important; }

.hero {
    background:linear-gradient(135deg,#0f172a,#1e293b);
    padding:42px; border-radius:28px; margin-bottom:28px;
    box-shadow:0 20px 60px rgba(15,23,42,.18);
    color:#fff !important;
}
.hero * { color:#fff !important; }
.hero p { color:#cbd5e1 !important; }

.section { font-size:25px; font-weight:750; color:#0f172a !important; margin:28px 0 16px; }

.metric-card,.trip-card,.day-card {
    background:#fff !important; color:#0f172a !important;
    border:1px solid #e2e8f0; box-shadow:0 8px 30px rgba(15,23,42,.05);
}
.metric-card { padding:22px; border-radius:20px; }
.trip-card { padding:24px; border-radius:22px; margin-bottom:14px; }
.day-card { padding:25px; border-radius:22px; margin-bottom:20px; }

.metric-label,.place-meta,.reason { color:#64748b !important; }
.metric-value,.place-name { color:#0f172a !important; }
.metric-value { font-size:28px; font-weight:800; margin-top:6px; }

.place { padding:17px; margin:10px 0; background:#f8fafc !important; border-radius:15px; border-left:4px solid #2563eb; }
.place-name { font-size:17px; font-weight:750; }
.place-meta { font-size:13px; margin-top:4px; }
.reason { font-size:14px; margin-top:8px; }

.badge { display:inline-block; padding:5px 10px; border-radius:999px; background:#e0f2fe !important; color:#0369a1 !important; font-size:11px; font-weight:700; margin-bottom:8px; }

.cost-row { display:flex; justify-content:space-between; padding:12px 0; border-bottom:1px solid #e2e8f0; color:#172033 !important; }
.cost-row span,.cost-row b { color:#172033 !important; }
.total-row { display:flex; justify-content:space-between; padding:16px 0; font-size:20px; font-weight:800; color:#0f172a !important; }

.info-box { background:#eff6ff !important; border:1px solid #bfdbfe; padding:18px; border-radius:16px; color:#1e3a8a !important; }
.info-box * { color:#1e3a8a !important; }
.warning-box { background:#fff7ed !important; border:1px solid #fed7aa; padding:18px; border-radius:16px; color:#9a3412 !important; }
.warning-box * { color:#9a3412 !important; }

textarea,input {
    background:#fff !important; color:#0f172a !important;
    -webkit-text-fill-color:#0f172a !important; border:1px solid #cbd5e1 !important;
}
textarea::placeholder { color:#64748b !important; -webkit-text-fill-color:#64748b !important; }
textarea:focus,input:focus { border-color:#2563eb !important; box-shadow:0 0 0 1px #2563eb !important; }

[data-testid="stSlider"] label,[data-testid="stSlider"] div,
[data-testid="stSelectSlider"] label,[data-testid="stSelectSlider"] div,
[data-testid="stNumberInput"] label { color:#172033 !important; }

[data-testid="stMetric"] { background:#fff !important; color:#0f172a !important; padding:18px; border-radius:18px; border:1px solid #e2e8f0; }
[data-testid="stMetricLabel"] { color:#64748b !important; }
[data-testid="stMetricValue"] { color:#0f172a !important; }

div.stButton > button,div[data-testid="stFormSubmitButton"] > button {
    background:#111827 !important; color:#fff !important;
    -webkit-text-fill-color:#fff !important; border-radius:12px; font-weight:650;
}
div.stButton > button:hover,div[data-testid="stFormSubmitButton"] > button:hover {
    background:#1e293b !important; color:#fff !important;
}

[data-testid="stExpander"] { background:#fff !important; border:1px solid #e2e8f0 !important; border-radius:16px !important; }
[data-testid="stExpander"] * { color:#172033 !important; }
hr { border-color:#e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_city_data(city):
    with open(os.path.join(DATA_DIR, "places.json"), encoding="utf-8") as f:
        places = json.load(f)

    with open(os.path.join(DATA_DIR, "hotels.json"), encoding="utf-8") as f:
        hotels = json.load(f)

    return places.get(city.lower(), []), hotels.get(city.lower(), [])


def money(value):
    return f"₹{int(value):,}"


def reset_state():
    for key in list(st.session_state.keys()):
        if key not in ["trip_input"]:
            del st.session_state[key]


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">
    <div style="font-size:14px;font-weight:700;color:#60a5fa;letter-spacing:.12em;">
        AI TRAVEL OPTIMIZATION
    </div>
    <h1>TravelMind 🧭</h1>
    <p>
        Tell us where you're going, how you want to travel,
        and what you want to spend. TravelMind builds the optimized trip.
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# INPUT
# ============================================================

st.markdown('<div class="section">Plan your trip</div>', unsafe_allow_html=True)

with st.form("trip_form"):
    user_input = st.text_area(
        "Describe your trip",
        placeholder=(
            "Example: 5 days from Bangalore to Goa, "
            "₹60,000 for 4 people, beaches and food, "
            "I don't want to rush."
        ),
        height=110,
        label_visibility="collapsed",
    )

    submitted = st.form_submit_button(
        "✨ Build my optimized trip",
        use_container_width=True,
    )


if submitted and user_input.strip():

    reset_state()

    with st.spinner("Understanding your travel preferences..."):
        parsed_result = parse_constraints(user_input)

    if not parsed_result["ok"]:
        st.error(parsed_result["error"])
        st.stop()

    parsed = parsed_result["data"]

    st.session_state["parsed"] = parsed

    origin = parsed.get("origin")
    destination = parsed.get("destination")

    if not destination:

        with st.spinner("Finding the best destination for you..."):

            rec = recommend_destination(
                parsed["interests"],
                parsed["budget_inr"],
                parsed["days"],
                parsed.get("month"),
            )

        destination = rec["city"]

        st.info(
            f"TravelMind selected **{destination.title()}** "
            f"based on your preferences."
        )

    destination = destination.lower()

    st.session_state["origin"] = origin
    st.session_state["destination"] = destination


# ============================================================
# RESULTS
# ============================================================

if "parsed" not in st.session_state:
    st.markdown("""
    <div class="info-box">
    <b>Try the demo:</b><br>
    5 days from Bangalore to Goa, ₹60,000 for 4 people,
    beaches and food, I don't want to rush.
    </div>
    """, unsafe_allow_html=True)

    st.stop()


parsed = st.session_state["parsed"]
origin = st.session_state.get("origin")
destination = st.session_state["destination"]

places, hotels = load_city_data(destination)

if not places:
    st.error(
        f"No curated attraction data available for {destination.title()} yet."
    )
    st.stop()


# ============================================================
# TRIP UNDERSTANDING
# ============================================================

st.markdown('<div class="section">Trip understood</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("From", origin or "Not specified")
c2.metric("Destination", destination.title())
c3.metric("Duration", f"{parsed['days']} days")
c4.metric("Travelers", parsed["group_size"])
c5.metric("Budget", money(parsed["budget_inr"]))

persona = parsed.get("travel_persona", parsed.get("pace", "Balanced"))

st.markdown(
    f"""
    <div class="trip-card">
        <span class="badge">TRAVEL PERSONA</span>
        <h3 style="margin:4px 0;">{persona}</h3>
        <div style="color:#64748b;">
        Interests: {", ".join(parsed.get("interests", []))}
        &nbsp; · &nbsp;
        Pace: {parsed.get("pace","Balanced")}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LIVE CONTROLS
# ============================================================

st.markdown('<div class="section">Customize your trip</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    budget = st.slider(
        "Total budget",
        1000,
        max(100000, parsed["budget_inr"]),
        parsed["budget_inr"],
        500,
    )

with c2:
    pace = st.select_slider(
        "Travel pace",
        ["Relaxed", "Balanced", "Packed"],
        value=parsed.get("pace", "Balanced"),
    )

with c3:
    group_size = st.number_input(
        "Travelers",
        1,
        20,
        parsed["group_size"],
    )


# ============================================================
# WEATHER
# ============================================================

if "weather" not in st.session_state:

    with st.spinner("Checking destination weather..."):
        st.session_state["weather"] = get_daily_weather(
            destination,
            parsed["days"],
        )

weather = st.session_state["weather"]

weather_days = weather.get("days", [])

rainy_days = {
    i for i, day in enumerate(weather_days)
    if day.get("is_rainy")
}


# ============================================================
# TRANSPORT
# ============================================================

transport = None

if origin:

    with st.spinner("Calculating transportation..."):

        try:
            transport = get_transport_options(
                origin,
                destination,
                group_size=group_size,
            )
        except Exception:
            transport = None


# ============================================================
# HOTEL
# ============================================================

mid_hotel = next(
    (h for h in hotels if h.get("tier") == "mid"),
    hotels[0] if hotels else None,
)

hotel_cost = (
    mid_hotel.get("cost_per_night_inr", 0)
    if mid_hotel
    else 0
)


# ============================================================
# OPTIMIZER
# ============================================================

weather_places = filter_places_for_weather(
    places,
    day_is_rainy=bool(rainy_days),
)

transport_cost = 0

if transport and transport.get("ok"):
    transport_cost = transport.get(
        "total_group_cost_inr",
        0,
    )

result = solve_itinerary(
    places=weather_places,
    days=parsed["days"],
    budget_inr=budget,
    pace=pace,
    interests=parsed["interests"],
    group_size=group_size,
    hotel_cost_per_night=hotel_cost,
    fixed_transport_cost=transport_cost,
    rainy_days=rainy_days,
)

if not result["ok"]:
    st.warning(result["error"])
    st.stop()


# ============================================================
# SUMMARY
# ============================================================

total_cost = result["total_cost_inr"]

score = compute_trip_score(
    total_cost,
    budget,
)

per_person = compute_per_person_cost(
    total_cost,
    group_size,
)

remaining = budget - total_cost

st.markdown('<div class="section">Your optimized trip</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Trip Match",
    f"{score['score']}/100",
)

m2.metric(
    "Total Estimate",
    money(total_cost),
)

m3.metric(
    "Per Person",
    money(per_person),
)

m4.metric(
    "Remaining Budget",
    money(max(remaining, 0)),
)


if remaining >= 0:

    st.markdown(
        f"""
        <div class="info-box">
        <b>✓ Within budget</b><br>
        You have {money(remaining)} remaining.
        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        f"""
        <div class="warning-box">
        <b>⚠ Over budget</b><br>
        This plan exceeds your budget by {money(abs(remaining))}.
        Try reducing the hotel tier, transport cost or trip pace.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# COST BREAKDOWN
# ============================================================

st.markdown('<div class="section">Where your money goes</div>', unsafe_allow_html=True)

activity_cost = sum(
    p["cost_inr"] * group_size
    for day_places in result["schedule"].values()
    for pid in day_places
    for p in places
    if p["id"] == pid
)

hotel_total = hotel_cost * max(parsed["days"] - 1, 0)

food_estimate = (
    700
    * group_size
    * parsed["days"]
)

local_transport = (
    400
    * parsed["days"]
    * group_size
)

display_cost = {
    "Intercity transport": transport_cost,
    "Accommodation": hotel_total,
    "Food estimate": food_estimate,
    "Local transport": local_transport,
    "Activities": activity_cost,
}

cc1, cc2 = st.columns([1.5, 1])

with cc1:

    st.markdown('<div class="trip-card">', unsafe_allow_html=True)

    for name, value in display_cost.items():

        st.markdown(
            f"""
            <div class="cost-row">
                <span>{name}</span>
                <b>{money(value)}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="total-row">
            <span>Total</span>
            <span>{money(total_cost)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

with cc2:

    st.markdown(
        f"""
        <div class="trip-card">
            <span class="badge">BUDGET HEALTH</span>
            <h2 style="margin:4px 0;">
                {score.get("status","great_fit").replace("_"," ").title()}
            </h2>
            <p style="color:#64748b;">
                Budget: {money(budget)}<br>
                Estimated spend: {money(total_cost)}<br>
                Remaining: {money(max(remaining,0))}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# TRANSPORT
# ============================================================

if transport:

    st.markdown('<div class="section">Getting there</div>', unsafe_allow_html=True)

    t1, t2, t3 = st.columns(3)

    options = transport.get("options", {})

    transport_cards = [
        ("✈️ Flight", options.get("flight")),
        ("🚆 Train", options.get("train")),
        ("🚌 Bus", options.get("bus")),
    ]

    for col, (name, price) in zip(
        [t1, t2, t3],
        transport_cards,
    ):

        with col:

            if price:
                round_price = price * 2
                group_price = round_price * group_size

                st.markdown(
                    f"""
                    <div class="trip-card">
                        <span class="badge">ESTIMATED</span>
                        <h3>{name}</h3>
                        <h2>{money(price)}</h2>
                        <div style="color:#64748b;">
                        per person · one way<br>
                        Round trip: {money(round_price)}<br>
                        Group total: {money(group_price)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:

                st.markdown(
                    f"""
                    <div class="trip-card">
                        <h3>{name}</h3>
                        <div style="color:#94a3b8;">
                        Estimate unavailable
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# ITINERARY
# ============================================================

st.markdown('<div class="section">Optimized itinerary</div>', unsafe_allow_html=True)

places_by_id = {
    p["id"]: p
    for p in places
}

scheduled = [
    places_by_id[pid]
    for day in result["schedule"].values()
    for pid in day
]

if scheduled:

    with st.spinner("Generating AI guide descriptions..."):

        blurb_result = generate_guide_blurbs(
            scheduled,
            parsed["interests"],
        )

    blurbs = blurb_result.get("blurbs", {})

else:

    blurbs = {}


for day_idx in range(parsed["days"]):

    day_places = result["schedule"].get(day_idx, [])

    rainy = day_idx in rainy_days

    weather_text = " 🌧️ Rain expected" if rainy else ""

    st.markdown(
        f"""
        <div class="day-card">
            <div class="badge">DAY {day_idx + 1}</div>
            <h2 style="margin:4px 0 18px;">
                {destination.title()}{weather_text}
            </h2>
        """,
        unsafe_allow_html=True,
    )

    if not day_places:

        st.write("No stops scheduled.")

    for pid in day_places:

        p = places_by_id[pid]

        st.markdown(
            f"""
            <div class="place">
                <div class="place-name">
                    {p["name"]}
                </div>

                <div class="place-meta">
                    ₹{p["cost_inr"]} ·
                    {p["duration_minutes"]} minutes
                </div>

                <div class="reason">
                    {blurbs.get(
                        pid,
                        p.get("description_seed","")
                    )}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# REJECTED
# ============================================================

if result["rejected"]:

    st.markdown(
        '<div class="section">Why some places were skipped</div>',
        unsafe_allow_html=True,
    )

    labels = {
        "over_budget": "💸 Budget constraint",
        "time_conflict": "⏱️ Time constraint",
        "low_interest_match": "🎯 Low interest match",
    }

    for item in result["rejected"]:

        p = places_by_id.get(item["place_id"])

        if p:

            st.markdown(
                f"""
                <div class="trip-card">
                    <b>{p["name"]}</b><br>
                    <span style="color:#64748b;">
                    {labels.get(
                        item["reason"],
                        item["reason"]
                    )}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# PACKING
# ============================================================

st.markdown('<div class="section">Travel intelligence</div>', unsafe_allow_html=True)

with st.expander("🎒 Packing recommendations"):

    tips = generate_packing_tips(
        destination,
        parsed.get("month"),
        parsed["interests"],
    )

    for tip in tips.get("tips", []):
        st.write(f"• {tip}")


st.markdown("""
<div style="text-align:center;margin-top:50px;color:#94a3b8;font-size:13px;">
TravelMind · AI-powered constraint-based travel optimization
</div>
""", unsafe_allow_html=True)