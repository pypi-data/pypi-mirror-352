import torch.nn as nn
from file_golem import FilePathEntries
from ml_golem.datatypes import ModelCheckpoint
from ml_golem.model_loading_logic.model_config_keywords import ModelConfigKeywords
from ml_golem.base_classes.dataloading_base import DataLoadingBase

class ModelIOBase(DataLoadingBase):
    def __init__(self, args,subconfig_keys):
        super().__init__(args,subconfig_keys)
        self.dataloader = self._initialize_dataloader(args,self.subconfig_keys)
        self.model = self.instantiate_config_based_class(args, subconfig_keys =[ModelConfigKeywords.ARCHITECTURE.value])
        self.model, self.resume_epoch = self.load_model_checkpoint(self.config)

    def save_model_checkpoint(self,model,epoch):
        self.data_io.save_data(ModelCheckpoint, data_args = {
            ModelCheckpoint.CONFIG_NAME: self.global_config_name,
            ModelCheckpoint.EPOCH: epoch,
            ModelCheckpoint.DATA: model.state_dict()
        })

    def load_model_checkpoint(self,task_config):
        resume_epoch =  task_config.get(ModelConfigKeywords.RESUME_EPOCH.value, -1)
        if not issubclass(type(self.model), nn.Module):
            return self.model, resume_epoch

        if resume_epoch == -1:
            data_args = {ModelCheckpoint.CONFIG_NAME: self.global_config_name,
                             ModelCheckpoint.EPOCH:FilePathEntries.OPEN_ENTRY }
            for file_path in self.data_io.get_file_iterator(ModelCheckpoint, data_args = data_args):
                missing_data_args = self.data_io.retrieve_data_args(ModelCheckpoint,data_args, file_path)
                new_epoch = int(missing_data_args[ModelCheckpoint.EPOCH])
                if new_epoch > resume_epoch:
                    resume_epoch = new_epoch

        if resume_epoch == -1:
            print('No checkpoint found, initializing model from scratch')
            resume_epoch = 0
        else:
            model_checkpoint = self.data_io.load_data(ModelCheckpoint, data_args = {
                ModelCheckpoint.CONFIG_NAME: self.global_config_name,
                ModelCheckpoint.EPOCH: resume_epoch
            })

            self.model.load_state_dict(model_checkpoint)
        return self.model, resume_epoch