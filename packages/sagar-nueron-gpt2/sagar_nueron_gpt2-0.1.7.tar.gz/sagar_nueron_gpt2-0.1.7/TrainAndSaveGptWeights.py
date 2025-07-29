import torch
import torch.nn as nn
import tiktoken
import os
import time

from sagar_nueron_gpt2.processing.data_loader_train_val import DataProcessor_TrainValLoader
from sagar_nueron_gpt2.processing.loss_calculate import CalculatLoss
from sagar_nueron_gpt2.model_configuration.gpt_model import GPTModel
from sagar_nueron_gpt2.processing.Text2TokenViceVersa import Converter

########################################## INITIALISATION ARENA #####################

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else
                      "mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using {device} device.")

# Ensure reproducibility for data loader shuffling
torch.manual_seed(123)

# Initialize loss calculator, tokenizer, and converter
calculation = CalculatLoss()
tokenizer = tiktoken.get_encoding("gpt2")
converter = Converter()

########################################## TRAINING ARENA #####################

class EvaluateTrainModel:
    def evaluate_model(self, model, train_loader, val_loader, device, eval_iter):
        """Evaluate the model on training and validation data."""
        model.eval()
        with torch.no_grad():
            train_loss = calculation.calc_loss_loader(
                train_loader, model, device, num_batches=eval_iter
            )
            val_loss = calculation.calc_loss_loader(
                val_loader, model, device, num_batches=eval_iter
            )
        model.train()
        return train_loss, val_loss

    def generate_text_simple(self, model, idx, max_new_tokens, context_size, temperature=1.0):
        """Generate text by sampling from the model."""
        for _ in range(max_new_tokens):
            # Crop context if it exceeds the supported size
            idx_cond = idx[:, -context_size:]
            with torch.no_grad():
                logits = model(idx_cond)  # Shape: (batch, n_tokens, vocab_size)
            # Focus on the last time step
            logits = logits[:, -1, :] / temperature  # Shape: (batch, vocab_size)
            # Apply softmax to get probabilities
            probas = torch.softmax(logits, dim=-1)  # Shape: (batch, vocab_size)
            # Sample the next token
            idx_next = torch.multinomial(probas, num_samples=1)  # Shape: (batch, 1)
            # Append to the sequence
            idx = torch.cat((idx, idx_next), dim=1)  # Shape: (batch, n_tokens+1)
        return idx

    def generate_and_print_sample(self, model, tokenizer, device, start_context):
        """Generate and print a sample text from the model."""
        model.eval()
        context_size = model.pos_emb.weight.shape[0]
        encoded = converter.text_to_token_ids(start_context, tokenizer).to(device)
        with torch.no_grad():
            token_ids = self.generate_text_simple(
                model=model, idx=encoded,
                max_new_tokens=50, context_size=context_size, temperature=0.7
            )
        decoded_text = converter.token_ids_to_text(token_ids, tokenizer)
        print(decoded_text.replace("\n", " "))  # Compact print format
        model.train()

    def saving_weights_of_model_optimizer(self, model, optimizer, epoch,folder_path):
        """Save model and optimizer weights."""
        os.makedirs(f"{folder_path}/weghts", exist_ok=True)
        torch.save({
            "model_state_dict": model.state_dict(),
        }, f"{folder_path}/weghts/model_epoch_{epoch}.pth")
        print(f"\n\nModel weights saved for epoch {epoch}")

        

    def train_gpt(self, model, train_loader, val_loader, optimizer, device,
                  num_epochs, eval_freq, eval_iter, start_context, tokenizer, path_to_save_model_weights):
        """Train the model and evaluate periodically."""
        train_losses, val_losses, track_tokens_seen = [], [], []
        tokens_seen, global_step = 0, -1
        

        for epoch in range(num_epochs):
            model.train()
            for input_batch, target_batch in train_loader:
                optimizer.zero_grad()
                loss = calculation.calc_loss_batch(
                    input_batch, target_batch, model, device
                )
                loss.backward()
                optimizer.step()
                tokens_seen += input_batch.numel()
                global_step += 1

                if global_step % eval_freq == 0:
                    train_loss, val_loss = self.evaluate_model(
                        model, train_loader, val_loader, device, eval_iter
                    )
                    train_losses.append(train_loss)
                    val_losses.append(val_loss)
                    track_tokens_seen.append(tokens_seen)

                    print(f"Ep {epoch+1} (Step {global_step:06d}): "
                          f"Train loss {train_loss:.3f}, Val loss {val_loss:.3f}")

            self.generate_and_print_sample(model, tokenizer, device, start_context)

            self.saving_weights_of_model_optimizer(model, optimizer, epoch,folder_path=path_to_save_model_weights)
        return train_losses, val_losses, track_tokens_seen, model


