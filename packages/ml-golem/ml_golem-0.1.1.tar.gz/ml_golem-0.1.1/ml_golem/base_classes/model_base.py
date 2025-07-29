from ml_golem.model_loading_logic.config_class_instantiator import ConfigBasedClass
import torch.nn as nn

class ModelBase(ConfigBasedClass,nn.Module):
    def __init__(self,args,subconfig_keys):
        ConfigBasedClass.__init__(self, args, subconfig_keys)
        nn.Module.__init__(self)    