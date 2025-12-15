from sklearn.model_selection import train_test_split
import os
import shutil

dataset_path = "C:/Users/JEEVA/Downloads/plantvillage dataset/color"  # <<< IMPORTANT
output_path = "data"

classes = os.listdir(dataset_path)

for cls in classes:
    class_path = os.path.join(dataset_path, cls)
    images = os.listdir(class_path)

    # Skip empty folders
    if len(images) == 0:
        continue

    # Split dataset
    train_imgs, test_imgs = train_test_split(images, test_size=0.2, random_state=42)
    train_imgs, val_imgs = train_test_split(train_imgs, test_size=0.1, random_state=42)

    # Create output folders
    for split in ["train", "val", "test"]:
        os.makedirs(os.path.join(output_path, split, cls), exist_ok=True)

    # Copy images
    for img in train_imgs:
        shutil.copy(os.path.join(class_path, img), os.path.join(output_path, "train", cls))

    for img in val_imgs:
        shutil.copy(os.path.join(class_path, img), os.path.join(output_path, "val", cls))

    for img in test_imgs:
        shutil.copy(os.path.join(class_path, img), os.path.join(output_path, "test", cls))

print("Dataset split completed successfully!")
