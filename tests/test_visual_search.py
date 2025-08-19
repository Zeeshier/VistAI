import os
import pytest
import pandas as pd
import numpy as np
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.visual_search import VisualSearch

# Get the base test directory
TEST_DIR = Path(__file__).parent
DATA_DIR = TEST_DIR / 'data'
TEST_CSV = DATA_DIR / 'metadata.csv'

# Ensure the images directory exists
IMAGES_DIR = DATA_DIR / 'images'
IMAGES_DIR.mkdir(exist_ok=True)


# Update the metadata CSV with correct paths
def update_metadata_csv():
    # Read the existing CSV
    df = pd.read_csv(TEST_CSV)
    
    # Update the image paths to be relative to the test data directory
    df['image_path'] = df['image_path'].apply(
        lambda x: str(IMAGES_DIR / Path(x).name)
    )
    
    df.to_csv(TEST_CSV, index=False)

# Update the metadata CSV with correct paths
update_metadata_csv()

@pytest.fixture(scope="module")
def visual_search():
    # Create a temporary directory for test outputs
    with tempfile.TemporaryDirectory() as temp_dir:
        index_file = Path(temp_dir) / 'test_faiss.index'
        embeddings_file = Path(temp_dir) / 'test_embeddings.pkl'
        
        # Initialize with test data
        vs = VisualSearch(
            data_csv=str(TEST_CSV),
            index_file=str(index_file),
            embeddings_file=str(embeddings_file)
        )
        yield vs

def test_csv_loaded(visual_search):
    assert hasattr(visual_search, 'data')
    assert not visual_search.data.empty
    assert 'product_id' in visual_search.data.columns
    assert 'image_path' in visual_search.data.columns
    assert len(visual_search.data) == 5  

    # Verify the first image exists
    first_img = Path(visual_search.data["image_path"].iloc[0])
    assert first_img.exists(), f"Test image not found at {first_img}"

def test_embedding_generation(visual_search):
    test_img = visual_search.data["image_path"].iloc[0]
    test_img_path = Path(test_img)
    
    assert test_img_path.exists(), f"Test image not found at {test_img_path}"
    
    embedding = visual_search.get_embedding(str(test_img_path))
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape[0] == 512  # CLIP ViT-B/32 outputs 512-dim embeddings

def test_search_returns_results(visual_search):
    test_img = visual_search.data["image_path"].iloc[0]
    test_img_path = Path(test_img)
    
    results = visual_search.search_similar(str(test_img_path), k=3)
    
    assert isinstance(results, list)
    assert len(results) == 3 
    assert all("product_id" in r for r in results)
    assert all("color" in r for r in results)

def test_search_with_invalid_k(visual_search):
    test_img = visual_search.data["image_path"].iloc[0]
    test_img_path = Path(test_img)
    
    # Test with k=1 (minimum valid value)
    results = visual_search.search_similar(str(test_img_path), k=1)
    assert len(results) == 1
    
    k = len(visual_search.data) + 10
    results = visual_search.search_similar(str(test_img_path), k=k)
    
    unique_results = {r['product_id'] for r in results}
    assert len(unique_results) <= len(visual_search.data)

def test_search_with_invalid_image(visual_search):
    with pytest.raises(FileNotFoundError):
        visual_search.search_similar("non_existent_image.jpg")

