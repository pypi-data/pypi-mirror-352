import torch
import tiktoken

tokenizer = tiktoken.get_encoding("gpt2")

class Converter: 
    def __init__(self):
        print("Converter Initialised\n")

    def text_to_token_ids(self, text, tokenizer):
        """Convert text to token IDs with batch dimension."""
        encoded = tokenizer.encode(text, allowed_special={'<|endoftext|>'})
        return torch.tensor(encoded).unsqueeze(0)  # Add batch dimension

    def token_ids_to_text(self, token_ids, tokenizer):
        """Convert token IDs back to text."""
        flat = token_ids.squeeze(0)  # Remove batch dimension
        return tokenizer.decode(flat.tolist())