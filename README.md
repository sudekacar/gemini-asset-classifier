🎮 Generative AI Game Asset Classifier (Gemini Vision API)

This project is an MLOps tool designed to automatically analyze and tag (generate metadata for) game development assets (image files) using the Google Gemini Vision API and Structured JSON Schema.

📰 Featured Medium Article

You can find the detailed article explaining the technical specifics of this project, why Structured JSON was used, and how MLOps principles were applied:

[Article Title: Redefining Game Development: Automating Asset Classification with the Gemini Vision API]

[(https://medium.com/@sudeykacar/redefining-game-development-automating-asset-classification-with-the-gemini-vision-api-8cfa2c9ef697)]

🎯 Project Goal

To eliminate the inconsistency and slowness caused by manual metadata entry in game development pipelines. The tool generates a category (Character, Environment Object), a main theme (Sci-Fi Minimalist), and critical tags (Requires Animation, Low Poly) for every asset.

✨ Key Features

Generative AI Classification: Visual analysis and tagging using the Gemini 2.5 Flash model.

Structured JSON Output: Consistent and machine-readable output guaranteed by a predefined JSON schema.

MLOps Observability: tqdm integration provides crucial progress visualization during the processing of large batches of files.

Persistent Storage: All results are saved to an asset_classification_results.json file.

Command-Line Filtering: Ability to perform instant searches by tag, category, or theme directly from the command line.

🚀 Setup and Running

1. Environment Preparation

Install the required Python libraries using the requirements.txt file:

pip install -r requirements.txt


2. API Key Configuration

Set your Gemini API key (obtained from Google AI Studio) as an environment variable.

Linux/macOS:

export GEMINI_API_KEY="YOUR_API_KEY"


Windows (Git Bash/CMD):

export GEMINI_API_KEY="YOUR_API_KEY"


3. Adding Assets

Place the image assets (.png or .jpg files) you want to process (e.g., car.jpg, explosion.png) in the same folder as the asset_processor.py file.

4. Running the Program

A. Standard Run (Process All Assets)

All assets are processed, results are displayed in the terminal, and saved to asset_classification_results.json.

python asset_processor.py


B. Filtered Run (Search Specific Tag or Category)

Add an argument to display only the results that match a specific tag, category, or theme.

# Filter for assets containing the 'Animation' tag or theme
python asset_processor.py Animasyon 
# (You can use Turkish words here if the tags are in Turkish, or the English equivalent)


# Filter for assets only in the 'Vehicle' category
python asset_processor.py Vehicle


Author: Sude Yaren Kacar
License: MIT License
