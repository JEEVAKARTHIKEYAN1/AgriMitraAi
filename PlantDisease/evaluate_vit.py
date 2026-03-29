import os
import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets
from transformers import ViTForImageClassification, ViTImageProcessor
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# -----------------------------
# PATHS (LOCAL WINDOWS PATHS)
# -----------------------------
# Assuming you ran the split and have 'data/test' and the trained model folder
test_dir = "./data/test" 
model_dir = "./vit-plant-disease-final" 

if not os.path.exists(test_dir):
    print(f"Error: Test directory '{test_dir}' not found. Ensure you are running this from the PlantDisease directory.")
    exit(1)

if not os.path.exists(model_dir):
    print(f"Error: Model directory '{model_dir}' not found. Make sure the vit-plant-disease-final folder is here.")
    exit(1)

# -----------------------------
# LOAD TEST DATA
# -----------------------------
print("Loading Test Dataset...")
test_ds = datasets.ImageFolder(test_dir)
print(f"Test size: {len(test_ds)}")
print(f"Number of classes: {len(test_ds.classes)}")

# -----------------------------
# LOAD PRE-TRAINED MODEL
# -----------------------------
print(f"Loading existing trained model from {model_dir}...")
processor = ViTImageProcessor.from_pretrained(model_dir)
model = ViTForImageClassification.from_pretrained(model_dir)
model.to(device)
model.eval()

# -----------------------------
# CUSTOM DATASET CLASS (EVAL ONLY)
# -----------------------------
class ViTTestDataset(Dataset):
    def __init__(self, dataset, processor):
        self.dataset = dataset
        self.processor = processor

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        img, label = self.dataset[idx]
        encoded = self.processor(img, return_tensors="pt")
        encoded = {k: v.squeeze(0) for k, v in encoded.items()}
        encoded["labels"] = torch.tensor(label)
        return encoded

test_dataset = ViTTestDataset(test_ds, processor)
test_loader = DataLoader(test_dataset, batch_size=8, shuffle=False)

# -----------------------------
# TEST EVALUATION
# -----------------------------
all_preds = []
all_labels = []

print("Running inference on test dataset safely without training...")
with torch.no_grad():
    for batch in test_loader:
        pixel_values = batch["pixel_values"].to(device)
        labels = batch["labels"].to(device)
        
        outputs = model(pixel_values=pixel_values)
        logits = outputs.logits
        preds = logits.argmax(-1)
        
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

test_acc = accuracy_score(all_labels, all_preds)
print(f"\n====================================")
print(f"True Test Accuracy: {test_acc:.4f} ({(test_acc*100):.2f}%)")
print(f"====================================\n")

print("Classification Report:")
print(classification_report(all_labels, all_preds, target_names=test_ds.classes))

# -----------------------------
# CONFUSION MATRIX
# -----------------------------
print("\nGenerating Confusion Matrix...")
cm = confusion_matrix(all_labels, all_preds)

plt.figure(figsize=(12, 10))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=test_ds.classes, yticklabels=test_ds.classes)

plt.xlabel("Predicted Labels")
plt.ylabel("True Labels")
plt.title("Test Confusion Matrix (Trained Model)")
plt.tight_layout()

cm_filename = "vit_test_confusion_matrix.png"
plt.savefig(cm_filename)
plt.close()

print(f"Confusion matrix successfully saved as '{cm_filename}'")
