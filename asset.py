import json
from algosdk import account, mnemonic
from algosdk.v2client import algod, indexer
from algosdk.future.transaction import AssetConfigTxn, AssetTransferTxn, AssetFreezeTxn

# # Print all assets created by an account *using the indexer*
# def print_all_assets_createdby(account_id):
#     account_id = accounts_dict[account_id]['pk']
#     assets = indexer_client.search_assets(creator=account_id)
#     print('List of the assets:\n{}'.format(json.dumps(assets, indent=4)))
#     return assets

# # Print details of an asset using its assetid
# def print_details_asset(algodclient=algod_client, assetid=0):
#     asset_info = indexer_client.asset_info(assetid)
#     print('Info asset:\n{}'.format(json.dumps(asset_info, indent=4)))
#     return asset_info

# Initialize default values to avoid errors
accounts_dict = None
algod_client = None

# Print balance of accounts in accounts_dict
def print_accounts_balance(accounts=accounts_dict):
    for account in accounts_dict:
        # For each account, select the address and recover infos
        account_info = algod_client.account_info(accounts_dict[account]['pk'])
        print('\nInfo account: {}\nAmount: {}\n'.format(json.dumps(account_info, indent=4),
                account_info.get('amount')))

# Wait for a transaction to be confirmed
def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print('Waiting for confirmation')
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print('Transaction {} confirmed in round {}.'.format(txid, txinfo.get('confirmed-round')))
    return txinfo

# Print an asset created by a particular account
def print_asset_created(algodclient=algod_client, account=account, assetid=0):
    account_info = algodclient.account_info(account)
    idx = 0
    for my_account_info in account_info['created-assets']:
        scrutinized_asset = account_info['created-assets'][idx]
        idx +=1
        if (scrutinized_asset['index'] == assetid):
            print('Asset created by the account: {}\nAsset ID: {}'.format(
                account_info.get('address'), scrutinized_asset['index']))

            print(json.dumps(my_account_info['params'], indent=4))
            return
    print('No asset with ID: {} created by the account: {}'.format(assetid, account))

# Print an asset holded by a particular account
def print_asset_holding(algodclient=algod_client, account=account, assetid=0):
    account_info = algodclient.account_info(account)
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx +=1
        if (scrutinized_asset['asset-id'] == assetid):
            print('Asset holding by the account: {}\nAsset ID: {}'.format(
                account_info.get('address'), scrutinized_asset['asset-id']))
            
            print(json.dumps(scrutinized_asset, indent=4))
            return
    print('No asset with ID: {} holding by the account: {}'.format(assetid, account))   

# Print all assets holded by a particular account
def print_all_assets_holdingby(params_dict):
    algod_client, _ = algod_connect(params_dict)
    account = params_dict['account']
    account_info = algod_client.account_info(account)
    idx = 0
    print('List of asset holding by the account: {}'.format(account))
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx +=1
        print(json.dumps(scrutinized_asset, indent=4))
    return

# Print all assets created by an account
def print_all_assets_createdby(params_dict):
    algod_client, _ = algod_connect(params_dict)
    account = params_dict['account']
    account_info = algod_client.account_info(account)
    idx = 0
    print('List of asset created by the account: {}'.format(account))
    for my_account_info in account_info['created-assets']:
        scrutinized_asset = account_info['created-assets'][idx]
        idx +=1
        print(json.dumps(scrutinized_asset, indent=4))
    return

# Configure a connection from a dictionary
def algod_connect(params_dict):
    if params_dict['purestake'] == True:
        # Configure address and token of the Purestake node 
        algod_address = params_dict['address']
        algod_token = params_dict['token']
        purestake_token = {'X-Api-key': algod_token}
        
        # Initializes an algod client with purestake
        algod_client = algod.AlgodClient(algod_token, algod_address, headers=purestake_token)
        
    else:
        # Configure address and token of the node
        algod_address = params_dict['address']
        algod_token = params_dict['token']
        
        # Initializes an algod client
        algod_client = algod.AlgodClient(algod_token, algod_address)

    # Recover required values for all types of transactions
    params = algod_client.suggested_params()

    # Return a tuple with algod_client witch is needed for the connexion and the defaults transactions's params
    return (algod_client, params)

