import pandas as pd  # For data manipulation and analysis
import fasttext  # For language detection
from transformers import MarianMTModel, MarianTokenizer  # For translation model and tokenizer
import swifter  # For efficient parallel processing of pandas DataFrames
import warnings  # To manage warnings

# Ignore all warnings
warnings.filterwarnings('ignore')

class LanguageProcessor:
    """
    A class to process language data, including language detection and translation.
    
    Attributes:
        data_path (str): The path to the Excel file containing the data.
        model_loc (str): The path to the FastText language detection model.
        translation_model_name (str): The name of the translation model to use.
        df (pd.DataFrame): The DataFrame containing the data.
        language_detection_model (fasttext.FastText._FastText): The loaded FastText language detection model.
        translation_model (MarianMTModel): The loaded translation model.
        tokenizer (MarianTokenizer): The tokenizer associated with the translation model.
    """
    
    def __init__(self, data_path, model_loc, translation_model_name):
        """
        Initialize the LanguageProcessor with paths and model names.
        
        Parameters:
            data_path (str): Path to the Excel file with the data.
            model_loc (str): Path to the FastText language detection model.
            translation_model_name (str): Name of the translation model from Hugging Face.
        """
        self.data_path = data_path
        self.model_loc = model_loc
        self.translation_model_name = translation_model_name
        self.df = None
        self.language_detection_model = None
        self.translation_model = None
        self.tokenizer = None
        self._load_models()  # Load models at initialization

    def _load_data(self):
        """
        Load data from the specified Excel file into a pandas DataFrame.
        """
        self.df = pd.read_excel(self.data_path)
        # Ensure only the first column is used, no matter the header name
        first_column_name = self.df.columns[0]
        self.df = self.df[[first_column_name]]
        self.df.columns = ['News_Title']  # Rename for consistency in processing

    def _load_models(self):
        """
        Load the language detection and translation models.
        """
        # Load the FastText language detection model
        self.language_detection_model = fasttext.load_model(self.model_loc)
        # Load the MarianMT translation model and tokenizer
        self.tokenizer = MarianTokenizer.from_pretrained(self.translation_model_name)
        self.translation_model = MarianMTModel.from_pretrained(self.translation_model_name)
        
    def detect_language_and_accuracy(self, text):
        """
        Detect the language of a given text and provide the accuracy of the detection.
        
        Parameters:
            text (str): The text to analyze for language detection.
        
        Returns:
            tuple: Detected language and accuracy of the detection.
        """
        # Predict the language of the text
        model_predict = self.language_detection_model.predict(text)
        # Extract the predicted language
        language = model_predict[0][0].split("__")[2]
        # Extract and format the accuracy value
        accuracy_value = model_predict[1][0] * 100
        if accuracy_value >= 100:
            accuracy = f"{accuracy_value:.0f}%"
        else:
            accuracy = f"{accuracy_value:.2f}%"
        # Return the detected language and accuracy
        return language, accuracy

    def translate_text(self, text):
        """
        Translate the given text to English using the translation model.
        
        Parameters:
            text (str): The text to translate.
        
        Returns:
            str: The translated text.
        """
        # Tokenize the text for the translation model
        tokens = self.tokenizer(text, return_tensors="pt", truncation=True, padding="longest")
        # Generate the translation
        translation = self.translation_model.generate(**tokens)
        # Decode the translated text
        translated_text = self.tokenizer.decode(translation[0], skip_special_tokens=True)
        return translated_text

    def process_data(self):
        """
        Process the DataFrame to detect language and translate text for the 'News_Title' column.
        """
        # Check if data is loaded
        if self.df is None:
            raise ValueError("Data not loaded. Please call _load_data() first.")

        # Apply the language detection function to the 'News_Title' column using swifter for parallel processing
        self.df['Detected_Language'], self.df['Accuracy'] = zip(*self.df['News_Title'].swifter.apply(self.detect_language_and_accuracy))
        # Apply the translation function to the 'News_Title' column using swifter for parallel processing
        self.df["English Translation"] = self.df["News_Title"].swifter.apply(lambda x: self.translate_text(x))

    def get_dataframe(self):
        """
        Get the processed DataFrame with detected languages and translations.
        
        Returns:
            pd.DataFrame: The processed DataFrame with the original text, detected language, accuracy, and English translation.
        """
        # Check if data is processed
        if 'Detected_Language' not in self.df.columns or 'English Translation' not in self.df.columns:
            raise ValueError("Data not processed. Please call process_data() first.")
        
        return self.df[['News_Title', 'Detected_Language', 'Accuracy', 'English Translation']]

# Example usage:
# data_path = 'path_to_your_data.xlsx'
# model_loc = 'path_to_your_fasttext_model.bin'
# translation_model_name = 'Helsinki-NLP/opus-mt-mul-en'
# processor = LanguageProcessor(data_path, model_loc, translation_model_name)
# processor._load_data()  # Load the data
# processor.process_data()  # Process the data
# processed_df = processor.get_dataframe()  # Get the processed data
