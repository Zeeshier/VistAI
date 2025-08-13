import os
import torch
import clip
from PIL import Image
import faiss
import numpy as np
import pandas as pd
import pickle

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

class VisualSearch:
    def __init__(self, data_csv="data/processed_images.csv", index_file="models/embeddings/faiss_index.bin", embeddings_file="models/embeddings/embeddings.pkl"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device, download_root="models/clip_model")
        self.data = pd.read_csv(data_csv)
        self.image_paths = self.data["image_path"].tolist()
        self.index_file = index_file
        self.embeddings_file = embeddings_file

        if os.path.exists(index_file) and os.path.exists(embeddings_file):
            print("📂 Loading existing FAISS index and embeddings...")
            self.index = faiss.read_index(index_file)
            with open(self.embeddings_file, "rb") as f:
                self.embeddings = pickle.load(f)
        else:
            print("⚙️ Building new FAISS index...")
            self.index, self.embeddings = self.build_index()
            os.makedirs(os.path.dirname(index_file), exist_ok=True)
            faiss.write_index(self.index, index_file)
            with open(self.embeddings_file, "wb") as f:
                pickle.dump(self.embeddings, f)

    def build_index(self):
        embeddings = []
        for path in self.image_paths:
            image = self.preprocess(Image.open(path)).unsqueeze(0).to(self.device)
            with torch.no_grad():
                embedding = self.model.encode_image(image).cpu().numpy()
            embeddings.append(embedding)
        embeddings = np.vstack(embeddings)

        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)

        return index, embeddings

    def get_embedding(self, image_path):
        """Return the 512-dim CLIP embedding for a given image."""
        image = self.preprocess(Image.open(image_path)).unsqueeze(0).to(self.device)
        with torch.no_grad():
            embedding = self.model.encode_image(image).cpu().numpy()
        return embedding.flatten()

    def search_similar(self, image_path, k=5):
        """Find k similar T-shirts based on the uploaded image."""
        query_embedding = self.get_embedding(image_path)
        distances, indices = self.index.search(query_embedding.reshape(1, -1), k)
        return self.data.iloc[indices[0]][["product_id", "category", "color", "image_path"]].to_dict("records")

if __name__ == "__main__":
    visual_search = VisualSearch()
    results = visual_search.search_similar("static/uploads/test_image.jpg")
    print("Similar Products:", results)