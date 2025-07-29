from ml_golem.model_loading_logic.config_class_instantiator import ConfigBasedClass
from ml_golem.model_loading_logic.model_config_keywords import ModelConfigKeywords
from torch.utils.data import DataLoader
from ml_golem.base_classes.dataset_base import DatasetBase
            
class DataLoadingBase(ConfigBasedClass):
    def _initialize_dataloader(self,args,subconfig_keys):
        config = self.data_io.fetch_subconfig(
            self.data_io.load_config(self.global_config_name),
            subconfig_keys=subconfig_keys)

        if ModelConfigKeywords.DATASET.value not in config:
            return None
            
        dataset = self.instantiate_config_based_class(
            args,
            subconfig_keys=subconfig_keys+[ModelConfigKeywords.DATASET.value],
            default_class=DatasetBase)
        #collate_fn = 
        
        #dataset.custom_collate_fn if hasattr(dataset,'custom_collate_fn') else None

        dataloader_config= self.data_io.fetch_subconfig(config,
            subconfig_keys=[ModelConfigKeywords.DATALOADER.value])
        dataloader = DataLoader(dataset,
            batch_size=dataloader_config.get(ModelConfigKeywords.BATCH_SIZE.value, 1), 
            num_workers=dataloader_config.get(ModelConfigKeywords.NUM_WORKERS.value,1),
            collate_fn=dataset._get_custom_collate_fn(),
            shuffle=self._is_shuffle(), 
            pin_memory=True)
        return dataloader
    
    def _is_shuffle(self):
        return False