### Návod k použití funkcí `store_string` a `get_string`

Tyto funkce slouží k ukládání textových řetězců do Ethereum smart kontraktu a jejich následnému čtení.

#### 1. Předpoklady pro použití funkcí

Abyste mohli tyto funkce úspěšně volat, je nutné mít:

*   **Nainstalované závislosti:**
    Ujistěte se, že máte nainstalované potřebné Python knihovny, zejména `web3` a `python-dotenv`. Obvykle se instalují pomocí `pip install -r requirements.txt`.

*   **Konfigurační soubor .env:**
    Musíte mít v kořenovém adresáři projektu (nebo tam, odkud je `dotenv` schopno ho načíst) soubor .env s následujícími proměnnými:
    ```env
    # filepath: .env
    CONTRACT_ADDRESS="ADRESA_VASEHO_KONTRAKTU"
    ACCOUNT_PASSWORD="HESLO_K_VASUMU_UCTU"
    ACCOUNT_ADDRESS="ADRESA_VASEHO_UCTU"
    RPC_URL="URL_VASEHO_ETHEREUM_NODU" 
    ```

*   **ABI soubor kontraktu:**
    Soubor `StringStorage_abi.json` musí být dostupný ve stejném adresáři, odkud je skript spouštěn, nebo cesta k němu musí být správně specifikována.

*   **Inicializované objekty `web3` a `contract`:**
    Funkce `store_string` a `get_string` předpokládají, že již existují a jsou správně nakonfigurovány globální proměnné `web3` (instance `Web3`) a `contract` (instance kontraktu `web3.eth.contract`). Tyto jsou inicializovány na začátku skriptu test.py.

    ```python
    # filepath: /home/vojtech/Documents/aaa_programovani/attentid-eth-sit-docker/python_source/test.py
    # ... (importy a načtení .env) ...

    # Inicializace Web3
    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    # ... (kontrola připojení) ...

    # Načtení kontraktu
    contract_address = web3.to_checksum_address(CONTRACT_ADDRESS)
    ACCOUNT_ADDRESS = web3.to_checksum_address(ACCOUNT_ADDRESS) # Také se používá v store_string
    
    with open('StringStorage_abi.json') as f:
        contract_abi = json.load(f)
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    
    # ... (další kód skriptu) ...
    ```

#### 2. Funkce `store_string(value: str) -> int`

*   **Účel:** Uloží zadaný textový řetězec (`value`) do smart kontraktu na blockchainu.
*   **Parametry:**
    *   `value (str)`: Textový řetězec, který chcete uložit.
*   **Návratová hodnota:**
    *   `int`: Unikátní ID, pod kterým byl řetězec uložen v kontraktu.
    *   `None`: Pokud došlo k chybě během procesu (např. chyba při odemykání účtu, selhání transakce).
*   **Co dělá:**
    1.  Pokusí se odemknout účet specifikovaný v `ACCOUNT_ADDRESS` pomocí `ACCOUNT_PASSWORD`.
    2.  Odhadne potřebný gas pro transakci.
    3.  Sestaví a odešle transakci volající funkci `storeString(value)` smart kontraktu.
    4.  Čeká na potvrzení transakce na blockchainu.
    5.  Pokud je transakce úspěšná, získá a vrátí nové ID uloženého stringu (zavoláním `stringCount()` na kontraktu).
    6.  Vypisuje průběžné informace a případné chyby do konzole.

*   **Příklad použití (v kontextu skriptu test.py):**
    ```python
    # filepath: /home/vojtech/Documents/aaa_programovani/attentid-eth-sit-docker/python_source/test.py
    # ... (za předpokladu, že web3 a contract jsou inicializovány) ...

    muj_text = "Testovací zpráva pro blockchain."
    nove_id = store_string(muj_text)

    if nove_id is not None:
        print(f"Text '{muj_text}' byl úspěšně uložen pod ID: {nove_id}")
    else:
        print(f"Nepodařilo se uložit text '{muj_text}'.")
    ```

#### 3. Funkce `get_string(string_id: int) -> str`

*   **Účel:** Načte textový řetězec z blockchainu, který byl dříve uložen pod zadaným `string_id`.
*   **Parametry:**
    *   `string_id (int)`: ID řetězce, který chcete načíst.
*   **Návratová hodnota:**
    *   `str`: Načtený textový řetězec.
    *   `None`: Pokud došlo k chybě během čtení nebo pokud string s daným ID neexistuje.
*   **Co dělá:**
    1.  Zavolá funkci `getString(string_id)` smart kontraktu (toto je `call`, tedy neodesílá transakci a nespotřebovává gas kromě poplatku za čtení u RPC providera).
    2.  Vrátí načtený řetězec.
    3.  Vypisuje případné chyby do konzole.

*   **Příklad použití (v kontextu skriptu test.py):**
    ```python
    # filepath: /home/vojtech/Documents/aaa_programovani/attentid-eth-sit-docker/python_source/test.py
    # ... (za předpokladu, že web3 a contract jsou inicializovány a nove_id bylo získáno) ...

    if nove_id is not None: # Předpokládáme, že nove_id bylo získáno z store_string
        nacteny_text = get_string(nove_id)
        if nacteny_text is not None:
            print(f"Text uložený pod ID {nove_id} je: '{nacteny_text}'")
        else:
            print(f"Nepodařilo se načíst text pro ID {nove_id}.")
    ```

Pamatujte, že pro správnou funkci těchto metod je klíčové mít správně nastavené všechny proměnné v .env souboru a funkční připojení k Ethereum nodu. Tyto funkce jsou navrženy tak, aby fungovaly v rámci struktury skriptu test.py, kde jsou proměnné jako `web3`, `contract`, `ACCOUNT_ADDRESS`, a `ACCOUNT_PASSWORD` dostupné v jejich kontextu.