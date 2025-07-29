from ml_golem.model_loading_logic.config_class_instantiator import ConfigBasedClass

class LossBase(ConfigBasedClass):
    MAIN_LOSS = 'main_loss'
    def __init__(self,args,subconfig_keys):
        super().__init__(args,subconfig_keys)


    def __call__(self, model_input, model_output):
        raise Exception('Not Implemented')
    
    def log_loss_results(self,writer,loss_results,epoch):
        writer.add_scalar('Loss/Total', loss_results[self.MAIN_LOSS], epoch)