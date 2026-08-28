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

## Setup (everyone runs this once)

```bash
git clone <your-repo-url>
cd travelmind
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Then open `.env` and add your `ANTHROPIC_API_KEY`.

## Run the app

```bash
streamlit run app.py
```

This opens the app in your browser, usually at `http://localhost:8501`.

## Test individual pieces without running the whole app

```bash
python -m llm.parse_constraints        # test the constraint parser
python -m llm.recommend_destination    # test destination suggestion
python -m optimizer.model              # test the OR-Tools scheduler
python -m weather.weather_check        # test weather fetch (no API key needed)
python data/train_data.py              # test train fare lookup
```

## Currently supported cities

Only `chennai` has curated data right now (see `data/places.json`). Add more
cities by adding a new top-level key to `places.json` and `hotels.json`, and
a matching entry in `weather/weather_check.py`'s `CITY_COORDS`, and
`llm/recommend_destination.py`'s `AVAILABLE_CITIES`.

## Known scoping decisions (intentional, not shortcuts)

- **Flight/bus costs are ESTIMATED**, not live — clearly labeled in
  `data/transport_estimates.json`. Live booking APIs weren't feasible in
  hackathon time. Train costs attempt a real public rail data source with
  graceful fallback to estimates (`data/train_data.py`).
- **Live re-plan only re-runs the optimizer**, not the LLM parsing or data
  fetching — that's what keeps slider updates under 1-2 seconds.

## Architecture

```
User input (plain English)
      │
      ▼
parse_constraints()  [LLM]  ──► if no destination ──► recommend_destination() [LLM]
      │
      ▼
load places/hotels/transport for city  [JSON data layer]
      │
      ▼
weather check  ──► flags rainy days
      │
      ▼
solve_itinerary()  [OR-Tools]  ──► schedule + rejected places w/ reasons
      │                              ▲
      │                              │ re-runs on slider change (fast)
      ▼
generate_guide_blurbs() + generate_packing_tips()  [LLM]
      │
      ▼
Trip Score + per-person cost
      │
      ▼
Streamlit renders itinerary
```

## Checkpoints

- Hour 4: first merge — data schema locked, stub functions wired
- Hour 8: second merge — real logic in each module, basic end-to-end works
- Hour 12: third merge — polish, weather integration, demo rehearsal
- Hour 15: ship it
