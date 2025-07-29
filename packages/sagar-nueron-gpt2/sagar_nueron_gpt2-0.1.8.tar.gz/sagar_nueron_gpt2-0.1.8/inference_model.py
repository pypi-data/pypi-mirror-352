import torch 
from sagar_nueron_gpt2.load_model.load_local_models import LoadWeightsAndPrepareModel
from sagar_nueron_gpt2.processing.Text2TokenViceVersa import Converter
import tiktoken

class Inference:
    def generate(self, model, idx, max_new_tokens, context_size, temperature=0.0, top_k=None, eos_id=None):
        """Generate text by sampling from the model."""
        # Use the device of the model's first parameter
        device = next(model.parameters()).device
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -context_size:].to(device)  # Ensure input is on model's device
            with torch.no_grad():
                logits = model(idx_cond)
            logits = logits[:, -1, :]

            # Filter logits with top_k sampling
            if top_k is not None:
                # Keep only top_k values
                top_logits, _ = torch.topk(logits, top_k)
                min_val = top_logits[:, -1]
                logits = torch.where(logits < min_val, torch.tensor(float("-inf")).to(device), logits)

            # Apply temperature scaling
            if temperature > 0.0:
                logits = logits / temperature
                # Apply softmax to get probabilities
                probs = torch.softmax(logits, dim=-1)  # (batch_size, vocab_size)
                # Sample from the distribution
                idx_next = torch.multinomial(probs, num_samples=1)  # (batch_size, 1)
            else:
                # Get idx of the vocab entry with the highest logits value
                idx_next = torch.argmax(logits, dim=-1, keepdim=True)  # (batch_size, 1)

            if idx_next == eos_id:  # Stop generating early if end-of-sequence token is encountered
                break

            # Append sampled index to the running sequence
            idx = torch.cat((idx, idx_next), dim=1)  # (batch_size, num_tokens+1)

        return idx
    


class Inferencing: 
    def __init__(self):
        print("Inference you are in\n")

    def inference(self):
        print("Hey this is to be used carefully so that to prevent loading mistakes.\nThe information will be stored in:\n ****file.txt***** ")
        m = input("Check this and enter properly . Start looking at the Press ENTER: ")
        context_length = int(input("Enter the context lenght:  "))
        embedding_dimension =  int(input("Enter Embedding dimension: "))
        number_of_heads =  int(input("Enter the number of heads:  "))
        number_of_layers =  int(input("Enter the number of transformer Layers: "))



        GPT_CONFIG = {
            "vocab_size": 50257,
            "context_length": context_length,
            "emb_dim": embedding_dimension,
            "n_heads": number_of_heads,
            "n_layers": number_of_layers,
            "drop_rate": 0.1,
            "qkv_bias": False
        }

        tokenizer = tiktoken.get_encoding("gpt2")
        conv = Converter()

        # Load model and optimizer
        model_weight_path = input("Cleanly enter the path to the model weights:  ")
        model = LoadWeightsAndPrepareModel().prepare_model(GPT_CONFIG, model_weight_path )
        model.eval()  # Set model to evaluation mode for inference

        # Determine model device
        device = next(model.parameters()).device

        text = input("Ask GPT: ") or ''' 
        Then no speech is needed; silence will carry the truth. Do not
        spend your energy in talking, but meditate in silence; and do not let the rush
        of the outside world disturb you.
        '''
        mnt = int(input("Enter the number of tokens to be produced: "))
        temp =  float(input("Temperature: "))
        k = int(input("Top K samples : "))
        # Generate token IDs

        token_ids = Inference().generate(
            model=model,
            idx=conv.text_to_token_ids(text=text, tokenizer=tokenizer).to(device),  # Use model's device
            max_new_tokens=mnt,
            context_size=GPT_CONFIG['context_length'],
            temperature=temp,
            top_k=k,
            # Simplified EOS token handling
        )

        # Convert token IDs back to text
        generated_text = conv.token_ids_to_text(token_ids, tokenizer)
        print("\nGenerated Text:")
        print(generated_text.replace("\n", " "))  # Compact print format



if __name__ == "__main__":
    print("Hey this is to be used carefully so that to prevent loading mistakes.\nThe information will be stored in:\n ****file.txt***** ")
    m = input("Check this and enter properly . Start looking at the Press ENTER: ")
    context_length = int(input("Enter the context lenght:  "))
    embedding_dimension =  int(input("Enter Embedding dimension: "))
    number_of_heads =  int(input("Enter the number of heads:  "))
    number_of_layers =  int(input("Enter the number of transformer Layers: "))



    GPT_CONFIG = {
        "vocab_size": 50257,
        "context_length": context_length,
        "emb_dim": embedding_dimension,
        "n_heads": number_of_heads,
        "n_layers": number_of_layers,
        "drop_rate": 0.1,
        "qkv_bias": False
    }

    tokenizer = tiktoken.get_encoding("gpt2")
    conv = Converter()

    # Load model and optimizer
    model_weight_path = input("Cleanly enter the path to the model weights:  ")
    model = LoadWeightsAndPrepareModel().prepare_model(GPT_CONFIG, model_weight_path )
    model.eval()  # Set model to evaluation mode for inference

    # Determine model device
    device = next(model.parameters()).device

    text = input("Ask GPT: ") or ''' 
    Then no speech is needed; silence will carry the truth. Do not
    spend your energy in talking, but meditate in silence; and do not let the rush
    of the outside world disturb you.
    '''
    mnt = int(input("Enter the number of tokens to be produced: "))
    temp =  int(input("Temperature: "))
    k = int(input("Top K samples : "))
        # Generate token IDs

    token_ids = Inference().generate(
            model=model,
            idx=conv.text_to_token_ids(text=text, tokenizer=tokenizer).to(device),  # Use model's device
            max_new_tokens=mnt,
            context_size=GPT_CONFIG['context_length'],
            temperature=temp,
            top_k=k,
            # Simplified EOS token handling
    )

    # Convert token IDs back to text
    generated_text = conv.token_ids_to_text(token_ids, tokenizer)
    print("\nGenerated Text:")
    print(generated_text.replace("\n", " "))  # Compact print format