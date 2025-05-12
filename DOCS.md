# Průvodce: Lokální Ethereum PoW Blockchain s Geth v Dockeru

Tento průvodce vás krok za krokem provede nastavením soukromého, lokálního Ethereum blockchainu běžícího na Proof-of-Work (PoW) konsenzu pomocí Gethu v Docker kontejneru. Na tento blockchain následně nasadíme jednoduchý smart kontrakt pro ukládání hašů.

## Část 1: Příprava Prostředí a Blockchainu

### Krok 1: Co budeš potřebovat (Předpoklady)

1. **Docker:** Ujistěte se, že máte na svém počítači nainstalovaný a spuštěný Docker. Pokud ne, stáhněte si ho a nainstalujte z [oficiálních stránek Dockeru](https://www.docker.com/get-started).
2. **Terminál/Příkazový řádek:** Budete pracovat v terminálu (např. Bash, PowerShell, CMD).

### Krok 2: Vytvoření Projektového Adresáře

Na svém počítači si vytvořte nový adresář pro tento projekt. Otevřete terminál a zadejte:

```bash
mkdir muj-eth-projekt
cd muj-eth-projekt
```

(Všechny další příkazy budeme spouštět z tohoto adresáře muj-eth-projekt).

### Krok 3: Vytvoření genesis.json Souboru

Vytvořte v adresáři muj-eth-projekt soubor s názvem genesis.json a vložte do něj následující obsah:

```json
{
    "config": {
        "chainId": 12345,
        "homesteadBlock": 0,
        "eip150Block": 0,
        "eip155Block": 0,
        "eip158Block": 0,
        "byzantiumBlock": 0,
        "constantinopleBlock": 0,
        "petersburgBlock": 0,
        "ethash": {}
    },
    "difficulty": "0x200",
    "gasLimit": "0x8000000",
    "alloc": {
        // Zde za chvíli přidáme tvůj nový účet
    },
    "timestamp": "0x0000000000000000",
    "extradata": "0x0000000000000000000000000000000000000000000000000000000000000000"
}
```

- **chainId: 12345**: Unikátní ID vašeho blockchainu.
- **ethash: {}**: Říká Gethu, že chceme Proof-of-Work (Ethash) konsenzus.
- **difficulty: "0x200"**: Nízká obtížnost pro rychlé těžení bloků na lokálním testnetu.
- **alloc: {}**: Sem za chvíli přidáme adresu vašeho účtu a počáteční zůstatek ETH.

### Krok 4: Vytvoření Adresáře pro Data Gethu

Geth potřebuje místo, kam si bude ukládat data blockchainu a vaše účty (keystore). Vytvořte podadresář:

```bash
mkdir geth_data_docker
```

### Krok 5: Vytvoření Nového Ethereum Účtu

Použijeme Docker s Geth image ethereum/client-go:v1.10.26. Tato verze Gethu plně podporuje start nových PoW sítí.
Spusťte v terminálu:

```bash
docker run -it --rm \
  -v "$(pwd)/geth_data_docker:/app/geth-data" \
  ethereum/client-go:v1.10.26 --datadir /app/geth-data account new
```

- `-v "$(pwd)/geth_data_docker:/app/geth-data"`: Mapuje váš lokální adresář geth_data_docker do adresáře /app/geth-data uvnitř Docker kontejneru. Geth si tam uloží keystore soubor.

Geth vás vyzve k zadání hesla: Password:. Zadejte nějaké heslo (např. pixmapixma pro tento PoC).

Znovu vás vyzve: Repeat password:. Zadejte stejné heslo.

**DŮLEŽITÉ:** Geth vypíše něco jako:

```
Public address of the key:   0xTVOJE_NOVA_ADRESA_NAPRIKLAD_0123ABC...
Path of the secret key file: /app/geth-data/keystore/UTC--...--TVOJE_NOVA_ADRESA...
```

Pečlivě si zkopírujte a uložte tu Public address of the key (např. 0xTVOJE_NOVA_ADRESA...). Budete ji potřebovat.
Zapamatujte si heslo, které jste zadali!

### Krok 6: Úprava genesis.json – Přidání Účtu do alloc

Otevřete znovu soubor genesis.json. Do sekce alloc vložte adresu, kterou jste právě vytvořili, a přidělte jí nějaké Ethery. Nahraďte 0xTVOJE_NOVA_ADRESA_Z_KROKU_5 vaší skutečnou novou adresou.

```json
{
    "config": {
        "chainId": 12345,
        "homesteadBlock": 0,
        "eip150Block": 0,
        "eip155Block": 0,
        "eip158Block": 0,
        "byzantiumBlock": 0,
        "constantinopleBlock": 0,
        "petersburgBlock": 0,
        "ethash": {}
    },
    "difficulty": "0x200",
    "gasLimit": "0x8000000",
    "alloc": {
        "0xTVOJE_NOVA_ADRESA_Z_KROKU_5": {  /* <-- ZDE VLOŽTE SVOU NOVOU ADRESU */
            "balance": "5000000000000000000000"  /* 5000 ETH v Wei */
        }
    },
    "timestamp": "0x0000000000000000",
    "extradata": "0x0000000000000000000000000000000000000000000000000000000000000000"
}
```

Uložte soubor genesis.json.

### Krok 7: Inicializace Blockchainu

Teď řekneme Gethu, aby vytvořil první (genesis) blok podle vašeho genesis.json.

```bash
docker run -it --rm \
  -v "$(pwd)/geth_data_docker:/app/geth-data" \
  -v "$(pwd)/genesis.json:/app/genesis.json" \
  ethereum/client-go:v1.10.26 --datadir /app/geth-data init /app/genesis.json
```

- `-v "$(pwd)/genesis.json:/app/genesis.json"`: Mapuje váš lokální genesis.json do kontejneru.
- Měli byste vidět výstup obsahující Successfully wrote genesis state.

### Krok 8: Spuštění Geth Nodu (Váš Lokální Blockchain)

Nyní spustíme samotný Geth node. Bude těžit, zpřístupní RPC rozhraní atd.
Nahraďte 0xTVOJE_NOVA_ADRESA_Z_KROKU_5 vaší skutečnou novou adresou!

```bash
docker run -it --name muj_geth_node_poc \
  -v "$(pwd)/geth_data_docker:/app/geth-data" \
  -p 8545:8545 \
  -p 8546:8546 \
  -p 30303:30303 \
  -p 30303:30303/udp \
  ethereum/client-go:v1.10.26 \
    --datadir /app/geth-data \
    --networkid 12345 \
    --nodiscover \
    --mine \
    --miner.etherbase "0xTVOJE_NOVA_ADRESA_Z_KROKU_5" \
    --http \
    --http.addr "0.0.0.0" \
    --http.port 8545 \
    --http.corsdomain "*" \
    --http.api "eth,net,web3,personal,miner" \
    --ws \
    --ws.addr "0.0.0.0" \
    --ws.port 8546 \
    --ws.origins "*" \
    --ws.api "eth,net,web3,personal,miner" \
    --allow-insecure-unlock \
    console
```

* `--name muj_geth_node_poc`: Pojmenuje váš Docker kontejner.
* `-p 8545:8545`: Mapuje port pro HTTP RPC.
* `--mine`: Říká Gethu, aby těžil.
* `--miner.etherbase "0xTVOJE_NOVA_ADRESA_Z_KROKU_5"`: Adresa, na kterou půjdou odměny z těžení.
* `--allow-insecure-unlock`: Povolí odemykání účtů přes RPC (pro pohodlí v lokálním vývoji).
* `console`: Spustí Geth JavaScript konzoli.

Po chvíli (může to trvat i několik minut, než se vygeneruje DAG pro těžení) byste měli vidět logy, že Geth těží nové bloky. Otevře se Geth konzole (`>`).

### Krok 9: Ověření v Geth Konzoli

1. **Zkontrolujte počáteční zůstatek (mělo by být 5000 ETH):**
   ```javascript
   > web3.fromWei(eth.getBalance("0xTVOJE_NOVA_ADRESA_Z_KROKU_5"), "ether")
   ```

2. **Zkontrolujte číslo bloku (mělo by být 0, pak začne růst, jak Geth těží):**
   ```javascript
   > eth.blockNumber
   ```

3. **Odemkněte svůj účet (bude potřeba pro nasazení kontraktu):**
   Použijte heslo, které jste zadali v Kroku 5.
   ```javascript
   > personal.unlockAccount("0xTVOJE_NOVA_ADRESA_Z_KROKU_5", "tvojeHesloZkroku5", 3600) // Odemkne na 1 hodinu
   ```
   Mělo by to vrátit `true`.

## Část 2: Smart Kontrakt

### Krok 10: Vytvoření Smart Kontraktu (`HashStorage.sol`)

V adresáři `muj-eth-projekt` vytvořte soubor HashStorage.sol s následujícím obsahem:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HashStorage {
    address public owner;
    mapping(uint256 => bytes32) public storedHashes;
    uint256 public hashCount;

    event HashStored(uint256 indexed id, bytes32 hashValue, address indexed storer);

    constructor() {
        owner = msg.sender; // Ten, kdo nasadí kontrakt, bude vlastník
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Ownable: caller is not the owner");
        _;
    }

    function storeHash(bytes32 _hash) public onlyOwner {
        hashCount++;
        storedHashes[hashCount] = _hash;
        emit HashStored(hashCount, _hash, msg.sender);
    }

    function getHash(uint256 _id) public view returns (bytes32) {
        require(_id > 0 && _id <= hashCount, "HashStorage: ID out of bounds");
        return storedHashes[_id];
    }

    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "Ownable: new owner is the zero address");
        owner = newOwner;
    }
}
```

### Krok 11: Použití Remix IDE pro Nasazení

Otevřete webový prohlížeč a jděte na https://remix.ethereum.org.

**Nahrajte nebo vytvořte soubor:**
- V levém panelu ("File Explorers") vytvořte nový soubor HashStorage.sol a vložte do něj kód z Kroku 10.

**Zkompilujte kontrakt:**
- Přejděte na záložku "SOLIDITY COMPILER" (vlevo).
- "COMPILER": Vyberte verzi kompilátoru, která odpovídá pragma solidity ^0.8.0; (např. 0.8.0 nebo 0.8.20 atd.).
- "EVM VERSION": V "Advanced Configurations" nastavte na istanbul (nebo petersburg). To je důležité pro kompatibilitu s Geth v1.10.26.
- Klikněte na "Compile HashStorage.sol". Neměly by být žádné chyby.

**Připojte Remix k vašemu Geth Nodu:**
- Přejděte na záložku "DEPLOY & RUN TRANSACTIONS" (vlevo).
- "ENVIRONMENT": Vyberte "Web3 Provider".
- "Web3 Provider Endpoint": Zadejte http://127.0.0.1:8545. Klikněte "OK".
- Měli byste vidět svou adresu (z Kroku 5) v sekci "ACCOUNT" a její zůstatek.

**Nasaďte kontrakt:**
- Ujistěte se, že váš účet v Geth konzoli je stále odemčený (viz Krok 9, bod 3).
- V Remixu, v sekci "CONTRACT", by měl být vybrán HashStorage.
- Pole "VALUE" nechte na 0 Wei.
- Klikněte na oranžové tlačítko "Deploy".
- Sledujte terminál Remixu (dole). Po chvíli (až Geth vytěží blok) by se mělo objevit Transaction mined and execution succeed.
- Níže v sekci "Deployed Contracts" se objeví váš nasazený kontrakt s jeho adresou. Tuto adresu si poznamenejte!

### Krok 12: Interakce s Nasazeným Kontraktem v Remixu

V Remixu, v sekci "Deployed Contracts", rozklikněte váš nasazený HashStorage.

- **owner** (modré tlačítko): Klikněte, zobrazí se vaše adresa.
- **storeHash** (oranžové tlačítko): Zadejte nějaký hash (např. 0xabcdef123...) a klikněte. Bude to transakce.
- **hashCount** (modré tlačítko): Po úspěšném storeHash by se mělo zvýšit.
- **getHash** (modré tlačítko): Zadejte ID (např. 1) a získejte uložený hash.

## Část 3: Správa Nodu

### Krok 13: Připojení Čisté Geth Konzole (když hlavní těží)

Když v hlavním okně Dockeru běží těžení a logy, je těžké zadávat příkazy. Otevřete nový terminál a zadejte:

```bash
docker exec -it muj_geth_node_poc geth attach ipc:///app/geth-data/geth.ipc
```

Tím získáte novou, čistou Geth konzoli připojenou ke stejnému nodu.

### Krok 14: Zastavení Geth Nodu

V Geth konzoli (buď v hlavní, nebo v té připojené přes attach) zadejte `exit` nebo stiskněte Ctrl+D.

Pokud se Docker kontejner neukončí sám, v terminálu, kde jste spustili docker run..., stiskněte Ctrl+C. Pokud to nepomůže, z jiného terminálu:

```bash
docker stop muj_geth_node_poc
```

(Volitelné) Pokud chcete kontejner odstranit (data v geth_data_docker zůstanou):

```bash
docker rm muj_geth_node_poc
```

### Krok 15: Opětovné Spuštění Geth Nodu

Pro opětovné spuštění (se zachováním všech dat a nasazených kontraktů) použijte stejný docker run příkaz z Kroku 8. Geth načte existující data.

Similar code found with 1 license type

Apollyus: @GitHubCopilot 

GitHub Copilot: Sorry, there is no context or conversation provided to infer the user's goal. Please provide more details or clarify your requirements.