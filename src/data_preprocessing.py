import cv2
import os
import glob

def preprocess_images(input_dir="data/images", output_dir="data/processed_images"):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    image_paths = glob.glob(os.path.join(input_dir, "*.jpg"))
    
    # Resize and normalize images
    for idx, img_path in enumerate(image_paths):
        img = cv2.imread(img_path)
        if img is not None:
            img = cv2.resize(img, (224, 224))  # CLIP input size
            img = img / 255.0  # Normalize to [0, 1]
            output_path = os.path.join(output_dir, f"image{idx+1}.jpg")
            cv2.imwrite(output_path, img * 255)

if _name_ == "_main_":
    preprocess_images()
