import csv
from pathlib import Path

in_file  = 'data/metadata.csv'
out_file = 'data/processed_images.csv'

# collect all distinct colors
colors = set()
with open(in_file, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        colors.add(row['color'].strip().lower())
colors = sorted(colors)          # deterministic order
color2idx = {c: i for i, c in enumerate(colors)}

# one-hot vectors
with open(in_file, newline='') as fin, open(out_file, 'w', newline='') as fout:
    reader = csv.DictReader(fin)
    writer = csv.writer(fout)

    # header: image_path,product_id,category,color,color1,color2,...,colorN
    writer.writerow(['image_path', 'product_id', 'category', 'color'] + colors)

    for row in reader:
        img_path   = row['image_path']
        product_id = row['product_id']
        category   = row['category']
        true_color = row['color'].strip().lower()

        vec = [0.0] * len(colors)
        vec[color2idx[true_color]] = 1.0

        writer.writerow([img_path, product_id, category, true_color] + vec)
