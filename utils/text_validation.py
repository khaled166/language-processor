# utils/text_validation.py

class TextValidator:
    def __init__(self, min_len=None, max_len=None,min_sentence_length= 3,max_sentence_length=5000):
        """
        Initialize the TextValidator with optional constraints.
        
        Parameters:
            min_len (int, optional): The minimum word length. Defaults to the global minimum.
            max_len (int, optional): The maximum word length. Defaults to the global maximum.
            max_sentence_length (int, optional): The maximum allowed sentence length (in words). Defaults to 5000.
        """
        self.min_len = min_len or self.get_min_max_word_lengths()[0]
        self.max_len = max_len or self.get_min_max_word_lengths()[1]
        self.min_sentence_length = min_sentence_length
        self.max_sentence_length = max_sentence_length

    def get_min_max_word_lengths(self):
        # You need to define how to get these values globally, or hardcode them
        min_len = 1  # Minimum word length typically seen in languages (e.g., "a" in English)
        max_len = 45 # Longest word length ( 45 char length in Greek) 
        return min_len, max_len

    def validate_word_lengths(self, text):
        """
        Validates the word lengths in the text.
        
        Parameters:
            text (str): The text to validate.
        
        Returns:
            tuple: (bool, str) where the first element is whether the validation passed, 
                   and the second element is an error message if it failed.
        """
        for word in text.split():
            if len(word) < self.min_len:
                return False, f"Word '{word}' is shorter than the minimum length of {self.min_len}."
            elif len(word) > self.max_len:
                return False, f"Word '{word}' is longer than the maximum length of {self.max_len}."
        
        return True, "All words meet the length criteria."

    def validate_sentence_length(self, text):
        """
        Validates the sentence lengths in the text.
        
        Parameters:
            text (str): The text to validate.
        
        Returns:
            tuple: (bool, str) where the first element is whether the validation passed, 
                   and the second element is an error message if it failed.
        """
        for sentence in text.split('.'):
            words = sentence.split()
            if len(words) > self.max_sentence_length:
                return False, f"Sentence exceeds the maximum length of {self.max_sentence_length} words."
            elif len(words) < self.min_sentence_length:
                    return False, f"Sentence less than the min length of {self.min_sentence_length} words."
        
        return True, "All sentences meet the length criteria."