def get_int_input(prompt, default=None):
    """Helper function to get integer input with error handling."""
    while True:
        try:
            user_input = input(prompt)
            return int(user_input) if user_input.strip() else default
        except ValueError:
            print("Please enter a valid integer.")



def print_model_size_in_MB(model):
    total_params = sum(p.numel() for p in model.parameters())
    total_size_MB = (total_params * 4) / (1024 ** 2)  # 4 bytes per param (float32)
    print(f"Model size: {total_size_MB:.2f} MB")
    return total_size_MB


class Execute: 
    def __init__(self):
        print("Now you are about to execute the training\n")
    
    def execute(self):
        start_time = time.time()

    # Model configuration
        context_length = get_int_input("Context Length or Press ENTER for DEFAULT 256: ", 256)
        embedding_dimension_of_each_token = get_int_input("Embedding Dimension of Each Token or Press ENTER for DEFAULT 768: ", 768)

        nheads = 0
        while nheads == 0 or embedding_dimension_of_each_token % nheads != 0:
            nheads = get_int_input(f"The number of heads must divide {embedding_dimension_of_each_token}: ", None)
            if embedding_dimension_of_each_token % nheads == 0 and (embedding_dimension_of_each_token // nheads) < 64:
                print(f"Each head will have dimension {embedding_dimension_of_each_token // nheads}, which is less than 64.\nPress 1 to proceed, 2 to re-enter nheads: ")
                choice = get_int_input("", None)
                if choice == 2:
                    continue

        number_of_transformer_layers = get_int_input("Number of Transformer Blocks or Press ENTER for DEFAULT 12: ", 12)

        GPT_CONFIG = {
            "vocab_size": 50257,
            "context_length": context_length,
            "emb_dim": embedding_dimension_of_each_token,
            "n_heads": nheads,
            "n_layers": number_of_transformer_layers,
            "drop_rate": 0.1,
            "qkv_bias": False
        }

        info = f'''    
            "vocab_size": 50257,\n
            "context_length": {context_length},\n
            "emb_dim": {embedding_dimension_of_each_token},\n
            "n_heads": {nheads},\n
            "n_layers": {number_of_transformer_layers},\n
            "drop_rate": 0.1,\n
            "qkv_bias": False,\n
        '''


        # Initialize data loaders
        inp = ""
        while inp == "" or not os.path.exists(inp):
            inp = input("Give the path of the local file: ")
            print("File path: ",inp)

        batch = int(input("Batch Size:  "))
        data_prep = DataProcessor_TrainValLoader(file_path=inp,
                                                 max_length=context_length, 
                                                 stride=context_length,
                                                 train_ratio=0.9,
                                                 batch_size=batch
                                                 )
    
        train_loader, val_loader = data_prep.train_loader, data_prep.val_loader

        if not train_loader or not val_loader:
            raise ValueError("Data loaders could not be created. Check the input file.")

        # Initialize model and optimizer
        torch.manual_seed(123)
        model = GPTModel(GPT_CONFIG)
        model.to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.0004, weight_decay=0.1)

        size = print_model_size_in_MB(model=model)
        info += f"size: "+str(size)+"\n" 

        ch = int(input("Enter 1.OK WITH THE MODEL SIZE  2.I'LL RE-ENTER THE CONFIGURATIONS"))
        if ch==2:
            exit() 



        train = EvaluateTrainModel()

        print("Input text (up to 100 words) to check model performance:")
        start_context = input()
        num_epochs = get_int_input("Number of epochs or Press ENTER for DEFAULT 10: ", 10)
        path  = input("Enter the path to save the model_weights  which is to be passed as input while you make the inference: ") 
        print("This is the path you have given: ",path)

        train_losses, val_losses, tokens_seen, model = train.train_gpt(
            model, train_loader, val_loader, optimizer, device,
            num_epochs=num_epochs, eval_freq=5, eval_iter=5,
            start_context=start_context, tokenizer=tokenizer,path_to_save_model_weights=path
        )
        info += "train_loss: "+str(train_losses)+"\n"+"val_loss: "+str(val_losses)+"\n"+"Weight save path:  "+str(path)+"\n"

        with open(f'{path}/file.txt', 'w') as f:  
            f.writelines(info)
        

        end_time = time.time()
        execution_time_minutes = (end_time - start_time) / 60
        print(f"Training completed in {execution_time_minutes:.2f} minutes.")
            


