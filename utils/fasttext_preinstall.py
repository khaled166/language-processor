import os
import urllib.request

class FastTextModelManager:
    def __init__(self, model_path, model_url):
        """
        Initialize the FastTextModelManager with the model path and URL.
        
        Parameters:
            model_path (str): The local path where the FastText model should be saved.
            model_url (str): The URL to download the FastText model from if not found locally.
        """
        self.model_path = model_path
        self.model_url = model_url

    def check_and_download_model(self):
        """
        Check if the FastText model exists locally, and download it if not.
        """
        if not os.path.exists(self.model_path):
            print("Model not found. Downloading now...")
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            # Download the model
            urllib.request.urlretrieve(self.model_url, self.model_path)
            print(f"Model downloaded and saved at {self.model_path}")
        else:
            print("Model already exists.")

# Example usage:
# model_manager = FastTextModelManager(r"models\fast_api_model\lid.176.bin", "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin")
# model_manager.check_and_download_model()
