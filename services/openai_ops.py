import os, io, shutil, requests
from typing import Optional, List
from openai import OpenAI
import re
import tempfile
from bs4 import BeautifulSoup
from pathlib import Path

def make_client(api_key: Optional[str] = None) -> OpenAI:
    # Looks in explicit arg, then env var. Streamlit version will pass st.secrets
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY")
    return OpenAI(api_key=api_key)

def create_meals(client: OpenAI,
                 ingredients: str,
                 kcal: int = 2000,
                 exact_ingredients: bool = False,
                 output_format: str = "HTML and CSS",
                 model: str = "gpt-3.5-turbo",
                 system_role: str = "You are a skilled cook and dietitian with expertise of a chef.",
                 temperature: float = 1.0,
                 extra: Optional[str] = None) -> str:
    prompt = f"""
Create a healthy daily meal plan for breakfast, lunch, and dinner based on the following ingredients: ```{ingredients}```
Return a SINGLE **HTML fragment** (no <!doctype>, <html>, <head>, or <body>, and **do not** wrap in triple backticks).
Structure it exactly as:

<section id="meal-plan">
  <h1>Daily Meal Plan</h1>

  <section data-meal="Breakfast">
    <h2>Breakfast: {{TITLE}}</h2>
    <p>Total Calories: …, Servings: …</p>
    <p>Prep Time: …, Cook Time: …, Total Time: …</p>
    <ol>…Multiple detailed steps…</ol>
  </section>

  <section data-meal="Lunch">…same format…</section>
  <section data-meal="Dinner">…same format…</section>

  <p id="titles" hidden>{{TITLE_BREAKFAST}}, {{TITLE_LUNCH}}, {{TITLE_DINNER}}</p>
</section>

Follow the instructions below carefully.

### Instructions:
1. {'Use ONLY the provided ingredients with salt, pepper, and spices.' if exact_ingredients else 'Feel free to incorporate other common pantry staples.'}
2. Specify the exact amount of each ingredient.
3. Ensure that the total daily calorie intake is below {kcal}.
4. For each meal, explain each recipe, step by step, in clear and simple sentences. Use bullet points or numbers to organize the steps.
5. For each meal, specify the total number of calories and the number of servings.
6. For each meal, provide a concise and descriptive title that summarizes the main ingredients and flavors. The title should not be generic.
7. For each recipe, indicate the prep, cook and total time.
{('8. If possible the meals should be:' + extra) if extra else ''}

Before answering, make sure that you have followed the instructions listed above (points 1 to 7 or 8).
The last line of your answer should be a string that contains ONLY the titles of the recipes and nothing more with a comma in between.
Example of the last line of your answer:
'\\nBroccoli and Egg Scramble, Grilled Chicken and Vegetable, Baked fish and Cabbage Slaw'.
"""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role":"system","content":system_role},
            {"role":"user","content":prompt}
        ],
        temperature=temperature
    )
    return resp.choices[0].message.content

def parse_titles_from_output(output: str) -> List[str]:
    last = output.splitlines()[-1]
    titles = [re.sub(r"\s+", " ", t).strip(" '\"\t\r\n") for t in last.split(",")]
    return [t for t in titles if t]

def generate_image(client: OpenAI, title: str,
                   model: str = "dall-e-3",
                   size: str = "1024x1024",
                   quality: str = "standard",
                   extra: str = "") -> str:
    image_prompt = f"{title}, hd quality, {extra}".strip().strip(",")
    gen = client.images.generate(
        model=model,
        prompt=image_prompt,
        style="natural",
        size=size,
        quality=quality
    )
    url = gen.data[0].url
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    # Return in-memory bytes and URL; Streamlit can display directly.
    bio = io.BytesIO(r.content)
    bio.name = f"{title}.png"
    return bio

def tts_recipe(client: OpenAI, text: str, voice: str = "alloy") -> bytes:
    # Streams server audio directly to a file path
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
        tmp_path = Path(tf.name)

    with client.audio.speech.with_streaming_response.create(
        model="tts-1",             # or gpt-4o-mini-tts if you prefer
        voice=voice,
        input=text,
        response_format="mp3"
    ) as response:
        response.stream_to_file(tmp_path.as_posix())  # <-- expects a string path

    # Return bytes for Streamlit
    audio_bytes = tmp_path.read_bytes()
    try:
        tmp_path.unlink(missing_ok=True)  # clean up
    except Exception:
        pass
    return audio_bytes

def html_to_text(html: str) -> str:
    """Remove <style>/<script> and return readable text."""
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["style", "script", "noscript"]):
        t.decompose()
    # Collapse whitespace and keep logical breaks
    text = soup.get_text(separator="\n")
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())

def extract_meal_section(html_fragment_or_doc: str, meal_name: str) -> str:
    """Return inner HTML for the requested meal section, else empty string."""
    soup = BeautifulSoup(html_fragment_or_doc, "lxml")
    # First try our structured sections
    node = soup.select_one(f'section[data-meal="{meal_name}"]')
    if not node:
        # Fallback: a heading starting with 'Breakfast:' etc.
        h = soup.find(lambda tag: tag.name in ["h2", "h3"] and tag.get_text().strip().startswith(meal_name))
        if h:
            # collect siblings until next heading
            html_parts = [str(h)]
            for sib in h.find_all_next():
                if sib.name in ["h1", "h2", "h3"] and sib is not h:
                    break
                html_parts.append(str(sib))
            return "".join(html_parts)
        return ""
    # Inner HTML of the meal section
    return "".join(str(c) for c in node.contents)