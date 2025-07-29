from ml_golem.model_loading_logic.config_class_instantiator import ConfigBasedClass
from ml_golem.model_loading_logic.model_config_keywords import ModelConfigKeywords

class VisualizerBase(ConfigBasedClass):
    def __init__(self,args,subconfig_keys):
        super().__init__(args,subconfig_keys)

        self.dataset = self.instantiate_config_based_class(args,
            subconfig_keys=self.subconfig_keys[:-1] + [ModelConfigKeywords.DATASET.value])

        print('VisualizerBase init')
        print(self.dataset)


    def __call__(self):
        raise Exception('Not Implemented')