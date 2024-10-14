from flask import Flask, render_template, request, redirect, url_for
import os
import re
import time
import requests
import json
from datetime import datetime, timedelta
from pytrends.request import TrendReq
import random

app = Flask(__name__)

# Sanitize the filename to prevent illegal characters
def sanitize_filename(name):
    return re.sub(r'[\/*?:"<>|]', "", name)

# Record trending words to a log file
def record_trending_words(words):
    log_file = 'trending_words_log.json'
    current_time = datetime.now().isoformat()
    if not os.path.exists(log_file):
        with open(log_file, 'w') as file:
            json.dump([], file)
    
    with open(log_file, 'r') as file:
        data = json.load(file)
    
    # Append new records
    for word in words:
        data.append({"word": word, "timestamp": current_time})
    
    # Remove records older than 7 days
    seven_days_ago = datetime.now() - timedelta(days=7)
    data = [entry for entry in data if datetime.fromisoformat(entry['timestamp']) > seven_days_ago]
    
    with open(log_file, 'w') as file:
        json.dump(data, file)

# Fetch trending words based on country, focusing on events
def fetch_trending_words(country):
    pytrends = TrendReq(hl='en-US', tz=360)
    region = get_region_code(country)
    if region is None:
        print(f"Region code not found for country: {country}")
        return []
    try:
        trending_searches_df = pytrends.trending_searches(pn=region)
        trending_words = trending_searches_df[0].tolist()
        # Filter out words that are likely related to people rather than events
        filtered_words = [word for word in trending_words if not is_person_related(word)]
        top_events = filtered_words[:10]  # Get the top 10 events
        record_trending_words(top_events)
        return top_events
    except Exception as e:
        print(f"Error fetching general trending searches for region {region}: {e}")
        return []

# Function to check if a word is likely related to a person
def is_person_related(word):
    # Simple heuristic: check if the word contains common person-related terms
    person_keywords = ['president', 'minister', 'actor', 'celebrity', 'singer', 'player', 'coach', 'leader']
    return any(keyword in word.lower() for keyword in person_keywords)

# Convert the country name to the region code required by Google Trends
def get_region_code(country_name):
    country_name = country_name.lower()
    region_mapping = {
        'united states': 'united_states',
        'canada': 'canada',
        'united kingdom': 'united_kingdom',
        'australia': 'australia',
    }
    return region_mapping.get(country_name)

# Generate an image from text using the Hugging Face API
def generate_image_from_text(text_description, output_dir='static/generated_images', max_retries=5):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
    headers = {"Authorization": f"Bearer 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"}  # Replace with your API token

    payload = {
        "inputs": f"low resolution illustration of {text_description}",
    }

    retries = 0
    while retries < max_retries:
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                image_data = response.content
                filename = sanitize_filename(text_description)
                image_path = os.path.join(output_dir, f"{filename}.png")
                with open(image_path, 'wb') as handler:
                    handler.write(image_data)
                return f"generated_images/{filename}.png"
            
            elif response.status_code == 503:
                estimated_time = response.json().get("estimated_time", 60)
                time.sleep(min(estimated_time, 60))
                retries += 1
            else:
                print(f"Error generating image: Status code {response.status_code}, Error message: {response.content}")
                break
        except Exception as e:
            print(f"An error occurred while generating image for '{text_description}': {e}")
            break

    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and 'generate_images' in request.form:
        country = request.form.get('country')
        trending_words = fetch_trending_words(country)
        if trending_words:
            selected_word = random.choice(trending_words)
            image_path = generate_image_from_text(selected_word)
            if image_path:
                return render_template('index.html', image_paths=[image_path], country=country, next_word=selected_word, remaining_words=trending_words)
    return render_template('index.html', image_paths=None, next_word=None, remaining_words=None)

@app.route('/generate_next_image', methods=['POST'])
def generate_next_image():
    next_word = request.form.get('next_word')
    remaining_words = json.loads(request.form.get('remaining_words'))

    if next_word and remaining_words:
        image_path = generate_image_from_text(next_word)
        if image_path:
            remaining_words.remove(next_word)
            if remaining_words:
                next_word = random.choice(remaining_words)
            else:
                next_word = None
            return render_template('index.html', image_paths=[image_path], country=request.form.get('country'), next_word=next_word, remaining_words=remaining_words)

    return render_template('index.html', image_paths=None, next_word=None, remaining_words=None)

if __name__ == '__main__':
    app.run(debug=True)