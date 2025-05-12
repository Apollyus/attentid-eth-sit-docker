from web3 import Web3
import json
import hashlib

# 1. Připojení k Ethereum nodu (tvůj lokální Geth)
rpc_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(rpc_url))

if not web3.is_connected():
    print("Chyba: Nepodařilo se připojit k Ethereum nodu!")
    exit()

print(f"Připojeno k Ethereum nodu. Chain ID: {web3.eth.chain_id}")

# 2. Načtení kontraktu
contract_address = web3.to_checksum_address("0xde478a41c3c9c7fceef869fee6bf4e1cdd04cd02")

# ABI zkopírované z Remixu (ponechávám původní ABI)
contract_abi = """
[
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "bytes32",
				"name": "hashValue",
				"type": "bytes32"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "storer",
				"type": "address"
			}
		],
		"name": "HashStored",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_id",
				"type": "uint256"
			}
		],
		"name": "getHash",
		"outputs": [
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "hashCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "_hash",
				"type": "bytes32"
			}
		],
		"name": "storeHash",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "storedHashes",
		"outputs": [
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]
"""

# Převod ABI z řetězce na Python objekt
abi_object = json.loads(contract_abi)
contract = web3.eth.contract(address=contract_address, abi=abi_object)

# 3. Účet pro odesílání transakcí - použijeme náš nově vytvořený účet
sender_address = "0x29FD9216fC3da9FD5E1D0387b4449975C5e902c2" # AKTUALIZUj NA SVŮJ ÚČET

# Heslo pro odemykání účtu
account_password = "pixmapixma"

# --- Funkce pro hashování a uložení ---
def hash_and_store_data(data_to_hash, account_address, private_key_hex=None):
    """Zahashuje data a uloží je na blockchain voláním smart kontraktu."""
    if isinstance(data_to_hash, str):
        data_to_hash = data_to_hash.encode('utf-8')

    # Vytvoření hashe (např. SHA256)
    data_hash = hashlib.sha256(data_to_hash).digest() # Výstup je bytes

    print(f"Zahashovaná data (bytes32 hex): {data_hash.hex()}")

    # Příprava transakce pro volání funkce 'storeHash'
    try:
        # Vždy se pokusíme odemknout účet
        unlock_success = web3.provider.make_request("personal_unlockAccount", [account_address, account_password, 60])        
        if unlock_success:
            print(f"Účet {account_address} úspěšně odemčen")
            nonce = web3.eth.get_transaction_count(account_address)
            tx_params = {
                'from': account_address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': web3.eth.gas_price,
            }
            
            transaction = contract.functions.storeHash(data_hash).build_transaction(tx_params)
            tx_hash = web3.eth.send_transaction(transaction)
            print(f"Transakce pro uložení hashe odeslána: {tx_hash.hex()}")
            
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Transakce zpracována. Status: {'Úspěch' if tx_receipt.status == 1 else 'Selhání'}")
            
            if tx_receipt.status == 1:
                current_hash_count = contract.functions.hashCount().call()
                print(f"Aktuální hashCount: {current_hash_count}, poslední uložené ID by mělo být toto.")
                return current_hash_count
            else:
                print("Uložení hashe selhalo.")
                return None
        else:
            print("Nepodařilo se odemknout účet.")
            
            # Pokud máme privátní klíč, zkusíme metodu s podepsáním transakce
            if private_key_hex:
                return _store_with_private_key(data_hash, account_address, private_key_hex)
            return None
    except Exception as e:
        print(f"Chyba při odemykání účtu nebo odesílání transakce: {e}")
        
        # Pokud máme privátní klíč, zkusíme metodu s podepsáním transakce jako záložní plán
        if private_key_hex:
            return _store_with_private_key(data_hash, account_address, private_key_hex)
        return None

def _store_with_private_key(data_hash, account_address, private_key_hex):
    """Pomocná funkce pro uložení hashe pomocí privátního klíče."""
    try:
        nonce = web3.eth.get_transaction_count(account_address)
        tx_params = {
            'from': account_address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': web3.eth.gas_price,
        }
        
        # Sestavení transakce
        transaction = contract.functions.storeHash(data_hash).build_transaction(tx_params)

        # Podepsání transakce
        signed_tx = web3.eth.account.sign_transaction(transaction, private_key=private_key_hex)

        # Odeslání podepsané transakce
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Transakce pro uložení hashe odeslána s privátním klíčem: {tx_hash.hex()}")

        # Čekání na zpracování transakce
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transakce zpracována. Status: {'Úspěch' if tx_receipt.status == 1 else 'Selhání'}")
        
        if tx_receipt.status == 1:
            current_hash_count = contract.functions.hashCount().call()
            print(f"Aktuální hashCount: {current_hash_count}, poslední uložené ID by mělo být toto.")
            return current_hash_count
        else:
            print("Uložení hashe selhalo.")
            return None
    except Exception as e:
        print(f"Chyba při odesílání transakce s privátním klíčem: {e}")
        return None

# --- Funkce pro získání hashe ---
def get_stored_hash(hash_id):
    """Získá uložený hash z blockchainu podle jeho ID."""
    try:
        stored_hash_bytes32 = contract.functions.getHash(hash_id).call()
        # stored_hash_bytes32 je typu bytes. Pro zobrazení jako hex:
        print(f"Získaný hash (ID: {hash_id}): {stored_hash_bytes32.hex()}")
        return stored_hash_bytes32
    except Exception as e:
        print(f"Chyba při získávání hashe (ID: {hash_id}): {e}")
        return None

# --- Příklad použití ---
if __name__ == "__main__":
    # Uložení nového hashe
    data_pro_blockchain = "Ahoj světe!!"
    
    print(f"Použití účtu {sender_address} pro uložení dat")
    new_hash_id = hash_and_store_data(data_pro_blockchain, sender_address)

    if new_hash_id:
        print(f"Data byla uložena pod ID: {new_hash_id}")
        # Získání uloženého hashe
        retrieved_hash = get_stored_hash(new_hash_id)
        if retrieved_hash:
            # Ověření (pro tento příklad, kdy známe původní data)
            original_data_hash = hashlib.sha256(data_pro_blockchain.encode('utf-8')).digest()
            if retrieved_hash == original_data_hash:
                print("Ověření úspěšné: Získaný hash odpovídá původnímu hashi.")
            else:
                print("Chyba ověření: Získaný hash NEODPOVÍDÁ původnímu hashi.")

    print(f"Aktuální počet uložených hašů: {contract.functions.hashCount().call()}")