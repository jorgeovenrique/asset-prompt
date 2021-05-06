from asset import create as asset_create
from asset import edit as asset_edit
from asset import optin as asset_optin
from asset import destroy as asset_destroy
from asset import print_all_assets_createdby
import re

def asset_prompt():
    print('Tool for managing assets')
    print('------------------------')
    user_command = ''
    prompt_action = ''
    while True:
        user_command = input('What do you want to do ? Create [0], Edit [1], Optin[2], Destroy [3], List [4]: ')
        if user_command == '0':
            prompt_action = 'create'
            args_list = ['address', 'token', 'sender', 'total', 'unit_name', 'asset_name', 'manager', 'reserve', 
            'freeze', 'clawback', 'decimals', 'mnemonic']
            break
        
        elif user_command == '1':
            prompt_action = 'edit'
            args_list = ['address', 'token', 'sender', 'mnemonic', 'asset', 'manager', 'reserve', 'freeze', 'clawback']
            break

        elif user_command == '2':
            prompt_action = 'optin'
            args_list = ['address', 'token', 'account', 'mnemonic', 'asset']
            break

        elif user_command == '3':
            prompt_action = 'destroy'
            args_list = ['address', 'token', 'sender', 'mnemonic', 'asset']
            break

        elif user_command == '4':
            prompt_action = 'list'
            args_list = ['address', 'token', 'account']
            break

        elif user_command == 'exit':
            exit()

        else:
            print('Incorrect answer')

    params_dict = {}
    for arg in args_list:     
        # Modify prompt if "address" or "token" have to be configured
        if arg == 'address' or arg == 'token':
            user_command = input('algod {}: '.format(arg))

        # Modify prompt if "account" have to be configured
        elif arg == 'account' and prompt_action == 'list':
            user_command = input('creator {}: '.format(arg))

        elif arg == 'account' and prompt_action == 'optin':
            user_command = input('opt-in {}: '.format(arg))

        elif arg == 'asset':
            user_command = input('{} ID: '.format(arg))

        else:
            user_command = input('{}: '.format(arg))

        if user_command == 'exit':
            exit()

        # Verify if "address" is a purestake address
        if arg == 'address':
            purestake_address_regex = re.compile(r'^.*api\.purestake\.io.*$')
            if purestake_address_regex.match(user_command):
                params_dict['purestake'] = True
                # print('This is a purestake address')

            else: params_dict['purestake'] = False

        if arg == 'total' or arg == 'decimals' or arg == 'asset':
            int_regex = re.compile(r'^[0-9]+$')

            while int_regex.match(user_command) == None:
                print('This one have to be an integer ! Please try again')
                user_command = input('{}: '.format(arg))

                if user_command == 'exit':
                    exit()

            user_command = int(user_command)

        params_dict[arg] = user_command
        print('>', params_dict[arg])

    print('\nParams:\n-------')
    for key, value in params_dict.items():
        print('{}: {}'.format(key, value))

    # Default value of frozen param
    params_dict['default_frozen'] = False

    while True:
        user_command = input('Do you want to execute the action: [{}] with these parameters ?(Y/n): '.format(prompt_action))
        if user_command.lower() == 'yes' or user_command.lower() == 'y' or user_command == '':
            if prompt_action == 'create':
                asset_create(params_dict)

            elif prompt_action == 'edit':
                asset_edit(params_dict)

            elif prompt_action == 'optin':
                asset_optin(params_dict)

            elif prompt_action == 'destroy':
                asset_destroy(params_dict)

            elif prompt_action == 'list':
                print_all_assets_createdby(params_dict)

            else:
                print('prompt_action is incorrect')

        elif user_command.lower() == 'no' or user_command.lower() == 'n':
            # Here, find a way to replay the prompt loop
            exit()
        
        elif user_command == 'exit':
            exit()

        else:
            print('Incorrect answer')

while True:
    try:
        asset_prompt()
    except SystemExit:
        print('bye')
        exit()
    except:
        print('It seems the script did not run correctly, please try again')
        exit()
    # except Exception as e:
    #     raise
    #     exit()
