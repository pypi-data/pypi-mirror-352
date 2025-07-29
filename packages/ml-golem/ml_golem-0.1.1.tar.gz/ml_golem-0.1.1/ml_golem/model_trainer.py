
from accelerate import Accelerator
import torch
from tqdm import tqdm
from torch.utils.tensorboard import SummaryWriter
from ml_golem.base_classes.model_io_base import ModelIOBase,ModelConfigKeywords
from ml_golem.datatypes import TrainingLog


class ModelTrainer(ModelIOBase):
    def __init__(self,args,subconfig_keys):
        super().__init__(args,subconfig_keys)

        self.epochs = self.config[ModelConfigKeywords.EPOCHS.value]
        self.can_display_epoch_progress = self.config.get(ModelConfigKeywords.CAN_DISPLAY_EPOCH_PROGRESS.value, True)
        self.learning_rate = float(self.config[ModelConfigKeywords.LEARNING_RATE.value])
        self.save_every = self.config[ModelConfigKeywords.SAVE_EVERY.value]

        self.loss = self.instantiate_config_based_class(args,
            subconfig_keys=self.subconfig_keys + [ModelConfigKeywords.LOSS.value])
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)

        self.accelerator = Accelerator()
        self.model, self.optimizer, self.loader, self.loss= self.accelerator.prepare(self.model, self.optimizer,self.dataloader,self.loss)
        self.model.train()
        self.device = next(self.model.parameters()).device

        self.writer = SummaryWriter(self.data_io.get_data_path(TrainingLog,data_args ={
            TrainingLog.CONFIG_NAME: self.global_config_name,
        }))

    def __call__(self):
        if self.can_display_epoch_progress:
            epoch_iterator = tqdm(range(self.resume_epoch + 1, self.epochs), desc="Epochs")
        else:
            epoch_iterator = range(self.resume_epoch + 1, self.epochs)
        for epoch in epoch_iterator:
            for input_batch in self.dataloader:
                self.optimizer.zero_grad()
                input_batch = self.match_devices(input_batch)
                output_batch = self.model(input_batch)
                loss_results = self.loss(input_batch,output_batch)
                self.accelerator.backward(loss_results[self.loss.MAIN_LOSS])
                self.optimizer.step()
            
            self.loss.log_loss_results(self.writer,loss_results,epoch)

            if epoch % self.save_every == 0:
                self.save_model_on_epoch(epoch)

    def _is_shuffle(self):
        return True

    def match_devices(self,input_batch):
        if isinstance(input_batch,dict):
            for k in input_batch.keys():
                input_batch[k] = input_batch[k].to(self.device)
        else:
            input_batch = input_batch.to(self.device)
        return input_batch 


    def save_model_on_epoch(self, epoch):
        if self.accelerator.is_main_process:
            num_gpus = self.accelerator.state.num_processes
            if num_gpus > 1:
                original_model = self.model.module
            else:
                original_model = self.model

            self.save_model_checkpoint(original_model,epoch)

        self.accelerator.wait_for_everyone()