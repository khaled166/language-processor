import os
import urllib.request
from fastapi import FastAPI, UploadFile, File, Form, HTTPException  # Import necessary FastAPI modules
from pydantic import BaseModel  # Import BaseModel for structured data models
import asyncio  # Import asyncio for asynchronous operations
import time  # Import time for measuring execution time
from utils.fasttext_preinstall import FastTextModelManager  # Import the FastTextModelManager class
from utils.language_processor import LanguageProcessor  # Import the LanguageProcessor class
from utils.text_validation import TextValidator  # Import the TextValidator class
import uvicorn  # Import uvicorn for running the FastAPI app

# Initialize FastTextModelManager to manage the FastText model
model_manager = FastTextModelManager(
    model_path=r"models\fast_api_model\lid.176.bin",  # Specify the path to the FastText model
    model_url="https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"  # URL to download the FastText model
)

# Ensure the FastText model is available before starting the application
model_manager.check_and_download_model()

# Initialize the FastAPI app
app = FastAPI()

# Define paths and models for language processing
data_path = r"data\cleaned data\cleaned_data.xlsx"  # Path to the initial data file
translation_model_name = "Helsinki-NLP/opus-mt-mul-en"  # Translation model from Hugging Face

# Initialize LanguageProcessor and TextValidator instances
processor = LanguageProcessor(data_path, model_manager.model_path, translation_model_name)  # For processing language tasks
validator = TextValidator()  # For validating text input

# Define Pydantic models for structured API responses
class DetectionResponse(BaseModel):
    language: str  # Detected language
    accuracy: str  # Accuracy of the detection
    time_spent: float  # Time taken for the detection process

class TranslationResponse(BaseModel):
    translation: str  # Translated text
    time_spent: float  # Time taken for the translation process

# Define the language detection endpoint
@app.post("/detect_language", response_model=DetectionResponse)
async def detect_language(text: str = Form(...)):
    """
    Detect the language of the provided text.
    
    Parameters:
        text (str): The text to be analyzed for language detection.
    
    Returns:
        DetectionResponse: The detected language, accuracy, and time spent.
    """
    # Validate word lengths and sentence length
    word_valid, word_msg = validator.validate_word_lengths(text)
    sentence_valid, sentence_msg = validator.validate_sentence_length(text)
    if not word_valid or not sentence_valid:
        # Raise an HTTPException if validation fails
        raise HTTPException(status_code=400, detail=word_msg if not word_valid else sentence_msg)

    # Perform language detection asynchronously
    loop = asyncio.get_event_loop()
    start_time = time.time()  # Start time measurement
    language, accuracy = await loop.run_in_executor(None, processor.detect_language_and_accuracy, text)
    end_time = time.time()  # End time measurement
    time_spent = round((end_time - start_time) * 1000, 2)  # Calculate time spent in milliseconds
    
    return DetectionResponse(language=language, accuracy=accuracy, time_spent=time_spent)

# Define the translation endpoint
@app.post("/translate", response_model=TranslationResponse)
async def translate_text(text: str = Form(...)):
    """
    Translate the provided text to English.
    
    Parameters:
        text (str): The text to be translated.
    
    Returns:
        TranslationResponse: The translated text and time spent.
    """
    # Validate word lengths and sentence length
    word_valid, word_msg = validator.validate_word_lengths(text)
    sentence_valid, sentence_msg = validator.validate_sentence_length(text)
    if not word_valid or not sentence_valid:
        # Raise an HTTPException if validation fails
        raise HTTPException(status_code=400, detail=word_msg if not word_valid else sentence_msg)

    # Perform translation asynchronously
    loop = asyncio.get_event_loop()
    start_time = time.time()  # Start time measurement
    translation = await loop.run_in_executor(None, processor.translate_text, text)
    end_time = time.time()  # End time measurement
    time_spent = round((end_time - start_time) * 1000, 2)  # Calculate time spent in milliseconds
    
    return TranslationResponse(translation=translation, time_spent=time_spent)

# Define the endpoint to process and get data from an uploaded file
@app.post("/process_and_get_data/")
async def process_and_get_data(file: UploadFile = File(...)):
    """
    Upload, process the data file, and return processed data.
    
    Parameters:
        file (UploadFile): The uploaded file.
    
    Returns:
        list: Processed data as a list of dictionaries.
    """
    try:
        # Save the uploaded file locally
        file_location = f"uploaded_{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        # Initialize a new LanguageProcessor instance with the new file
        processor = LanguageProcessor(file_location, model_manager.model_path, translation_model_name)
        processor._load_data()  # Load data from the file

        # Ensure only the first column is used, regardless of the header name
        first_column_name = processor.df.columns[0]
        processor.df = processor.df[[first_column_name]]
        processor.df.columns = ['News_Title']  # Rename for consistency

        # Drop any rows where 'News_Title' is NaN or empty
        processor.df.dropna(subset=['News_Title'], inplace=True)
        processor.df = processor.df[processor.df['News_Title'].str.strip() != '']

        # Convert all values in 'News_Title' to strings
        processor.df['News_Title'] = processor.df['News_Title'].astype(str)

        # Initialize lists to store results and errors
        processed_results = []
        errors = []

        # Validate each row in 'News_Title' for word lengths and sentence length
        for index, text in enumerate(processor.df['News_Title']):
            try:
                word_valid, word_msg = validator.validate_word_lengths(text)
                sentence_valid, sentence_msg = validator.validate_sentence_length(text)
                
                if not word_valid or not sentence_valid:
                    # Collect the error with the specific row index
                    errors.append({
                        "row": index + 1,
                        "text": text,
                        "error": word_msg if not word_valid else sentence_msg
                    })
                    continue  # Skip to the next row without processing further

                # If valid, process the language detection and translation
                language, accuracy = processor.detect_language_and_accuracy(text)
                translation = processor.translate_text(text)
                
                processed_results.append({
                    "row": index + 1,
                    "News_Title": text,
                    "Detected_Language": language,
                    "Accuracy": accuracy,
                    "English_Translation": translation
                })

            except Exception as e:
                # If any unexpected error occurs during processing, log it and move to the next row
                errors.append({
                    "row": index + 1,
                    "text": text,
                    "error": str(e)
                })
                continue

        # Return both processed results and errors
        return {"processed_results": processed_results, "errors": errors}

    except Exception as e:
        # Log and raise an HTTPException if an error occurs during processing
        print(f"Error processing the data: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Main entry point to run the FastAPI app using Uvicorn
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