if __name__ == "__main__":
    
    start_time = time.time()

    # Model configuration
    context_length = get_int_input("Context Length or Press ENTER for DEFAULT 256: ", 256)
    embedding_dimension_of_each_token = get_int_input("Embedding Dimension of Each Token or Press ENTER for DEFAULT 768: ", 768)

    nheads = 0
    while nheads == 0 or embedding_dimension_of_each_token % nheads != 0:
        nheads = get_int_input(f"The number of heads must divide {embedding_dimension_of_each_token}: ", None)
        if embedding_dimension_of_each_token % nheads == 0 and (embedding_dimension_of_each_token // nheads) < 64:
            print(f"Each head will have dimension {embedding_dimension_of_each_token // nheads}, which is less than 64.\nPress 1 to proceed, 2 to re-enter nheads: ")
            choice = get_int_input("", None)
            if choice == 2:
                continue

    number_of_transformer_layers = get_int_input("Number of Transformer Blocks or Press ENTER for DEFAULT 12: ", 12)

    GPT_CONFIG = {
        "vocab_size": 50257,
        "context_length": context_length,
        "emb_dim": embedding_dimension_of_each_token,
        "n_heads": nheads,
        "n_layers": number_of_transformer_layers,
        "drop_rate": 0.1,
        "qkv_bias": False
    }

    info = f'''    
        "vocab_size": 50257,\n
        "context_length": {context_length},\n
        "emb_dim": {embedding_dimension_of_each_token},\n
        "n_heads": {nheads},\n
        "n_layers": {number_of_transformer_layers},\n
        "drop_rate": 0.1,\n
        "qkv_bias": False,\n
    '''


    # Initialize data loaders
    inp = ""
    while inp == "" or not os.path.exists(inp):
        inp = input("Give the path of the local file: ")
        print("File path: ",inp)

    batch = int(input("Batch Size:  "))
    data_prep = DataProcessor_TrainValLoader(file_path=inp,max_length=context_length, stride=context_length,train_ratio=0.9,batch_size=batch)
    train_loader, val_loader = data_prep.train_loader, data_prep.val_loader

    if not train_loader or not val_loader:
        raise ValueError("Data loaders could not be created. Check the input file.")

    # Initialize model and optimizer
    torch.manual_seed(123)
    model = GPTModel(GPT_CONFIG)
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.0004, weight_decay=0.1)

    size = print_model_size_in_MB(model=model)
    info += f"size: "+str(size)+"\n" 

    ch = int(input("Enter 1.OK WITH THE MODEL SIZE  2.I'LL RE-ENTER THE CONFIGURATIONS"))
    if ch==2:
        exit() 



    train = EvaluateTrainModel()

    print("Input text (up to 100 words) to check model performance:")
    start_context = input()
    num_epochs = get_int_input("Number of epochs or Press ENTER for DEFAULT 10: ", 10)
    path  = input("Enter the path to save the model_weights  which is to be passed as input while you make the inference: ") 
    print("This is the path you have given: ",path)

    train_losses, val_losses, tokens_seen, model = train.train_gpt(
        model, train_loader, val_loader, optimizer, device,
        num_epochs=num_epochs, eval_freq=5, eval_iter=5,
        start_context=start_context, tokenizer=tokenizer,path_to_save_model_weights=path
    )
    info += "train_loss: "+str(train_losses)+"\n"+"val_loss: "+str(val_losses)+"\n"+"Weight save path:  "+str(path)+"\n"

    with open(f'{path}/file.txt', 'w') as f:  
        f.writelines(info)
    

    end_time = time.time()
    execution_time_minutes = (end_time - start_time) / 60
    print(f"Training completed in {execution_time_minutes:.2f} minutes.")