from enum import Enum
class ModelConfigKeywords(Enum):
    MODEL_CLASS = 'model_class'
    TRAINING = 'training'
    INFERENCE = 'inference'
    #EVALUATION = 'evaluation'
    ARCHITECTURE = 'architecture'
    VISUALIZATION = 'visualization'
    CONFIG = 'config'


    RESUME_EPOCH = 'resume_epoch'

    #TRAINING KEYWORDS
    EPOCHS = 'epochs'
    LEARNING_RATE = 'learning_rate'
    SAVE_EVERY = 'save_every'
    CAN_DISPLAY_EPOCH_PROGRESS = 'can_display_epoch_progress'

    DATASET = 'dataset'

    MODEL_OUTPUT = 'model_output'
    GROUND_TRUTH = 'ground_truth'
    DATATYPE = 'datatype'
    DATA_SOURCES = 'data_sources'

    NUM_WORKERS = 'num_workers'
    BATCH_SIZE = 'batch_size'
    DATALOADER = 'dataloader'
    LOSS = 'loss'

    IS_PRELOADED = 'is_preloaded'
    HAS_INDEX = 'has_index'


    GRID_SEARCH = 'grid_search'
    GRID_SEARCH_PARAMS = 'grid_search_params'
    GRID_ACTIONS = 'grid_actions'
    GRID_SEARCH_STYLE = 'grid_search_style'
    GRID_SLURM_CONFIG = 'grid_slurm_config'