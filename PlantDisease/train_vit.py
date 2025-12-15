import os
import torch
from torch.utils.data import Dataset
from torchvision import datasets, transforms
from transformers import ViTForImageClassification, ViTImageProcessor
from transformers import TrainingArguments, Trainer
import evaluate
from PIL import Image

os.environ["WANDB_DISABLED"] = "true"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# -----------------------------
# PATHS
# -----------------------------
train_dir = "/content/PlantDisease/data/train"
val_dir = "/content/PlantDisease/data/val"
test_dir = "/content/PlantDisease/data/test"

output_dir = "/content/vit-plant-disease"

# -----------------------------
# NO TRANSFORMS HERE!
# -----------------------------
train_ds = datasets.ImageFolder(train_dir)
val_ds = datasets.ImageFolder(val_dir)
test_ds = datasets.ImageFolder(test_dir)

num_labels = len(train_ds.classes)
print("Number of classes:", num_labels)

# -----------------------------
# IMAGE PROCESSOR
# -----------------------------
processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")

# -----------------------------
# FIXED CUSTOM DATASET + AUGMENTATION
# -----------------------------
augment = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(20),
    transforms.ColorJitter(brightness=0.3, contrast=0.3),
])

class ViTDataset(Dataset):
    def __init__(self, dataset, processor, is_train=False):
        self.dataset = dataset
        self.processor = processor
        self.is_train = is_train

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        img, label = self.dataset[idx]

        if self.is_train:
            img = augment(img)

        encoded = self.processor(img, return_tensors="pt")
        encoded = {k: v.squeeze(0) for k, v in encoded.items()}
        encoded["labels"] = torch.tensor(label)

        return encoded

train_dataset = ViTDataset(train_ds, processor, is_train=True)
val_dataset = ViTDataset(val_ds, processor, is_train=False)
test_dataset = ViTDataset(test_ds, processor, is_train=False)

# -----------------------------
# MODEL
# -----------------------------
model = ViTForImageClassification.from_pretrained(
    "google/vit-base-patch16-224",
    num_labels=num_labels,
    ignore_mismatched_sizes=True
)

model.config.id2label = {i: c for i, c in enumerate(train_ds.classes)}
model.config.label2id = {c: i for i, c in enumerate(train_ds.classes)}

model.to(device)

# -----------------------------
# IMPROVED TRAINING CONFIG
# -----------------------------
training_args = TrainingArguments(
    output_dir=output_dir,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    save_total_limit=3,
    learning_rate=3e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=15,        # ⬅️ Increased for accuracy
    weight_decay=0.05,
    logging_steps=50,
    load_best_model_at_end=True,
    optim="adamw_torch",
)

# -----------------------------
# METRICS
# -----------------------------
accuracy = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = logits.argmax(-1)
    return accuracy.compute(predictions=preds, references=labels)

# -----------------------------
# TRAINER
# -----------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics
)

# -----------------------------
# TRAIN
# -----------------------------
print("Training started...")
trainer.train()

# -----------------------------
# SAVE MODEL + PROCESSOR
# -----------------------------
trainer.save_model("/content/drive/MyDrive/vit-plant-disease-final")
processor.save_pretrained("/content/drive/MyDrive/vit-plant-disease-final")

print("Training complete!")
