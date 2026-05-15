import easyocr
from PIL import Image
import numpy as np

# This loads the EasyOCR model — happens once when app starts
# First time it runs, it downloads the model (~100MB) automatically
reader = easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(image_file):
    """
    Takes an uploaded image file from Streamlit,
    runs OCR on it, and returns raw text as a string.
    """
    # Open image and convert to RGB (ensures compatibility)
    image = Image.open(image_file).convert('RGB')
    
    # EasyOCR needs a numpy array
    image_np = np.array(image)
    
    # Returns list of [bounding_box, text, confidence_score]
    results = reader.readtext(image_np)
    
    # We only need the text part, joined line by line
    raw_text = "\n".join([result[1] for result in results])
    
    return raw_text