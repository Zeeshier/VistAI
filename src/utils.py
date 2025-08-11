import pandas as pd
import numpy as np
from faker import Faker
import os

def generate_metadata(num_images=1000, output_path="data/product_images.csv"):
    fake = Faker()
    categories = ["tshirt"]  
    colors = ["red", "blue", "green", "black", "white"]
    
    data = {
        "image_path": [f"data/images/{i+1}.jpg" for i in range(num_images)],
        "product_id": [f"tshirt_{i+1}" for i in range(num_images)],
        "category": [np.random.choice(categories) for _ in range(num_images)],
        "color": [np.random.choice(colors) for _ in range(num_images)]
    }
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Metadata saved to {output_path}")

if __name__ == "__main__":
    os.makedirs("data/images", exist_ok=True)
    generate_metadata()