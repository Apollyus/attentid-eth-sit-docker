# Nastavení těžby na druhém Raspberry Pi (Miner 2)

Tento návod popisuje kroky pro spuštění dalšího Geth uzlu na druhém Raspberry Pi, který se připojí k vaší existující soukromé Ethereum síti a bude na ní těžit.

## Předpoklady

1.  **První Geth uzel (Miner 1) běží:** Ujistěte se, že váš první Geth uzel (např. `muj_geth_node_poc`) je spuštěný a funkční na prvním Raspberry Pi.
2.  **IP adresa prvního RPi:** Znáte IP adresu prvního Raspberry Pi ve vaší lokální síti.
3.  **Docker na druhém RPi:** Na druhém Raspberry Pi je nainstalovaný a funkční Docker.
4.  **`genesis.json` soubor:** Máte k dispozici soubor `genesis.json` (identický s tím, který byl použit pro inicializaci prvního uzlu) na druhém Raspberry Pi v adresáři, odkud budete spouštět příkazy.

## Kroky na druhém Raspberry Pi

### 1. Získání Enode URL prvního uzlu

Pokud ji ještě nemáte, zjistěte Enode URL vašeho prvního běžícího uzlu. Připojte se k jeho Geth konzoli:

```bash
sudo docker exec -it muj_geth_node_poc geth attach ipc:///app/geth-data/geth.ipc
```

A v konzoli zadejte:

```javascript
admin.nodeInfo.enode
```

Zkopírujte si výstupní URL. Nahraďte `[::]` nebo `127.0.0.1` skutečnou IP adresou prvního Raspberry Pi.
Příklad (jak je uvedeno ve vašich poznámkách, **použijte vaši aktuální IP adresu prvního RPi**):

`enode://7721f8e333a641c34896242f3d78b34e9779226ce2128a90b5de841bb9e0cf456765b67e6841a3e5e4f0b74d1cbe156221e8452c72be8c3516246ac988f8b4eb@192.168.37.205:30303?discport=0`

### 2. Příprava adresáře a účtu pro Miner 2

a.  **Vytvoření datového adresáře:**
    Na druhém Raspberry Pi vytvořte adresář pro data nového uzlu:
    ```bash
    mkdir geth_data_node2_docker
    ```

b.  **Vytvoření nového Ethereum účtu (Minerbase pro Miner 2):**
    ```bash
    sudo docker run --rm -v "$(pwd)/geth_data_node2_docker:/app/geth-data" ethereum/client-go:v1.10.26 --datadir /app/geth-data account new
    ```
    Zadejte silné heslo a pečlivě si ho zapamatujte. Zkopírujte si zobrazenou `Public address of the key`.
    Pro tento návod budeme předpokládat, že nová adresa je (jak je uvedeno ve vašich poznámkách):
    `0x82A6CEcF5D7441fBe7306615545548916f7632f0`

### 3. Inicializace Geth uzlu Miner 2

Inicializujte datový adresář nového uzlu pomocí vašeho `genesis.json` souboru:
```bash
sudo docker run --rm \
  -v "$(pwd)/geth_data_node2_docker:/app/geth-data" \
  -v "$(pwd)/genesis.json:/app/genesis.json" \
  ethereum/client-go:v1.10.26 --datadir /app/geth-data init /app/genesis.json
```
*Pokud se zobrazí chyba `database contains incompatible genesis`, vymažte obsah adresáře `geth_data_node2_docker` (`sudo rm -rf $(pwd)/geth_data_node2_docker/*`) a zkuste inicializaci znovu.*

### 4. Spuštění Geth uzlu Miner 2

Nyní spusťte Docker kontejner pro druhý Geth uzel. Tento příkaz je založen na vašich poznámkách:

```bash
sudo docker run -it --name muj_geth_node_miner2 \
  -v "$(pwd)/geth_data_node2_docker:/app/geth-data" \
  -p 8545:8545 \
  -p 8546:8546 \
  -p 30303:30303 \
  -p 30303:30303/udp \
  ethereum/client-go:v1.10.26 \
    --datadir /app/geth-data \
    --networkid 12345 \
    --bootnodes "enode://7721f8e333a641c34896242f3d78b34e9779226ce2128a90b5de841bb9e0cf456765b67e6841a3e5e4f0b74d1cbe156221e8452c72be8c3516246ac988f8b4eb@192.168.37.205:30303?discport=0" \
    --mine \
    --miner.etherbase "0x82A6CEcF5D7441fBe7306615545548916f7632f0" \
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
**Poznámky k příkazu:**
*   Nahraďte Enode URL v `--bootnodes` vaší skutečnou Enode URL prvního uzlu (včetně správné IP adresy).
*   Nahraďte adresu v `--miner.etherbase` vaší nově vytvořenou adresou pro Miner 2.
*   Porty `-p 8545:8545` a `-p 8546:8546` mohou kolidovat, pokud na druhém RPi již běží jiná služba na těchto portech. Pokud tento uzel nepotřebuje vystavovat RPC/WS porty externě nebo pokud je budete používat pouze lokálně v rámci Docker sítě, můžete zvážit jejich změnu nebo odstranění (např. `-p 18545:8545`). Pro připojení k síti a těžbu nejsou externí RPC porty nezbytně nutné, pokud neplánujete s tímto uzlem interagovat přes RPC z hostitelského systému. Port `30303` pro p2p komunikaci je důležitý.

### 5. Odemknutí účtu v Geth konzoli Miner 2

Po spuštění příkazu výše se otevře Geth konzole pro Miner 2. Abyste mohli začít těžit, musíte odemknout účet nastavený jako `miner.etherbase`:

```javascript
personal.unlockAccount("0x82A6CEcF5D7441fBe7306615545548916f7632f0", "VASE_HESLO_PRO_TENTO_UCET", 3600)
```
Nahraďte adresu a heslo vašimi skutečnými údaji. Číslo `3600` je doba odemčení v sekundách (1 hodina). Můžete použít `0` pro neomezenou dobu.

Po těchto krocích by se měl Miner 2 připojit k vašemu prvnímu uzlu a začít těžit bloky.
Můžete ověřit připojení peerů v Geth konzoli příkazem `admin.peers`.