def create(params_dict):
    algod_client, params = algod_connect(params_dict)
    print('\n=====================================CREATE ASSET=====================================')
    # Create an asset with the parameters params_dict

    # For each created or owned asset it is necessary to have a minimum balance on the account of -
    # -> 100,000 microAlgos

    txn = AssetConfigTxn(
    sender=params_dict['sender'],
    sp=params,
    total=params_dict['total'],
    default_frozen=params_dict['default_frozen'],
    unit_name=params_dict['unit_name'],
    asset_name=params_dict['asset_name'],
    manager=params_dict['manager'],
    reserve=params_dict['reserve'],
    freeze=params_dict['freeze'],
    clawback=params_dict['clawback'],
    decimals=params_dict['decimals'])
    
    private_key = mnemonic.to_private_key(params_dict['mnemonic'])

    # Sign transaction
    stxn = txn.sign(private_key)
    
    # Send signed transaction to the network and recover its ID
    txid = algod_client.send_transaction(stxn)
    print('Transaction ID: ', txid)
    
    wait_for_confirmation(algod_client, txid)
    
    try:
        ptx = algod_client.pending_transaction_info(txid)
        asset_id = ptx['asset-index']
        print_asset_created(algod_client, params_dict['sender'], asset_id)
        print_asset_holding(algod_client, params_dict['sender'], asset_id)
    except Exception as e:
        print(e)

    return asset_id

def edit(params_dict):
    algod_client, params = algod_connect(params_dict)
    print('\n=====================================EDIT ASSET=====================================')
    print('asset id:', params_dict['asset'])
    txn = AssetConfigTxn(
        sender=params_dict['sender'],
        sp=params,
        index=params_dict['asset'],
        manager=params_dict['manager'],
        reserve=params_dict['reserve'],
        freeze=params_dict['freeze'],
        clawback=params_dict['clawback'])
    
    private_key = mnemonic.to_private_key(params_dict['mnemonic'])

    stxn = txn.sign(private_key)
    txid = algod_client.send_transaction(stxn)
    print('Transaction ID: ', txid)
    
    wait_for_confirmation(algod_client, txid)    
    # Print the asset after the confirmation of the transaction
    print_asset_created(algod_client, params_dict['sender'], params_dict['asset'])

def optin(params_dict):
    algod_client, params = algod_connect(params_dict)
    print('\n=====================================OPT-IN ASSET=====================================')
    print('asset_id:', params_dict['asset'])
    account_info = algod_client.account_info(params_dict['account'])
    holding = None
    idx = 0
    
    # Verify if the account have an asset with the id: params_dict['asset'] 
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx +=1
        if scrutinized_asset['asset-id'] == params_dict['asset']:
            holding = True
            break
    
    # If the account is not holding the asset, optin the asset for this account
    if not holding:
        txn = AssetTransferTxn(
            sender=params_dict['account'],
            sp=params,
            receiver=params_dict['account'],
            amt=0,
            index=params_dict['asset'])
    
    private_key = mnemonic.to_private_key(params_dict['mnemonic'])
    stxn = txn.sign(private_key)
    txid = algod_client.send_transaction(stxn)
    print('Transaction ID: ', txid)
    
    wait_for_confirmation(algod_client, txid)
    print_asset_holding(algod_client, params_dict['account'], params_dict['asset'])

# --- Tranfert un actif
def transfer(asset_id, sender_account_id, receiver_account_id):
    print('\n=====================================ASSET TRANSFER=====================================')
    print('asset_id:', asset_id)
    # Transfert une valeur de 10 actifs du compte sender_account_id au compte receiver_account_id
    txn = AssetTransferTxn(
        sender=accounts_dict[sender_account_id]['pk'],
        sp=params,
        receiver=accounts_dict[receiver_account_id]['pk'],
        amt=10,
        index=asset_id)
    
    stxn = txn.sign(accounts_dict[sender_account_id]['sk'])
    txid = algod_client.send_transaction(stxn)
    print('Transaction ID: ', txid)
    
    wait_for_confirmation(algod_client, txid)
    # txid_list.append(txid)
    
    # Attend la confirmation le la liste de toutes les transactions précédentes
    # wait_for_confirmation_list(algod_client, txid_list)
    print_asset_holding(algod_client, accounts_dict[receiver_account_id]['pk'], asset_id)

