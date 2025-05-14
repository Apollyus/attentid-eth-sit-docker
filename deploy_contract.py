# // filepath: /home/vojtech/Documents/aaa_programovani/attentid-eth-sit-docker/deploy_contract.py
import json
import os
import web3 # For version
from web3 import Web3
from solcx import (
    compile_source, install_solc, set_solc_version,
    get_installed_solc_versions, get_solc_version
)
from solcx.exceptions import SolcError
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv() # Loads .env file from the current directory or parent

RPC_URL = os.getenv("RPC_URL", "http://192.168.37.205:8545")
SOLIDITY_FILE_PATH = "./StringStorage.sol"  # Path to your .sol file
CONTRACT_NAME = "StringStorage"             # The name of the contract inside the .sol file
DEPLOYER_ACCOUNT_ADDRESS = "0xbA302F03A4a8515d816b9Ac367cB7A5B6f537C9c" # Address of the account deploying
DEPLOYER_ACCOUNT_PASSWORD = "pixmapixma" # Password for the deploying account
# If your contract constructor takes arguments, add them here:
# CONSTRUCTOR_ARGS = [arg1, arg2, ...]
CONSTRUCTOR_ARGS = []


def compile_contract(file_path, contract_name_in_script):
    print(f"Compiling {file_path} for contract '{contract_name_in_script}'...")
    target_solc_version_str = 'v0.8.20' # String with 'v'
    target_evm_version = 'istanbul'

    try:
        installed_versions = get_installed_solc_versions() # List of Version objects
        print(f"Installed solc versions: {installed_versions}")

        # Correctly check if the target version is installed
        is_version_installed = False
        for v_obj in installed_versions:
            if str(v_obj) == target_solc_version_str.lstrip('v'): # Compare '0.8.20' with '0.8.20'
                is_version_installed = True
                print(f"Solc {target_solc_version_str} is already installed.")
                break
        
        if not is_version_installed:
            print(f"Solc {target_solc_version_str} not found. Attempting to install...")
            install_solc(target_solc_version_str)
            installed_versions = get_installed_solc_versions() # Re-check
            # Re-check after installation attempt
            is_version_installed_after_attempt = False
            for v_obj in installed_versions:
                 if str(v_obj) == target_solc_version_str.lstrip('v'):
                    is_version_installed_after_attempt = True
                    break
            if not is_version_installed_after_attempt:
                print(f"Failed to install or find solc {target_solc_version_str} after attempt. Please install it manually or check permissions.")
                return None, None
            print(f"Successfully installed/confirmed solc {target_solc_version_str}.")

        print(f"Setting solc version to {target_solc_version_str}...")
        set_solc_version(target_solc_version_str) # set_solc_version can take 'v0.8.20' or '0.8.20'
        current_solc_version_obj = get_solc_version()
        print(f"Successfully set solc version to: {current_solc_version_obj}")
        if str(current_solc_version_obj) != target_solc_version_str.lstrip('v'):
             print(f"Warning: Solc version mismatch after setting. Expected {target_solc_version_str.lstrip('v')}, got {current_solc_version_obj}")

    except Exception as e:
        print(f"Solc version setup error: {type(e).__name__} - {e}.")
        print(f"Ensure solc can be installed (e.g., internet connection, write permissions for py-solc-x).")
        return None, None

    with open(file_path, 'r') as f:
        source_code = f.read()

    try:
        print(f"Attempting to compile source with solc {get_solc_version()} targeting EVM: {target_evm_version}...")
        compiled_sol = compile_source(
            source_code,
            output_values=['abi', 'bin'],
            solc_version=str(get_solc_version()),
            evm_version=target_evm_version
        )
        
        print(f"Compiled contract keys: {list(compiled_sol.keys())}")
        
        expected_key_stdin = f'<stdin>:{contract_name_in_script}'
        
        if expected_key_stdin in compiled_sol:
            contract_interface = compiled_sol[expected_key_stdin]
        else:
            found_key = None
            for key in compiled_sol.keys():
                if key.endswith(f":{contract_name_in_script}"):
                    found_key = key
                    break
            if found_key:
                print(f"Found contract using alternative key: {found_key}")
                contract_interface = compiled_sol[found_key]
            else:
                print(f"Error: Contract '{contract_name_in_script}' not found in compiled output.")
                print(f"Please ensure '{contract_name_in_script}' matches the contract name in '{file_path}'.")
                print(f"And that the solidity code in '{file_path}' compiles without errors.")
                return None, None

        abi = contract_interface['abi']
        bytecode = contract_interface['bin']
        print("Compilation successful.")
        return abi, bytecode
    except SolcError as e:
        print(f"Solidity Compiler Error (SolcError): {e}")
        return None, None
    except KeyError as e:
        print(f"Compilation failed (KeyError): {e}. This usually means the contract name '{contract_name_in_script}' was not found in the compiled output.")
        print(f"Ensure the contract name is correct and the Solidity file compiles without errors.")
        return None, None
    except Exception as e:
        print(f"Generic compilation failed: {type(e).__name__} - {e}")
        return None, None

