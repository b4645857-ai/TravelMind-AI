"""
trip_score.py — feature #8.

Computes the "Trip Score" (how well the plan fits the budget) and
per-person cost when group_size > 1.
"""


def compute_trip_score(total_cost_inr: int, budget_inr: int) -> dict:
    """
    Trip Score = how efficiently the budget was used, capped at 100.
    - 100 = used the full budget (or very close) without going over
    - Going under budget by a lot scores lower (money left on the table)
    - Going over budget is impossible by construction (optimizer enforces
      the budget as a hard constraint), but we guard for it anyway.

    Returns:
        { "score": int (0-100), "budget_used_pct": float, "status": str }
    """
    if budget_inr <= 0:
        return {"score": 0, "budget_used_pct": 0.0, "status": "invalid_budget"}

    used_pct = round((total_cost_inr / budget_inr) * 100, 1)

    if used_pct > 100:
        score = 0
        status = "over_budget"
    elif used_pct >= 85:
        score = round(90 + (used_pct - 85) / 1.5)  # 90-100 range
        status = "great_fit"
    elif used_pct >= 60:
        score = round(60 + (used_pct - 60) * 1.2)  # 60-90 range
        status = "good_fit"
    else:
        score = round(used_pct)  # low usage = low score, room left unused
        status = "underused_budget"

    return {"score": min(int(score), 100), "budget_used_pct": used_pct, "status": status}


def compute_per_person_cost(total_cost_inr: int, group_size: int) -> int:
    if group_size <= 0:
        group_size = 1
    return round(total_cost_inr / group_size)


if __name__ == "__main__":
    print(compute_trip_score(7600, 8000))
    print(compute_per_person_cost(7600, 4))
