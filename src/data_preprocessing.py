import cv2
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
import os

def preprocess_images_and_metadata(input_csv="data/product_images.csv", output_csv="data/processed_images.csv"):
    # Load metadata
    df = pd.read_csv(input_csv)
    
    # Resize and normalize images
    os.makedirs("data/processed_images", exist_ok=True)
    for idx, row in df.iterrows():
        img_path = row["image_path"]
        img = cv2.imread(img_path)
        if img is not None:
            img = cv2.resize(img, (224, 224))  # CLIP input size
            img = img / 255.0  # Normalize to [0, 1]
            cv2.imwrite(f"data/processed_images/image{idx+1}.jpg", img * 255)
            df.loc[idx, "image_path"] = f"data/processed_images/image{idx+1}.jpg"
    
    # Encode metadata
    encoder = OneHotEncoder(sparse_output=False)
    encoded_metadata = encoder.fit_transform(df[["category", "color"]])
    encoded_df = pd.DataFrame(encoded_metadata, columns=encoder.get_feature_names_out())
    df = pd.concat([df, encoded_df], axis=1)
    
    # Save processed data
    df.to_csv(output_csv, index=False)
    print(f"Processed data saved to {output_csv}")

if __name__ == "__main__":
    preprocess_images_and_metadata()