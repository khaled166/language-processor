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
│ ├── cleaned_data/
│ ├── output/
│ └── row_data/
├── models/
│ └── fast_api_model/
│ └── lid.176.bin
├── notebooks/
  └── language_processor_notebook.ipynb
├── utils/
│ ├── fasttext_model_manager.py
│ └── language_processor.py
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

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/khaled166/language-processor.git
    
    cd https://github.com/khaled166/language-processor.git
    ```
2. **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the application:**

    ```bash
    uvicorn app:app --reload
    ```
    The application will start and can be accessed at `http://127.0.0.1:8000`.

## Usage

- **Language Detection**: Send a POST request to `/detect_language` with a text field to detect its language and accuracy.
- **Translation**: Send a POST request to `/translate` with a text field to translate it to English.
- **Process and Get Data**: Upload an Excel file to `/process_and_get_data/` to process and retrieve the data.


## Notes:

  - Due to the large size of the FastText model, the models folder is initially empty. Instead, the fasttext_preinstall.py script is integrated with the application to automatically download the FastText model when needed, ensuring it's available in the specified path before use.
  
  - The application processes only the first row of the uploaded Excel files, regardless of the header's name; this is mapped internally but first row should be a header.

  - Ensure that the input data is clean and substantial; corrupted data, very short text entries, or blank fields may lead to nonsensical or inaccurate results from the models.

  - If the command uvicorn app:app --reload doesn’t work as expected, try using python -m uvicorn app:app --reload instead. This issue may arise if Uvicorn is installed only within a virtual environment and not globally.
