import torch
from torch import nn
from torchvision import models, transforms
from PIL import Image

CLASSES = [
    "Biodegradable",
    "Dry Recyclable",
    "Hazardous / E-Waste"
]

# Load model
model = models.resnet18(weights=None)

model.fc = nn.Linear(
    model.fc.in_features,
    3
)

model.load_state_dict(
    torch.load(
        "waste_model.pth",
        map_location="cpu"
    )
)

model.eval()

# SAME preprocessing used during training
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def classify_waste(image):

    try:

        img = Image.open(image).convert("RGB")

        img = transform(img)

        img = img.unsqueeze(0)

        with torch.no_grad():

            output = model(img)

            probabilities = torch.softmax(
                output,
                dim=1
            )

            confidence, prediction = torch.max(
                probabilities,
                1
            )

        category = CLASSES[prediction.item()]

        confidence = confidence.item() * 100

        return {
            "category": category,
            "confidence": round(confidence, 2)
        }

    except Exception as e:

        print("ERROR:", e)

        return {
            "category": "Invalid image",
            "confidence": 0
        }
