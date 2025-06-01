import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_PATH = os.path.join(BASE_DIR, "models", "final_efficientnet.pt")
CSV_PATH = os.path.join(BASE_DIR, "data", "records.csv")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
