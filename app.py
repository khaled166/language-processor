import os
import urllib.request

# Import necessary packages for FastAPI, data handling, and the language processing module
from fastapi import FastAPI, UploadFile, File, Form  # For building the API
from pydantic import BaseModel  # For defining data models
import asyncio  # For asynchronous operations
import time  # For measuring execution time
from utils.fasttext_preinstall import check_and_download_model  # Function to ensure the model is available
from utils.language_processor import LanguageProcessor  # Custom module for language processing
import uvicorn  # For running the FastAPI app

# Path to the FastText model
model_path = r"models\fast_api_model\lid.176.bin"
# URL of the FastText model
model_url = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"

# Ensure the FastText model is available before the application starts
check_and_download_model(model_path, model_url)  # Ensure the model is downloaded

# Initialize FastAPI app
app = FastAPI()

# Initialize LanguageProcessor instance with paths to data and models
data_path = r"data\cleaned data\cleaned_data.xlsx"  # Path to the initial data file
translation_model_name = "Helsinki-NLP/opus-mt-mul-en"  # Name of the translation model from Hugging Face
processor = LanguageProcessor(data_path, model_path, translation_model_name)

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
    loop = asyncio.get_event_loop()  # Get the event loop for asynchronous tasks
    start_time = time.time()  # Start time measurement
    language, accuracy = await loop.run_in_executor(None, processor.detect_language_and_accuracy, text)  # Execute detection
    end_time = time.time()  # End time measurement
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
    loop = asyncio.get_event_loop()  # Get the event loop for asynchronous tasks
    start_time = time.time()  # Start time measurement
    translation = await loop.run_in_executor(None, processor.translate_text, text)  # Execute translation
    end_time = time.time()  # End time measurement
    time_spent = round((end_time - start_time) * 1000, 2)  # Calculate and round time spent in milliseconds to 2 decimal places
    return TranslationResponse(translation=translation, time_spent=time_spent)

@app.post("/process_and_get_data/")
async def process_and_get_data(file: UploadFile = File(...)):
    """
    Endpoint to upload, process the data file, and return processed data.

    Parameters:
        file (UploadFile): The uploaded file.

    Returns:
        list: Processed data as a list of dictionaries.
    """
    try:
        # Save the uploaded file
        file_location = f"uploaded_{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        # Initialize a new LanguageProcessor with the new file
        processor = LanguageProcessor(file_location, model_path, translation_model_name)
        
        # Load the data from the file
        processor._load_data()
        
        # Ensure only the first column is used, no matter the header name
        first_column_name = processor.df.columns[0]
        processor.df = processor.df[[first_column_name]]
        processor.df.columns = ['News_Title']  # Rename for consistency in processing

        # Convert all values in 'News_Title' to strings and handle NaN values
        processor.df['News_Title'] = processor.df['News_Title'].astype(str)


        # Process the data (detect language and translate)
        processor.process_data()

        # Prepare the final DataFrame with specific columns
        processed_df = processor.df[['News_Title', 'Detected_Language', 'Accuracy', 'English Translation']]
        
        # Convert the DataFrame to a list of dictionaries and return it
        return processed_df.to_dict(orient='records')

    except Exception as e:
        # Log the error for debugging
        print(f"Error processing the data: {e}")
        return {"error": "Internal server error. Please try again later."}

if __name__ == "__main__":
    # Run the FastAPI app using uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


