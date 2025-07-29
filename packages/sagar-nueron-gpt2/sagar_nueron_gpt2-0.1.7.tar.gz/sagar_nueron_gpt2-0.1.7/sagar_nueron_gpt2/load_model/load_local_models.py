from sagar_nueron_gpt2.model_configuration.gpt_model import GPTModel
import torch

class LoadWeightsAndPrepareModel: 
    def __init__(self):
        print("Loading and preparing model")

    def prepare_model(self,MODELCONFIG,path):
        model =  GPTModel(MODELCONFIG)
        checkpoint = torch.load(path)
        #model = GPTMomodeldel(GPT_CONFIG_124M)
        model.load_state_dict(checkpoint["model_state_dict"])
        #optimizer = torch.optim.AdamW(model.parameters(), lr=5e-4, weight_decay=0.1)
        #optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        model.train()

        return model