# --- Gèle un actif
def freeze(asset_id, sender_account_id, receiver_account_id):
    print('\n=====================================FREEZE ASSET=====================================')
    print('asset_id:', asset_id)
    txn = AssetFreezeTxn(
        sender=accounts_dict[sender_account_id]['pk'],
        sp=params,
        target=accounts_dict[receiver_account_id]['pk'],
        index=asset_id,
        new_freeze_state=True)
    
    stxn = txn.sign(accounts_dict[sender_account_id]['sk'])
    txid = algod_client.send_transaction(stxn)
    print('Transaction ID: ', txid)
    
    wait_for_confirmation(algod_client, txid)
    print_asset_holding(algod_client, accounts_dict[receiver_account_id]['pk'], asset_id)

# --- Révoque un actif
def revoke(asset_id, sender_account_id, receiver_account_id, target_account_id):
    print('\n=====================================REVOKE ASSET=====================================')
    print('asset_id:', asset_id)
    print('\n--- Before revoke')
    print('\nAccount', target_account_id)
    print_asset_holding(algod_client, accounts_dict[target_account_id]['pk'], asset_id)
    
    print('\nAccount', receiver_account_id)
    print_asset_holding(algod_client, accounts_dict[receiver_account_id]['pk'], asset_id)
    
    txn = AssetTransferTxn(
        sender=accounts_dict[sender_account_id]['pk'],
        sp=params,
        receiver=accounts_dict[receiver_account_id]['pk'],
        index=asset_id,
        amt=10,
        revocation_target=accounts_dict[target_account_id]['pk'])
    
    stxn = txn.sign(accounts_dict[sender_account_id]['sk'])
    txid = algod_client.send_transaction(stxn)
    print('Transaction ID:', txid)
    
    wait_for_confirmation(algod_client, txid)
    print('\n--- After revoke')
    print('\nAccount', target_account_id)
    print_asset_holding(algod_client, accounts_dict[target_account_id]['pk'], asset_id)
    
    print('\nAccount', receiver_account_id)
    print_asset_holding(algod_client, accounts_dict[receiver_account_id]['pk'], asset_id)

# --- Destroy an asset
def destroy(params_dict):
    algod_client, params = algod_connect(params_dict)
    print('\n=====================================DESTROY ASSET=====================================')
    print('asset id:', params_dict['asset'])

    # For destroy an asset, the account need to have all unites of the named asset
    # The sender have to be the manager account
    txn = AssetConfigTxn(
        sender=params_dict['sender'],
        sp=params,
        index=params_dict['asset'],
        strict_empty_address_check=False)
    
    private_key = mnemonic.to_private_key(params_dict['mnemonic'])
    stxn = txn.sign(private_key)

    txid = algod_client.send_transaction(stxn)
    print('Transaction ID:', txid)
    
    wait_for_confirmation(algod_client, txid)
    
    try:
        print_asset_holding(algod_client, params_dict['sender'], params_dict['asset'])
        print_asset_created(algod_client, params_dict['sender'], params_dict['asset'])   
    except Exception as e:
        print(e)

def destroy_all(account_id):
    print('\n=====================================DESTROY ALL ASSETS CREATED BY AN ACCOUNT=====================================')
    # Récupere le tableau des assets créé par ce compte
    assets_id_dict = print_all_assets_createdby(account_id=account_id)
    for asset_id in assets_id_dict:
        asset = print_details_asset(assetid=asset_id)
        print(asset)
        # Affiche le nombre total d'unitées en circulation pour chaque actif du dictionnaire
        # print(asset['params']['total'])
        # if asset['']:
        #     pass

        