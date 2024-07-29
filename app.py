# Import necessary packages for FastAPI, data handling, and the language processing module
from fastapi import FastAPI, UploadFile, File, Form  # For building the API
from pydantic import BaseModel  # For defining data models
import asyncio  # For asynchronous operations
import time  # For measuring execution time
from utils.language_processor import LanguageProcessor  # Custom module for language processing
import uvicorn  # For running the FastAPI app

# Initialize FastAPI app
app = FastAPI()

# Initialize LanguageProcessor instance with paths to data and models
data_path = r"data\cleaned data\cleaned_data.xlsx"  # Path to the initial data file
model_loc = r"models\fast_api_model\lid.176.bin"  # Path to the FastText language detection model
translation_model_name = "Helsinki-NLP/opus-mt-mul-en"  # Name of the translation model from Hugging Face
processor = LanguageProcessor(data_path, model_loc, translation_model_name)

# Define Pydantic models for structured responses
class DetectionResponse(BaseModel):
    language: str  # Detected language
    accuracy: str  # Accuracy of the detection
    time_spent: float  # Time taken for the detection process

class TranslationResponse(BaseModel):
    translation: str  # Translated text
    time_spent: float  # Time taken for the translation process

# Define routes for the FastAPI app

@app.post("/detect_language", response_model=DetectionResponse)
async def detect_language(text: str = Form(...)):
    """
    Endpoint to detect the language of a given text.
    
    Parameters:
        text (str): The text for which to detect the language.
    
    Returns:
        DetectionResponse: The detected language, accuracy, and time taken.
    """
    loop = asyncio.get_event_loop()
    start_time = time.time()  # Start time measurement
    language, accuracy = await loop.run_in_executor(None, processor.detect_language_and_accuracy, text)
    end_time = time.time()  # End time measurement
    time_spent = (end_time - start_time) * 1000  # Calculate time spent in milliseconds
    time_spent = round((end_time - start_time) * 1000, 2)  # Calculate and round time spent in milliseconds to 2 decimal places
    return DetectionResponse(language=language, accuracy=accuracy, time_spent=time_spent)

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(text: str = Form(...)):
    """
    Endpoint to translate a given text to English.
    
    Parameters:
        text (str): The text to translate.
    
    Returns:
        TranslationResponse: The translated text and time taken.
    """
    loop = asyncio.get_event_loop()
    start_time = time.time()  # Start time measurement
    translation = await loop.run_in_executor(None, processor.translate_text, text)
    end_time = time.time()  # End time measurement
    time_spent = (end_time - start_time) * 1000  # Calculate time spent in milliseconds
    time_spent = round((end_time - start_time) * 1000, 2)  # Calculate and round time spent in milliseconds to 2 decimal places
    return TranslationResponse(translation=translation, time_spent=time_spent)

@app.post("/upload_data/")
async def upload_data(file: UploadFile = File(...)):
    """
    Endpoint to upload a new data file and process it.
    
    Parameters:
        file (UploadFile): The uploaded file.
    
    Returns:
        dict: Information about the uploaded file.
    """
    # Save the uploaded file
    file_location = f"uploaded_{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Update the processor with the new file
    processor.data_path = file_location
    processor._load_data()
    processor.process_data()

    return {"info": "file uploaded successfully", "filename": file.filename}

@app.get("/get_processed_data")
async def get_processed_data():
    """
    Endpoint to retrieve the processed data.
    
    Returns:
        list: Processed data as a list of dictionaries.
    """
    df = processor.get_dataframe()
    return df.to_dict(orient='records')

if __name__ == "__main__":
    # Run the FastAPI app using uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
