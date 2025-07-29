import torch
import math  # Added to use math.exp for floats

class CalculatLoss: 
    def __init__(self):
        print("Calculating the loss\n")

    def calculate_perplexity(self, loss): 
        """Calculate perplexity from loss, handling both tensors and floats."""
        if isinstance(loss, torch.Tensor):
            perplexity = torch.exp(loss).item()  # Convert tensor result to float
        else:
            perplexity = math.exp(loss)  # Use math.exp for float input
        print("Perplexity: ", perplexity)  # Removed \n for cleaner output

    def calc_loss_batch(self, input_batch, target_batch, model, device):
        """Calculate loss for a single batch."""
        input_batch, target_batch = input_batch.to(device), target_batch.to(device)
        logits = model(input_batch)
        loss = torch.nn.functional.cross_entropy(logits.flatten(0, 1), target_batch.flatten())
        # Optionally compute per-batch perplexity here if desired:
        # self.calculate_perplexity(loss)
        return loss

    def calc_loss_loader(self, data_loader, model, device, num_batches=None):
        """Calculate average loss over batches and compute perplexity once."""
        total_loss = 0.
        if len(data_loader) == 0:
            return float("nan")
        elif num_batches is None:
            num_batches = len(data_loader)
        else:
            num_batches = min(num_batches, len(data_loader))
        
        for i, (input_batch, target_batch) in enumerate(data_loader):
            if i < num_batches:
                loss = self.calc_loss_batch(input_batch, target_batch, model, device)
                total_loss += loss.item()
            else:
                break
        
        average_loss = total_loss / num_batches
        self.calculate_perplexity(average_loss)  # Compute perplexity once with average loss
        return average_loss