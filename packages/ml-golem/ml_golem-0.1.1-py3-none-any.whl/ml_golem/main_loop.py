from ml_golem.argparsing import get_args_and_actions

def main_loop(_add_additional_args = lambda x, y: (x, y) , system_config_path = None, app_title = 'Default App Title'):
    print('Beginning program')
    args, actions = get_args_and_actions(_add_additional_args,system_config_path,app_title)
    for action in actions:
        if action(args):
            print('Program complete')
            return
    raise Exception(f'No action specified.')
