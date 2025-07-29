import torch
from torch.utils.data import Dataset, DataLoader
import tiktoken
import os
import urllib.request

class GPTDataset(Dataset):
    def __init__(self, txt, tokenizer, max_length, stride):
        self.input_ids = []
        self.target_ids = []

        # Tokenize the entire text
        token_ids = tokenizer.encode(txt, allowed_special={"<|endoftext|>"})

        # Use a sliding window to chunk the text into overlapping sequences of max_length
        for i in range(0, len(token_ids) - max_length, stride):
            input_chunk = token_ids[i:i + max_length]
            target_chunk = token_ids[i + 1: i + max_length + 1]
            self.input_ids.append(torch.tensor(input_chunk))
            self.target_ids.append(torch.tensor(target_chunk))

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return self.input_ids[idx], self.target_ids[idx]
    
    

def create_dataloader_for_gpt(txt, batch_size=4, max_length=256, stride=128, 
                              shuffle=True, drop_last=True, num_workers=0):
    """Create a DataLoader for GPT training."""
    # Initialize the tokenizer
    tokenizer = tiktoken.get_encoding("gpt2")

    # Create dataset
    dataset = GPTDataset(txt, tokenizer, max_length, stride)

    # Create dataloader
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        drop_last=drop_last,
        num_workers=num_workers
    )

    return dataloader, len(dataset)


#
class LoadDataFromTextSource:

    def __init__(self, file_path, url=None):
        self.file_path = file_path
        self.text_data = self._load_text(url)

    def _load_text(self, url):
        """Load or download text data."""
        try:
            if not os.path.exists(self.file_path):
                if not url:
                    raise ValueError("URL must be provided if file does not exist.")
                print(f"Downloading text from {url} ...")
                with urllib.request.urlopen(url) as response:
                    text_data = response.read().decode('utf-8')
                with open(self.file_path, "w", encoding="utf-8") as file:
                    file.write(text_data)
                print("Download complete and saved to disk.")
            else:
                print(f"File already exists: {self.file_path}")
                with open(self.file_path, "r", encoding="utf-8") as file:
                    text_data = file.read()

            # Validate text data
            if not text_data.strip():
                raise ValueError("Text data is empty or contains only whitespace.")

            # Inspect file info
            print("\nFile Information:")
            print(f" Path: {self.file_path}")
            print(f" File size: {os.path.getsize(self.file_path) / 1024:.2f} KB")
            print(f" Number of characters: {len(text_data):,}")
            print(f" Number of words: {len(text_data.split()):,}")
            print(f" Number of lines: {len(text_data.splitlines()):,}")
            print(f"\nLast 100 characters: {text_data[-100:]}")

            return text_data
        except urllib.error.URLError as e:
            raise ValueError(f"Failed to download file from {url}: {e}")
        except IOError as e:
            raise ValueError(f"Error reading/writing file {self.file_path}: {e}")

class DataProcessor_TrainValLoader:
    def __init__(self, file_path, url=None, train_ratio=0.9, batch_size=2, 
                 max_length=256, stride=256):
        # Validate train_ratio
        #file_path :  it is the path to the file in the local disrectort
        try:
            user_input = input("Enter training data ratio or [ENTER FOR DEFAULT 0.9]: ") or str(train_ratio)
            train_ratio = float(user_input)
            if not 0 < train_ratio < 1:
                raise ValueError("train_ratio must be between 0 and 1")
        except ValueError as e:
            if "must be between" not in str(e):
                print("Invalid input. Using default train_ratio of 0.9")
                train_ratio = 0.9
            else:
                raise ValueError("train_ratio must be between 0 and 1")

        # Load text data
        loader = LoadDataFromTextSource(file_path, url)
        text_data = loader.text_data

        # Calculate split index
        split_idx = int(train_ratio * len(text_data))
        train_data = text_data[:split_idx]
        val_data = text_data[split_idx:]

        # Validate data lengths
        if len(train_data) < max_length:
            raise ValueError(
                f"Not enough tokens for training loader ({len(train_data)} < {max_length}). "
                "Try lowering max_length or increasing train_ratio."
            )
        if len(val_data) < max_length:
            raise ValueError(
                f"Not enough tokens for validation loader ({len(val_data)} < {max_length}). "
                "Try lowering max_length or decreasing train_ratio."
            )

        # Set random seed for reproducibility
        torch.manual_seed(123)

        # Create dataloaders
        train_loader, train_dataset_len = create_dataloader_for_gpt(
            train_data,
            batch_size=batch_size,
            max_length=max_length,
            stride=stride,
            drop_last=True,
            shuffle=True,
            num_workers=0
        )

        val_loader, val_dataset_len = create_dataloader_for_gpt(
            val_data,
            batch_size=batch_size,
            max_length=max_length,
            stride=stride,
            drop_last=False,
            shuffle=False,
            num_workers=0
        )

        print(f"Train loader dataset size: {train_dataset_len} samples")
        print(f"Validation loader dataset size: {val_dataset_len} samples")

        self.train_loader = train_loader
        self.val_loader = val_loader


        #return  train_loader, val_loader


