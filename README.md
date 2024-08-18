# Language Processor API

This repository features a FastAPI-based web service that detects the language of text data and translates it into English using FastText for language detection and Hugging Face's MarianMT model (Helsinki-NLP) for multilingual translation. The application is highly versatile, capable of processing both individual text entries and entire Excel files. It efficiently handles language detection and translation tasks, providing processed data for single text rows or bulk datasets uploaded via Excel files.

## Features

- **Language Detection**: Detects the language of text using FastText.
- **Translation**: Translates text from detected language to English using MarianMT(Helsinki-NLP).
- **API Endpoints**:
  - `/detect_language`: Detects the language of a provided text.
  - `/translate`: Translates the provided text to English.
  - `/process_and_get_data`: Uploads an Excel file, processes it, and returns the processed data.

## Folder Structure

The project is organized as follows:

├── data/  
│   ├── cleaned_data/  
│   ├── output/  
│   └── row_data/  
├── models/  
│   ├── fast_api_model/  
│   └── lid.176.bin  
├── notebooks/  
│   └── language_processor_notebook.ipynb  
├── utils/  
│   ├── fasttext_model_manager.py  
│   └── language_processor.py  
├── .gitignore  
├── app.py  
├── README.md  
└── requirements.txt  

- `data/`: Contains raw and processed data files.
  - `cleaned_data/`: Contains cleaned data ready for processing.
  - `output/`: Processed output data files.
  - `row_data/`: Contains raw, unprocessed data files.
- `models/`: Stores machine learning models.
  - `fast_api_model/`: Contains the FastText language detection model (`lid.176.bin`).
- `notebooks/`: Contains Jupyter notebooks for development and experimentation.
- `utils/`: Contains utility scripts such as:
  - `fasttext_model_manager.py`: Handles downloading and checking the FastText model.
  - `language_processor.py`: Contains the core logic for language detection and translation.
- `app.py`: Main entry point for the FastAPI application.
- `README.md`: This file.
- `requirements.txt`: Lists all the dependencies needed to run the application.

## Models Used

This project leverages two key models for its language processing tasks:

1. **FastText Language Detection Model**:
   - **Model**: `lid.176.bin`
   - **Source**: Facebook's AI Research (FAIR)
   - **Purpose**: The FastText model is used to detect the language of the input text. It is highly efficient and capable of identifying over 170 languages. The model operates by representing text as character n-grams, which enhances its ability to understand morphologically rich languages and handle out-of-vocabulary words.
   - **Usage**: This model is automatically downloaded and saved to the `models/fast_api_model/` directory if not already present, ensuring the application can function without manual model installation.

2. **MarianMT Translation Model**:
   - **Model**: `Helsinki-NLP/opus-mt-mul-en`
   - **Source**: Hugging Face
   - **Purpose**: The MarianMT model is used for translating detected text into English. It supports a wide range of source languages and provides accurate and context-aware translations. The model is part of the Helsinki-NLP project and is pre-trained on a large dataset of multilingual parallel corpora.
   - **Usage**: The MarianMT model and its tokenizer are loaded during the application runtime, facilitating seamless translation services through the API.

## Installation

### Environment Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/khaled166/language-processor.git
    ```

2. **Create a virtual environment:**

    - On Windows:
    
      ```bash
      python -m venv venv
      venv\Scripts\activate
      ```
    
    - On macOS/Linux:
    
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

### Model Download

- The FastText language detection model (`lid.176.bin`) is not included in the repository due to its size. The model is automatically downloaded the first time the application is run. This ensures that the model is available in the `models/fast_api_model/` directory before use. The download occurs when the application checks for the model’s existence and downloads it if not found.

### Running the Application

1. **Run the application:**

    ```bash
    uvicorn app:app --reload
    ```
    The application will start and can be accessed at `http://127.0.0.1:8000`.


## Text Validation

The `TextValidator` class is a utility designed to ensure that input text meets specific criteria regarding word and sentence lengths. This validation process helps maintain the quality and consistency of the text data before it is processed for language detection and translation.

### Features

- **Word Length Validation**:
  - Ensures that each word in the text falls within specified minimum and maximum lengths.
  - Default word length constraints:
    - Minimum: 1 character
    - Maximum: 45 characters (suitable for languages like Greek with longer words).

- **Sentence Length Validation**:
  - Checks that each sentence in the text contains a number of words within the allowed range.
  - Default sentence length constraints:
    - Minimum: 3 words
    - Maximum: 5000 words.

### Example Usage

The `TextValidator` can be used to validate text before it is processed by the language detection and translation models. Here’s how you can use it:

```python
from utils.text_validation import TextValidator

# Initialize the validator with optional constraints
validator = TextValidator(min_len=2, max_len=50, min_sentence_length=5, max_sentence_length=1000)

# Validate word lengths in a text
is_valid, message = validator.validate_word_lengths("This is a test sentence.")
print(message)  # Output: "All words meet the length criteria."

# Validate sentence length in a text
is_valid, message = validator.validate_sentence_length("This is a test sentence.")
print(message)  # Output: "All sentences meet the length criteria."
```

## API Usage

### API Documentation

- **Language Detection**:
  - **Endpoint**: `/detect_language`
  - **Method**: POST
  - **Input**: Form data containing a single text field `text` (e.g., `{"text": "Bonjour tout le monde"}`)
  - **Output**: JSON response with the detected language, accuracy, and time taken.
  - **Example Response**:
    ```json
    {
      "language": "fr",
      "accuracy": "99.67%",
      "time_spent": 12.34
    }
    ```

- **Translation**:
  - **Endpoint**: `/translate`
  - **Method**: POST
  - **Input**: Form data containing a single text field `text` (e.g., `{"text": "Bonjour tout le monde"}`)
  - **Output**: JSON response with the translated text and time taken.
  - **Example Response**:
    ```json
    {
      "translation": "Hello everyone",
      "time_spent": 23.45
    }
    ```

- **Process and Get Data**:
  - **Endpoint**: `/process_and_get_data`
  - **Method**: POST
  - **Input**: Upload an Excel file containing text data. The first row should be a header.
  - **Output**: JSON response with a list of dictionaries containing the original text, detected language, accuracy, and translation.
  - **Example Response**:
    ```json
    [
      {
        "News_Title": "Bonjour tout le monde",
        "Detected_Language": "fr",
        "Accuracy": "99.67%",
        "English Translation": "Hello everyone"
      }
    ]
    ```    

## Notes

- **Model Download**: As noted in the "Model Download" section, the FastText model is automatically downloaded the first time the application runs, ensuring the necessary resources are available without manual intervention.
  
- **Data Handling**: The application processes only the first row of the uploaded Excel files, regardless of the header's name. This row is mapped internally, but ensure that the first row is a header for accurate processing.

- **Input Data Quality**: Ensure that the input data is clean and substantial. Corrupted data, very short text entries, or blank fields may lead to nonsensical or inaccurate results from the models.

- **Alternative Command for Running the App**: If the command `uvicorn app:app --reload` doesn’t work as expected, try using `python -m uvicorn app:app --reload` instead. This issue may arise if Uvicorn is installed only within a virtual environment and not globally.
