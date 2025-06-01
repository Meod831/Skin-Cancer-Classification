import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

class EfficientNetCustomHead(nn.Module):
    def __init__(self, num_classes):
        super(EfficientNetCustomHead, self).__init__()
        self.base_model = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT)
        in_features = self.base_model.classifier[1].in_features
        self.base_model.classifier = nn.Sequential(
            nn.Dropout(p=0.2),
            nn.Linear(in_features, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.2),
            nn.Linear(1024, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Linear(512, num_classes)
        )
        
    def forward(self, x):
        return self.base_model(x)

class ModelManager:
    def __init__(self, model_path, num_classes=7, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.num_classes = num_classes
        self.model = EfficientNetCustomHead(num_classes=self.num_classes)
        self.load_model(model_path)
        self.model.to(self.device)
        self.model.eval()
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ])
        self.idx2label = {
            0: "Actinic keratoses",
            1: "Basal cell carcinoma",
            2: "Benign keratosis",
            3: "Dermatofibroma",
            4: "Melanoma",
            5: "Melanocytic nevi",
            6: "Vascular lesions"
        }
        
    def load_model(self, model_path):
        if os.path.exists(model_path):
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
        else:
            raise FileNotFoundError(f"Model file not found at: {model_path}")
    
    def classify_image(self, image_path):
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            print(f"Error: {e}")
            return "Error", 0.0
        image_tensor = self.transform(image)
        image_tensor = image_tensor.unsqueeze(0).to(self.device)
        with torch.no_grad():
            output = self.model(image_tensor)
            probs = F.softmax(output, dim=1)
            confidence, predicted_idx = torch.max(probs, dim=1)
            predicted_idx = predicted_idx.item()
            confidence = confidence.item() * 100.0
        prediction = self.idx2label.get(predicted_idx, "Unknown")
        return prediction, confidence
