import os
import urllib.request

# Path to the FastText model
model_path = r"..\models\fast_api_model\lid.176.bin"
# URL of the FastText model
model_url = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"

def check_and_download_model(model_path, model_url):
    # Check if the model file exists
    if not os.path.exists(model_path):
        print("Model not found. Downloading now...")
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        # Download the model
        urllib.request.urlretrieve(model_url, model_path)
        print(f"Model downloaded and saved at {model_path}")
    else:
        print("Model already exists.")

# Call the function to check and download the model if necessary
#check_and_download_model(model_path, model_url)

# Your application code can go here, after ensuring the model is downloaded
#print("Application ready to run.")



