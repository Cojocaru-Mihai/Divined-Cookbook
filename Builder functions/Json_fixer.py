import json
import re

BUCKETS = [15, 30, 60, 90, 120, 180]


def normalize_time_key(time_str):
    numbers = re.findall(r"\d+", time_str)
    if not numbers:
        return "Very long"

    minutes = 0
    time_str_lower = time_str.lower()

    if "hour" in time_str_lower:
        hours = int(numbers[0])
        minutes = hours * 60
        if len(numbers) > 1:
            minutes += int(numbers[1])
    else:
        minutes = int(numbers[0])

    for b in BUCKETS:
        if minutes <= b:
            return str(b)
    return "Very long"


def normalize_difficulty_key(diff_str):
    numbers = re.findall(r"\d+", diff_str)
    if not numbers:
        return "unknown"

    num = int(numbers[0])
    if num in (7, 8, 30):
        return "unknown"
    return str(num)


def normalize_categories(filename="recipes.json", out_file="recipes_clean.json"):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    new_time = {}
    for key, recipes in data.get("time", {}).items():
        bucket = normalize_time_key(key)
        new_time.setdefault(bucket, []).extend(recipes)

    sorted_time = {}
    numeric_time_keys = sorted(
        [k for k in new_time.keys() if k.isdigit()],
        key=lambda x: int(x)
    )
    for k in numeric_time_keys:
        sorted_time[k] = new_time[k]
    if "Very long" in new_time:
        sorted_time["Very long"] = new_time["Very long"]

    data["time"] = sorted_time

    new_difficulty = {}
    for key, recipes in data.get("difficulty", {}).items():
        bucket = normalize_difficulty_key(key)
        new_difficulty.setdefault(bucket, []).extend(recipes)

    sorted_difficulty = {}
    numeric_keys = sorted(
        [k for k in new_difficulty.keys() if k.isdigit()],
        key=lambda x: int(x)
    )
    for k in numeric_keys:
        sorted_difficulty[k] = new_difficulty[k]
    if "unknown" in new_difficulty:
        sorted_difficulty["unknown"] = new_difficulty["unknown"]

    data["difficulty"] = sorted_difficulty

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"₍^. .^₎⟆ Normalized categories saved to {out_file}")


if __name__ == "__main__":
    normalize_categories("recipes.json", "recipes_clean.json")