# ... (rest of your deploy() function and if __name__ == "__main__": block remains the same)
def deploy():
    print(f"Using web3.py version: {web3.__version__}")

    if not DEPLOYER_ACCOUNT_ADDRESS or not DEPLOYER_ACCOUNT_PASSWORD:
        print("Error: DEPLOYER_ACCOUNT_ADDRESS and DEPLOYER_ACCOUNT_PASSWORD must be set.")
        return

    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    if not w3.is_connected():
        print(f"Failed to connect to Ethereum node at {RPC_URL}")
        return

    print(f"✅ Connected to {RPC_URL}, Chain ID: {w3.eth.chain_id}")

    # --- Debug prints ---
    print(f"DEBUG: dir(w3) = {dir(w3)}")
    if hasattr(w3, 'geth'):
        print(f"DEBUG: dir(w3.geth) = {dir(w3.geth)}")
        if hasattr(w3.geth, 'personal'):
            print(f"DEBUG: w3.geth.personal attribute exists.")
            if hasattr(w3.geth.personal, 'unlock_account'):
                 print(f"DEBUG: w3.geth.personal.unlock_account method exists.")
            else:
                 print(f"DEBUG: w3.geth.personal.unlock_account method does NOT exist.")
        else:
            print(f"DEBUG: w3.geth.personal attribute does NOT exist.")
        
        if hasattr(w3.geth, 'miner'):
            print(f"DEBUG: w3.geth.miner attribute exists.")
        else:
            print(f"DEBUG: w3.geth.miner attribute does NOT exist.")
    else:
        print(f"DEBUG: w3.geth attribute does not exist.")
    # --- End of debug prints ---

    w3.eth.default_account = DEPLOYER_ACCOUNT_ADDRESS

    # Unlock account
    unlocked = False
    try:
        print(f"Attempting to unlock account: {DEPLOYER_ACCOUNT_ADDRESS}")
        
        if hasattr(w3, 'geth') and hasattr(w3.geth, 'personal') and callable(getattr(w3.geth.personal, 'unlock_account', None)):
            print("DEBUG: Attempting unlock via w3.geth.personal.unlock_account")
            unlocked = w3.geth.personal.unlock_account(DEPLOYER_ACCOUNT_ADDRESS, DEPLOYER_ACCOUNT_PASSWORD, 0)
        else:
            print("DEBUG: w3.geth.personal.unlock_account not found or not callable.")
            print("DEBUG: Attempting direct RPC call for personal_unlockAccount.")
            try:
                rpc_response = w3.manager.request_blocking("personal_unlockAccount", 
                                                           [DEPLOYER_ACCOUNT_ADDRESS, DEPLOYER_ACCOUNT_PASSWORD, 0])
                unlocked = bool(rpc_response) 
                if unlocked:
                    print("DEBUG: Direct RPC call to personal_unlockAccount successful.")
                else:
                    print("DEBUG: Direct RPC call to personal_unlockAccount returned false (unlock failed by node).")
            except Exception as rpc_e:
                print(f"DEBUG: Error during direct RPC call to personal_unlockAccount: {type(rpc_e).__name__} - {rpc_e}")
                unlocked = False


        if not unlocked:
            print(f"❌ Failed to unlock account {DEPLOYER_ACCOUNT_ADDRESS}. Check password, account existence, and Geth logs.")
            return
        print(f"✅ Account {DEPLOYER_ACCOUNT_ADDRESS} unlocked successfully.")

    except AttributeError as e: 
        print(f"Error unlocking account (AttributeError): {e}")
        return
    except Exception as e: 
        print(f"An error occurred during account unlock: {type(e).__name__} - {e}")
        return

    abi, bytecode = compile_contract(SOLIDITY_FILE_PATH, CONTRACT_NAME)
    if not abi or not bytecode:
        return

    ContractFactory = w3.eth.contract(abi=abi, bytecode=bytecode)

    print(f"Deploying {CONTRACT_NAME}...")
    try:
        gas_estimate = ContractFactory.constructor(*CONSTRUCTOR_ARGS).estimate_gas({'from': DEPLOYER_ACCOUNT_ADDRESS})
        print(f"Estimated gas: {gas_estimate}")

        tx_hash = ContractFactory.constructor(*CONSTRUCTOR_ARGS).transact({
            'from': DEPLOYER_ACCOUNT_ADDRESS,
            'gas': int(gas_estimate * 1.2) 
        })
        print(f"Transaction sent. TX Hash: {tx_hash.hex()}")

        print("Waiting for transaction receipt...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        if tx_receipt.status == 1:
            print(f"✅ Contract {CONTRACT_NAME} deployed successfully!")
            print(f"   Contract Address: {tx_receipt.contractAddress}")
            print(f"   Block Number: {tx_receipt.blockNumber}")
            print(f"   Gas Used: {tx_receipt.gasUsed}")
        else:
            print(f"⛔ Contract deployment failed. Status: {tx_receipt.status}")
            print(f"   Transaction Receipt: {tx_receipt}")

    except Exception as e:
        print(f"Deployment error: {type(e).__name__} - {e}")

if __name__ == "__main__":
    deploy()