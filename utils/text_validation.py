# utils/text_validation.py

class TextValidator:
    def __init__(self, min_len=None, max_len=None, min_sentence_length=3, max_sentence_length=5000):
        """
        Initialize the TextValidator with optional constraints.
        
        Parameters:
            min_len (int, optional): The minimum word length. Defaults to the global minimum.
            max_len (int, optional): The maximum word length. Defaults to the global maximum.
            min_sentence_length (int, optional): The minimum allowed sentence length (in words). Defaults to 3.
            max_sentence_length (int, optional): The maximum allowed sentence length (in words). Defaults to 5000.
        """
        self.min_len = min_len or self.get_min_max_word_lengths()[0]
        self.max_len = max_len or self.get_min_max_word_lengths()[1]
        self.min_sentence_length = min_sentence_length
        self.max_sentence_length = max_sentence_length

    def get_min_max_word_lengths(self):
        # Define the global minimum and maximum word lengths
        min_len = 1  # Minimum word length typically seen in languages (e.g., "a" in English)
        max_len = 45 # Longest word length (45 characters in Greek)
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
        Validates the sentence lengths in the text and the total number of words.
        
        Parameters:
            text (str): The text to validate.
        
        Returns:
            tuple: (bool, str) where the first element is whether the validation passed, 
                   and the second element is an error message if it failed.
        """
        # Validate total word count of the text
        total_words = text.split()
        if len(total_words) > 5000:
            return False, "Paragraph exceeds the maximum length of 5000 words."
        
        # Check if any sentence has at least 3 words
        has_min_length_sentence = False
        
        # Validate each sentence length
        for sentence in text.split('.'):
            words = sentence.split()
            
            # Skip empty sentences caused by consecutive periods or trailing periods
            if not words:
                continue
            
            if len(words) > self.max_sentence_length:
                return False, f"Sentences exceeds the maximum length of {self.max_sentence_length} words."
            
            if len(words) >= self.min_sentence_length:
                has_min_length_sentence = True

        # If no sentence has at least 3 words, return an error
        if not has_min_length_sentence:
            return False, f"sentence does not meets the minimum length of {self.min_sentence_length} words."

        return True, "All sentences meet the length criteria."
