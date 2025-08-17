from flask import Flask, request, render_template, send_from_directory, jsonify, url_for
from werkzeug.utils import secure_filename
import os
import numpy as np
import pickle
from visual_search import VisualSearch
from rl_recommender import recommend_products

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static",
)

app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

from os.path import basename
app.jinja_env.filters['basename'] = basename

# Load visual search
try:
    visual_search = VisualSearch(
        data_csv="data/processed_images.csv",
        embeddings_file="models/embeddings/embeddings.pkl"
    )
except FileNotFoundError as e:
    print(f"Error loading visual search data: {e}")
    raise e

# Load embeddings for RL recommender
try:
    with open("models/embeddings/embeddings.pkl", "rb") as f:
        all_embeddings = pickle.load(f)
except FileNotFoundError as e:
    print(f"Error loading embeddings: {e}")
    all_embeddings = None

@app.route("/data/processed_images/<path:filename>")
def serve_image(filename):
    return send_from_directory("../data/processed_images", filename)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            # Visual Search
            try:
                results = visual_search.search_similar(file_path)
            except Exception as e:
                print(f"Visual search error: {e}")
                results = []

            # RL Recommendation using embeddings
            try:
                query_embedding = visual_search.get_embedding(file_path)  # 512-dim embedding
                recommended_index = recommend_products("models/dqn_model/dqn_recommender", query_embedding)
                recommendation = visual_search.data.iloc[recommended_index][["product_id", "category", "color", "image_path"]].to_dict()
            except Exception as e:
                print(f"Recommendation error: {e}")
                recommendation = visual_search.data.iloc[np.random.randint(0, len(visual_search.data))][["product_id", "category", "color", "image_path"]].to_dict()

            return jsonify({
                "results": results,
                "recommendation": recommendation,
                "uploaded_image": filename,
                "uploaded_image_url": url_for('static', filename=f'uploads/{filename}')
            })
    return render_template("index.html")


@app.route("/results.html", methods=["GET"])
def results_page():

    return render_template("results.html")

@app.route("/team", methods=["GET"])
def team_page():
    return render_template("team.html")

if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(debug=True)