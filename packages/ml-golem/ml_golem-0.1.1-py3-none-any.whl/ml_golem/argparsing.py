import argparse
import random
from file_golem import FileIO
from file_golem._file_io_helper import _locate_class

from ml_golem.model_action import ModelAction
from ml_golem.overleaf.overleaf_transfer import OverleafTransfer
from ml_golem.grid_search.tensorboard_logic import TensorBoardLogic
from ml_golem.grid_search.config_copier import ConfigCopier
from ml_golem.grid_search.grid_search_builder import GridSearchBuilder

def add_flag_argument(parser,action_list,object_type,flag_name,flag_abbreviation=None,help_text=None):
    if help_text is None:
        help_text = f'Use this flag to enable {flag_name}'

    if flag_abbreviation is None:
        parser.add_argument(f'--{flag_name}',action='store_true',help=help_text)
    else:
        parser.add_argument(f'--{flag_name}',f'-{flag_abbreviation}',action='store_true',help=help_text)

    action = lambda args: (object_type(args)() or True) if getattr(args, flag_name) else False
    action_list.append(action)
    return parser, action_list


def get_args_and_actions(app_title,system_config_path,_add_additional_args):
    action_list = []
    parser = argparse.ArgumentParser(description=app_title)

    parser.add_argument('--data_io',default = None, help='Data IO object to use')
    parser.add_argument('--is_debug',action='store_true',help='Print debug statements')
    parser.add_argument('-st','--system_transfer',type=str, default=None, help='System that the data_io object is transfering into' )

    parser.add_argument('--seed', type=int,default=random.randint(0, 2**32 - 1), help='Seed for random number')
    parser.add_argument('-c','--config_name', type=str, default=None, help='Path to relevant omega conf file')


    parser.add_argument('-cc','--copy_config', type=str, default=None, help='Copy a config file')
    action_list.append(lambda args: (ConfigCopier(args)() or True) if args.copy_config else False)


    parser.add_argument('-t', '--train', action= 'store_true', help='Train the model')
    action_list.append(lambda args: (ModelAction(args).train(args) or True) if args.train else False)

    parser.add_argument('-i', '--inference', action= 'store_true', help='Have the model make inferences')
    action_list.append(lambda args: (ModelAction(args).inference(args) or True) if args.inference else False)

    # parser.add_argument('-e', '--evaluate', action= 'store_true', help='Evaluate the model after inference')
    # action_list.append(lambda args: (ModelAction(args).evaluate(args) or True) if args.evaluate else False)

    parser.add_argument('-w', '--wipe', action= 'store_true', help='Wipe the model and training logs')
    action_list.append(lambda args: (ModelAction(args).wipe() or True) if args.wipe else False)

    parser.add_argument('-g', '--grid_search', action= 'store_true', help='Run a grid search')
    action_list.append(lambda args: (GridSearchBuilder(args)() or True) if args.grid_search else False)

    parser.add_argument('-v', '--visualization_type', type=str, default=None , help='Resume training')
    action_list.append(lambda args: (ModelAction(args).visualize(args) or True) if args.visualization_type else False)

    parser.add_argument('-co', '--call_object', type=str, default=None, help='construct an object with args and call __call__')
    action_list.append(lambda args: (_locate_class(args.call_object)(args)() or True) if args.call_object else False)

    parser.add_argument('-ot', '--overleaf_transfer', action='store_true', help='Update git-linked Overleaf to contain the latest graphics')
    action_list.append(lambda args: (OverleafTransfer(args)() or True) if args.overleaf_transfer else False)

    parser.add_argument('-tb', '--tensorboard', action='store_true', help='run the tensorboard for a given config')
    action_list.append(lambda args: (TensorBoardLogic(args)() or True) if args.tensorboard else False)

    if _add_additional_args is not None:
        parser, action_list = _add_additional_args(parser,action_list)

    args = parser.parse_args()
    if 'help' in args:
        parser.print_help()

    args.data_io = FileIO(
        system_config_path=system_config_path,
        is_debug=args.is_debug,
        system_transfer = args.system_transfer
    )

    return args, action_list




def main_loop(
        app_title = 'Default App Title',
        system_config_path = 'conf/system_configs/system_conf.yaml',
        _add_additional_args = lambda x, y: (x, y)        
        ):
    print('Beginning program')
    args, actions = get_args_and_actions(app_title,system_config_path,_add_additional_args)
    for action in actions:
        if action(args):
            print('Program complete')
            return
    raise Exception(f'No action specified.')

