import streamlit as st
import os
from services.openai_ops import make_client, create_meals, parse_titles_from_output, generate_image, tts_recipe
import re
import streamlit.components.v1 as components  # for full HTML documents

st.set_page_config(page_title="Daily Meal Plan Pro", page_icon="🥗", layout="wide")

if "images_by_title" not in st.session_state:
    st.session_state["images_by_title"] = {}  # title -> bytes

# --- API key: prefer secrets, fallback to env ---
API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
if not API_KEY:
    st.error("Please add OPENAI_API_KEY to .streamlit/secrets.toml or environment.")
    st.stop()

client = make_client(API_KEY)

st.title("🥗 Daily Meal Plan — Pro")

def clean_title(s: str) -> str:
    # collapse all whitespace (incl. \n, \t) to single spaces
    return re.sub(r"\s+", " ", s).strip(" '\"\t\r\n")

def safe_filename(s: str) -> str:
    base = clean_title(s)
    # replace filesystem-unfriendly chars
    base = re.sub(r"[\\/<>:*?\"|]", "_", base)
    # optional: limit length
    return (base[:120]).rstrip("_") + ".png"

def _strip_md_fences(text: str) -> str:
    fence = re.compile(r"^\s*```(?:html|HTML)?\s*\n(.*?)\n\s*```\s*$", re.S)
    m = fence.match(text.strip())
    return m.group(1) if m else text

def render_model_output(out: str, prefer_height: int = 1100):
    cleaned = _strip_md_fences(out)
    looks_html = bool(re.search(r"<(section|div|article|h[1-6]|p|ul|ol|table|body|html)\b", cleaned, re.I))
    if looks_html:
        is_full_doc = bool(re.search(r"<!DOCTYPE|<html\b", cleaned, re.I))
        if is_full_doc:
            # Full HTML documents render in an iframe:
            components.html(cleaned, height=prefer_height, scrolling=True)
        else:
            # HTML fragments render inline, sanitized:
            st.html(cleaned)  # sanitized with DOMPurify
    else:
        st.markdown(cleaned)

with st.sidebar:
    st.header("Generation Settings")
    kcal = st.number_input("Max daily kcal", min_value=800, max_value=5000, value=2000, step=50)
    exact = st.checkbox("Use only the provided ingredients", value=False, help="Otherwise pantry staples allowed")
    model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4.1-nano"], index=0)
    temperature = st.slider("Creativity (temperature)", 0.0, 2.0, 1.0, 0.1)
    extra = st.text_input("Optional: extra style (e.g., spicy, South Indian, high-protein)")

with st.form("meal_form"):
    st.subheader("Ingredients")
    ingredients = st.text_area(
        "Enter ingredients (comma-separated)",
        placeholder="extra-virgin olive oil, whole grains, fresh fruits and vegetables, nuts and seeds, fish, eggs, fermented foods, honey",
        height=100
    )
    submitted = st.form_submit_button("Generate Meal Plan")

if submitted:
    with st.spinner("Cooking up a plan..."):
        output = create_meals(
            client=client,
            ingredients=ingredients,
            kcal=int(kcal),
            exact_ingredients=exact,
            model=model,
            temperature=float(temperature),
            extra=extra or None
        )
        st.session_state["raw_output"] = output
        st.success("Meal plan generated.")

if "raw_output" in st.session_state:
    out = st.session_state["raw_output"]

    # Render the plan
    st.subheader("Plan")
    render_model_output(out, prefer_height=1200)

    # Extract titles
    titles = [clean_title(t) for t in parse_titles_from_output(out)]
    if titles:
        st.write("**Detected recipes:**", ", ".join(titles))

        # Image generation buttons
        st.subheader("Images")
        img_cols = st.columns(min(3, len(titles)))
        for i, title in enumerate(titles[:3]):
            if img_cols[i].button(f"Generate image: {clean_title(title)}", key=f"imgbtn_{i}"):
                with st.spinner(f"Generating image for “{clean_title(title)}”..."):
                    bio = generate_image(client, title, extra="white background")
                    st.session_state["images_by_title"][clean_title(title)] = bio.getvalue()  # persist bytes
                    img_cols[i].image(bio, caption=clean_title(title))
                    st.download_button("Download image", data=bio.getvalue(), file_name=safe_filename(bio.name), mime="image/png", key=f"dl_{i}")

    # TTS section
    st.subheader("Text-to-Speech")
    meal_choice = st.selectbox("Pick a meal to narrate", ["Breakfast", "Lunch", "Dinner"])
    # Use our HTML-aware extractors
    from services.openai_ops import extract_meal_section, html_to_text
    meal_html = extract_meal_section(out, meal_choice)
    recipe_text = html_to_text(meal_html) if meal_html else ""

    if st.button("Generate narration"):
        with st.spinner("Generating audio..."):
            audio_bytes = tts_recipe(client, recipe_text, voice="alloy")
            st.audio(audio_bytes, format="audio/mpeg")
            st.download_button("Download MP3", data=audio_bytes, file_name=f"{meal_choice}.mp3", mime="audio/mpeg")
    
    st.subheader("Image gallery")
    if st.session_state["images_by_title"]:
        for t, img_bytes in st.session_state["images_by_title"].items():
            st.image(img_bytes, caption=t)
            st.download_button(f"Download {t}", data=img_bytes, file_name=safe_filename(t), mime="image/png", key=f"dl_{t}")
    else:
        st.caption("No images yet.")