<div align="center">
  <h1>🥗 Daily Meal Planner</h1>
  <p><i>Generate healthy, web-styled daily meal plans with images and narration — powered by Streamlit & OpenAI</i></p>
</div>

<br>

<div align="center">
  <a href="https://github.com/brej-29/daily-meal-planner-streamlit">
    <img alt="Last Commit" src="https://img.shields.io/github/last-commit/brej-29/daily-meal-planner-streamlit">
  </a>
  <img alt="Language" src="https://img.shields.io/badge/Language-Python-blue">
  <img alt="Framework" src="https://img.shields.io/badge/Framework-Streamlit-ff4b4b">
  <img alt="API" src="https://img.shields.io/badge/API-OpenAI-orange">
  <img alt="Libraries" src="https://img.shields.io/badge/Libraries-Requests%20%7C%20Pillow%20%7C%20BeautifulSoup%20%7C%20lxml-brightgreen">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-black">
</div>

<div align="center">
  <br>
  <b>Built with the tools and technologies:</b>
  <br><br>
  <code>Python</code> | <code>Streamlit</code> | <code>OpenAI</code> | <code>Requests</code> | <code>Pillow</code> | <code>BeautifulSoup</code> | <code>lxml</code>
</div>

---

## **Table of Contents**
* [Overview](#overview)
* [Features](#features)
* [Getting Started](#getting-started)
    * [Project Structure](#project-structure)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
    * [Configuration](#configuration)
    * [Usage](#usage)
* [License](#license)
* [Contact](#contact)

---

## **Overview**

Daily Meal Planner is an interactive Streamlit application that generates professional, web-styled daily meal plans (Breakfast, Lunch, Dinner) from user-provided ingredients and calorie targets. The app renders clean HTML fragments, generates optional dish images, and produces text-to-speech narration for each meal. It also persists generated images in session so your gallery remains visible while you continue exploring plans.

<br>

### **Project Highlights**

- **Web-Style Rendering:** Clean HTML fragment output (no full-page boilerplate) displayed safely in-app.
- **TTS Narration:** Convert any selected meal into MP3 narration.
- **Image Generation:** Create dish images and keep them in an in-app gallery.
- **Session Persistence:** Previously generated images remain visible during new actions.
- **Secure Secrets:** Use Streamlit Secrets for your OpenAI API key (no keys committed).

---

## **Features**

- Generate daily meal plans from a comma-separated ingredient list.
- Enforce calorie ceilings per day (configurable).
- Professional HTML fragment rendering for a polished, website-like presentation.
- Extract clean, human-readable text from HTML for narration (no CSS/boilerplate readouts).
- Generate and download dish images; images persist via session state.
- Download narrated MP3 for any selected meal.

---

## **Getting Started**

Follow these steps to set up and run the project locally.

### **Project Structure**

    meal-planner/
    ├─ app.py
    ├─ services/
    │  └─ openai_ops.py
    ├─ .streamlit/
    │  └─ secrets.toml           # contains your OPENAI_API_KEY (not committed)
    ├─ requirements.txt
    ├─ LICENSE                   # MIT License
    └─ README.md

### **Prerequisites**
- Python 3.9+ recommended
- An OpenAI API key

### **Installation**
1) Navigate to your project folder and (optionally) create a virtual environment.

        python -m venv .venv
        # Windows:
        .venv\Scripts\activate
        # macOS/Linux:
        source .venv/bin/activate

2) Install dependencies.

        pip install -r requirements.txt

### **Configuration**
1) Create `.streamlit/secrets.toml` (the folder and file may not exist by default).

        OPENAI_API_KEY = "sk-...your-key..."

2) Confirm that `app.py` reads from `st.secrets["OPENAI_API_KEY"]` (already wired).

3) Ensure you have **not** committed any secrets; `.streamlit/` stays local when you push to GitHub.

### **Usage**
1) Run the Streamlit app.

        streamlit run app.py

2) In the sidebar, set your daily kcal target and other generation preferences.

3) Enter ingredients (comma-separated) and generate your meal plan.

4) Use the **Images** section to generate dish images; images persist in the in-app gallery.

5) Use **Text-to-Speech** to create MP3 narration for any meal and download it.

---

## **License**
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## **Contact**
For questions or feedback, connect with me on [LinkedIn](https://www.linkedin.com/in/brejesh-balakrishnan-7855051b9/)
