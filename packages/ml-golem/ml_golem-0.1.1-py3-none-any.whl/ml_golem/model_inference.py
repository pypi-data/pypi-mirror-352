from ml_golem.base_classes.model_io_base import ModelIOBase
import torch.nn as nn
class ModelInference(ModelIOBase):
    def __init__(self,args,subconfig_keys):
        super().__init__(args,subconfig_keys)

        if isinstance(self.model, nn.Module):
            self.device = next(self.model.parameters()).device
            self.model = self.model.to(self.device)
            self.model.eval()

    def __call__(self):

        if self.dataloader is None:
            results = self.make_inference(self.model)
            self.save_results(results, self.model)
        else:
            for input_data in self.dataloader:
                results = self.make_inference(self.model,input_data)
                self.save_results(results,self.model,input_data)

        self.complete_inference()


    def make_inference(self,model,input_data=None):
        if input_data is None:
            output = model()
        else:
            output = model(input_data)
        return output
    
    def save_results(self,output,model,input_data=None):
        model.save_results(output, input_data)

    def complete_inference(self):
        if hasattr(self.model, 'complete_inference'):
            self.model.complete_inference()
