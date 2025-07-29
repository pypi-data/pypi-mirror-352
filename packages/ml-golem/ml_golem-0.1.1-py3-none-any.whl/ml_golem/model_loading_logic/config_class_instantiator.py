from ml_golem.base_classes.data_io_object import DataIOObject

from ml_golem.model_loading_logic.model_config_keywords import ModelConfigKeywords

class ConfigBasedClass(DataIOObject):
    def __init__(self,args,subconfig_keys=[]):
        super().__init__(args)
        self.subconfig_keys = subconfig_keys
        self.global_config_name = args.config_name
        #if subconfig_keys is not None:
        self.config = self.data_io.fetch_subconfig(
            self.data_io.load_config(self.global_config_name),
            subconfig_keys= subconfig_keys)

    def instantiate_config_based_class(self,args,subconfig_keys,default_class=None):
        config_class =self.data_io.fetch_class_from_config(
            is_required = False,
            config_name = self.global_config_name,
            subconfig_keys = subconfig_keys + [ModelConfigKeywords.MODEL_CLASS.value])
        config_class = config_class if config_class is not None else default_class
        if config_class is None:
            raise Exception(f'No class found for keys {subconfig_keys} in config {self.global_config_name}')
        return config_class(args,subconfig_keys)
