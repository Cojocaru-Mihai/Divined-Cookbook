import json
import random
import requests
import time
import re
import customtkinter

API_URL = "https://en.wikibooks.org/w/api.php"
HEADERS = {"User-Agent": "Nostradamus-Cookbook/1.0 (NoDoxxingToday@example.com)"}

def load_data(filename="recipes_clean.json"):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def get_page_content(title, retries=3, backoff=2):
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
        "titles": title,
    }

    for attempt in range(retries):
        try:
            resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                revs = page.get("revisions")
                if revs:
                    return revs[0]["slots"]["main"]["*"]
            return "₍^. .^₎⟆ No recipe content found."

        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
            else:
                return f"₍^. .^₎⟆ Failed to fetch recipe: {e}"


def clean_wikitext(text: str) -> str:
    text = re.split(r"==\s*See also\s*==", text, flags=re.IGNORECASE)[0]
    text = re.sub(r"\[\[Category:[^\]]+\]\]", "", text)
    text = re.sub(r"\[\[[a-z\-]+:[^\]]+\]\]", "", text)
    text = re.sub(r"\{\{[^\}]+\}\}", "", text)
    text = re.sub(r"\[\[[^\|\]]+\|([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[\[(File|Image):[^\]]+\]\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def find_recipe_info(recipe, data):
    recipe_diff, recipe_time = None, None
    for diff, recipes in data.get("difficulty", {}).items():
        if recipe in recipes:
            recipe_diff = diff
            break
    for t, recipes in data.get("time", {}).items():
        if recipe in recipes:
            recipe_time = t
            break
    return recipe_diff, recipe_time


def pick_recipe(data, chosen_diff="", chosen_time=""):
    difficulty_set, time_set = set(), set()

    if chosen_diff and chosen_diff in data["difficulty"]:
        difficulty_set = set(data["difficulty"][chosen_diff])

    if chosen_time and chosen_time in data["time"]:
        time_set = set(data["time"][chosen_time])

    if chosen_diff and chosen_time:
        both = list(difficulty_set & time_set)
        if both:
            random.shuffle(both)
            return both[0]
        elif time_set:
            return random.choice(list(time_set))
        elif difficulty_set:
            return random.choice(list(difficulty_set))
    elif chosen_time and time_set:
        return random.choice(list(time_set))
    elif chosen_diff and difficulty_set:
        return random.choice(list(difficulty_set))
    else:
        all_recipes = []
        for lst in data["difficulty"].values():
            all_recipes.extend(lst)
        return random.choice(all_recipes)



class RecipeApp(customtkinter.CTk):
    def __init__(self, data):
        super().__init__()
        self.data = data

        self.geometry("900x700")
        self.title("✩₊˚.⋆☾⋆⁺₊✧")
        self.configure(fg_color="#6c63a6")

        # Difficulty OptionMenu
        self.diff_var = customtkinter.StringVar(value="")
        self.label1 = customtkinter.CTkLabel(self, text="Choose difficulty:", text_color="#242424")
        self.label1.pack(pady=(10, 0))

        self.option_menu1 = customtkinter.CTkOptionMenu(
            self,
            values=["₍^. .^₎⟆", '1', '2', '3', '4'],
            variable=self.diff_var,
            fg_color="#33265e",
            button_color="#33265e",
            text_color="#b3dad3",
        )
        self.option_menu1.pack(pady=5)

        self.time_var = customtkinter.StringVar(value="")
        self.label2 = customtkinter.CTkLabel(self, text="Choose time:", text_color="#242424")
        self.label2.pack(pady=(10, 0))

        self.option_menu2 = customtkinter.CTkOptionMenu(
            self,
            values=["₍^. .^₎⟆"] + list(data.get("time", {}).keys()),
            variable=self.time_var,
            fg_color="#33265e",
            button_color="#33265e",
            text_color="#b3dad3",
        )
        self.option_menu2.pack(pady=5)

        self.check_button = customtkinter.CTkButton(
            self,
            text="Fetch Recipe",
            command=self.show_recipe,
            fg_color="#33265e",
            text_color="#b3dad3",
        )
        self.check_button.pack(pady=10)

        self.recipe_box = customtkinter.CTkTextbox(
            self,
            wrap="word",
            width=760,
            height=350,
            fg_color="#33265e",
            text_color="#FFED91",
        )
        self.recipe_box.pack(pady=10)

        ascii_art = (
            "                   ＿＿ \n"
            "　　　　　🌸＞　　フ\n"
            "　　　　　| 　_　 _ l \n"
            "　 　　　／` ミ＿xノ  \n"
            "　　 　 /　　　 　 |\n"
            "　　　 /　 ヽ　　 ﾉ\n"
            "　 　 │　　|　|　|\n"
            "　／￣|　　 |　|　|\n"
            "　| (￣ヽ＿_ヽ_)__)\n"
            "　＼二つ\n"
        )
        self.recipe_box.insert("end", ascii_art.center(100))

        self.exit_button = customtkinter.CTkButton(
            self,
            text="Seal Your Fate",
            command=self.destroy,
            fg_color="#33265e",
            text_color="#FFED91",
        )
        self.exit_button.pack(pady=10)

    def show_recipe(self):
        chosen_diff = self.diff_var.get()
        chosen_time = self.time_var.get()

        if chosen_diff == "₍^. .^₎⟆":
            chosen_diff = ""
        if chosen_time == "₍^. .^₎⟆":
            chosen_time = ""

        recipe = pick_recipe(self.data, chosen_diff, chosen_time)
        raw_text = get_page_content(recipe)
        clean_text = clean_wikitext(raw_text)
        recipe_diff, recipe_time = find_recipe_info(recipe, self.data)

        self.recipe_box.delete("1.0", "end")
        self.recipe_box.insert("end", f"========== RECIPE =========\n{clean_text[:2000]}\n")
        self.recipe_box.insert(
            "end",
            f"\n========== INFO =========\nRecipe: {recipe}\nDifficulty: {recipe_diff if recipe_diff else 'Unknown'}\nTime: {recipe_time if recipe_time else 'Unknown'}\nLink: https://en.wikibooks.org/wiki/Cookbook:{recipe.replace(' ', '_')}\n",
        )


if __name__ == "__main__":
    random.seed(time.time())
    data = load_data()
    app = RecipeApp(data)
    app.mainloop()
