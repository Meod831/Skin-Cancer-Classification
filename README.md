# Skin Cancer Classification (SCC) App

## Project Description

This PyQt-based GUI application allows users to upload images and classify skin lesions using a custom EfficientNet model. It also keeps records of the classifications.

## Project Structure

```
app/
├── main.py
├── requirements.txt
├── README.md
├── configs/
│   └── config.py
├── data/
│   └── records.csv
├── models/
│   └── final_efficientnet.pt
└── utils/
    ├── model_manager.py
    ├── history_manager.py
    └── image_processor.py
```

## Setup and Installation

1. **Clone the repository.**
2. **Install dependencies:**  
   Run:
    ```
    pip install -r requirements.txt
    ```
3. **Model and Data**
   - Put the `.pt` model in the `models/` directory.
   - The CSV records will be stored in the `data/` directory.
4. **Images:**
   - Images for application including GIFS, icons, reference images are in the `images/` directory.

## Usage

You have two options to run the application:

### Option 1: From the Command Line
1. Open your terminal.
2. Navigate to the project directory.
3. Execute the following command:
```
  python main.py
```

### Option 2: From IDE
1. Open the directory in IDE.
2. Run main.py

## Guidelines

- All configuration paths are stored in `configs/config.py`.
- The utilities in the `utils/` directory handle model operations, history management, and image processing.


## Authors:
1. Rabib Ayan​
2. Jerry Li​
3. Xu Mengyang​
4. Mark O’Donnell​
5. Ashifur Rahman​
6. Emily Ye

## Get Started
Dropbox Links and Instructions

Windows: 
https://www.dropbox.com/scl/fi/5tl4lv3qyq6ho9m1n9pho/SCC_App_Windows.exe?rlkey=065mmu3oqt6oop8txao00n6u3&st=lp9yvzin&dl=0

Download app with link,
Double-click to open app,
 
MacOS:
https://www.dropbox.com/scl/fi/lyrc413x66bydzoc3e0u8/SCC_App_MacOS.zip?rlkey=a8k2yb82tl3clqd49cjil1664&st=01l866b4&dl=0

Download app with link,
Prior to opening app, run following command in Terminal,
xattr -cr /path/to/app/SCC_App.app

Double-click to open app,

MacOS requires additional steps because we do not have a developer account which requires a subscription
