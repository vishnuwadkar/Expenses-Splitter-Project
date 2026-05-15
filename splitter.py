def calculate_splits(assignments: dict, gst: float = 0) -> dict:
    """
    Takes a dictionary of person → list of items they owe,
    plus total GST amount. Returns total amount owed per person
    with GST split proportionally.

    Example input:
    {
        "Vishnu": [{"item": "Butter Chicken", "price": 280.0}],
        "Rahul":  [{"item": "Naan", "price": 60.0}]
    }
    gst = 50.0

    Example output:
    {
        "Vishnu": {"food": 280.0, "gst": 41.18, "total": 321.18},
        "Rahul":  {"food": 60.0,  "gst": 8.82,  "total": 68.82}
    }
    """
    # Calculate food totals per person
    food_totals = {}
    for person, items in assignments.items():
        food_totals[person] = round(sum(i["price"] for i in items), 2)

    # Total food bill (for proportional GST split)
    total_food = sum(food_totals.values())

    # Build result with GST split proportionally
    result = {}
    for person, food_amount in food_totals.items():
        if total_food > 0:
            person_gst = round(gst * (food_amount / total_food), 2)
        else:
            person_gst = round(gst / len(food_totals), 2) if food_totals else 0

        result[person] = {
            "food": food_amount,
            "gst": person_gst,
            "total": round(food_amount + person_gst, 2)
        }

    return result