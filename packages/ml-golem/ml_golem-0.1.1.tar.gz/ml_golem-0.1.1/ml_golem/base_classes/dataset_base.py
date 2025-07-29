import torch
from torch.utils.data import Dataset
from ml_golem.model_loading_logic.config_class_instantiator import ConfigBasedClass
from ml_golem.model_loading_logic.model_config_keywords import ModelConfigKeywords
from file_golem import FileDatatypes


class DatasetBase(ConfigBasedClass,Dataset):
    DEFAULT_DATASOURCE = 'default_datasource'

    def __init__(self,args,subconfig_keys):
        super().__init__(args,subconfig_keys)

        self.has_index = self.config.get(ModelConfigKeywords.HAS_INDEX.value,False)
        self.is_preloaded = self.config.get(ModelConfigKeywords.IS_PRELOADED.value, False)


        datasources= self.config.get(ModelConfigKeywords.DATA_SOURCES.value, {})
        self.datasources = {}
        if len(datasources) == 0:
            self.datasources[self.DEFAULT_DATASOURCE] = self.extract_dataset_config_and_datatype(self.config,self.DEFAULT_DATASOURCE)
        else:
            for key in datasources.keys():
                datasource_config = datasources[key]
                self.datasources[key] = self.extract_dataset_config_and_datatype(datasource_config,key)
        self.db = {}


    def _default_config(self):
        defaults = {
            self.DEFAULT_DATASOURCE: {
                ModelConfigKeywords.CONFIG.value: None,
                ModelConfigKeywords.DATATYPE.value: None
            }
        }
        return defaults


    def extract_dataset_config_and_datatype(self,config,datasource_key):
        all_dataset_config_and_datatype = self._default_config()

        dataset_config = config.get(ModelConfigKeywords.CONFIG.value, None)
        if dataset_config is None:
            if datasource_key in all_dataset_config_and_datatype:
                dataset_config = all_dataset_config_and_datatype[datasource_key][ModelConfigKeywords.CONFIG.value]
            
        datatype = self.data_io.fetch_class_from_config(
            config = config,
            subconfig_keys=[ModelConfigKeywords.DATATYPE.value],
            is_required=False)
        if datatype is None:
            if datasource_key in all_dataset_config_and_datatype:
                datatype = all_dataset_config_and_datatype[datasource_key][ModelConfigKeywords.DATATYPE.value]

        data_dict = {
            ModelConfigKeywords.CONFIG.value: dataset_config,
            ModelConfigKeywords.DATATYPE.value: datatype
        }
        return data_dict



    def _load_item(self,idx):
        dataset_config = self._get_dataset_config()
        datatype = self._get_datatype()
        data_item = self.data_io.load_data(datatype,data_args={
            datatype.IDX: idx,
            datatype.CONFIG_NAME: dataset_config})
        
        if self.has_index:
            data_item[datatype.IDX] = torch.tensor(idx)
        
        return data_item
    
    def __len__(self):
        dataset_config = self._get_dataset_config()
        datatype = self._get_datatype()
        return self.data_io.get_datatype_length(datatype,data_args= {
            datatype.CONFIG_NAME: dataset_config
        })


    def _get_custom_collate_fn(self):
        if hasattr(self,'custom_collate_fn'):
            return self.custom_collate_fn
        
        datatype = self._get_datatype()
        if datatype is None or (datatype.FILE_DATATYPE != FileDatatypes.TORCH):
            return lambda x: x    
        return None


    def __getitem__(self, idx):
        if self.is_preloaded:
            if len(self.db)==0:
                for i in range(len(self)):
                    x = self._load_item(i)
                    self.db[i] = x

            return self.db[idx]
        else:
            return self._load_item(idx)
        

    def _get_dataset_config(self,datasource=None):
        if len(self.datasources) == 1:
            return self.datasources[self.DEFAULT_DATASOURCE][ModelConfigKeywords.CONFIG.value]
        if datasource is not None:
            return self.datasources[datasource][ModelConfigKeywords.CONFIG.value]
        raise Exception('Multiple datasources found, please specify the datasource')
    

    def _get_datatype(self,datasource=None):
        if len(self.datasources) == 1:
            return self.datasources[self.DEFAULT_DATASOURCE][ModelConfigKeywords.DATATYPE.value]
        if datasource is not None:
            return self.datasources[datasource][ModelConfigKeywords.DATATYPE.value]
        return None
        #raise Exception('Multiple datasources found, please specify the datasource')
