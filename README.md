# Proof of Concept: Lokální Ethereum Blockchain pro Ukládání Hašů

Tento projekt slouží jako Proof of Concept (PoC) pro vytvoření soukromého, lokálního Ethereum blockchainu běžícího na Proof-of-Work (PoW) konsenzu. Umožňuje nasazení a interakci se smart kontraktem navrženým pro ukládání hašů dat s řízeným přístupem k zápisu.

Tento repozitář je součástí projektu AttentID, systému na potvrzování přítomnosti osob s bezpečným ukládáním na blockchain.

**Autor:** Vojtěch Faltýnek
**Datum:** Květen 2024

## Bezpečnostní Upozornění

Tento projekt je určen **výhradně pro vzdělávací a testovací účely (Proof of Concept)**.

V tomto repozitáři **může být obsažen** adresář `geth_data_docker/keystore` obsahující zašifrované privátní klíče k testovacím účtům. **Nikdy neukládejte privátní klíče nebo keystore soubory k reálným účtům na veřejné repozitáře!**

### Doporučení pro bezpečné použití:

1. Používejte nové a unikátní klíče pro každé nasazení.
2. Ukládejte privátní klíče offline a chráněné silným heslem.
3. Zvažte použití hardwarových peněženek.
4. Hesla musí být silná a unikátní.

## Obsah

1. [Cíl Projektu](#cíl-projektu)
2. [Použité Technologie](#použité-technologie)
3. [Požadavky](#požadavky)
4. [Kroky pro Spuštění](#kroky-pro-spuštění)
5. [Nasazení Smart Kontraktu](#nasazení-smart-kontraktu)
6. [Interakce s Kontraktem](#interakce-s-kontraktem)
7. [Zastavení a Uložení Blockchainu](#zastavení-a-uložení-blockchainu)

## Cíl Projektu

Nastavení a provoz soukromého Ethereum blockchainu s PoW konsenzem a nasazení smart kontraktu pro ukládání hašů.

## Použité Technologie

* **Geth (Go Ethereum)**: v1.10.26-stable
* **Docker**: Kontejnerizace a izolace prostředí
* **Solidity**: Programování smart kontraktů
* **Remix IDE**: Webové IDE pro smart kontrakty

## Požadavky

* Docker nainstalovaný v systému

## Kroky pro Spuštění

1. Klonujte repozitář:

   ```bash
   git clone <URL>
   cd <adresář>
   ```
2. Vytvořte nový účet:

   ```bash
   docker run -it --rm -v "$(pwd)/geth_data_docker:/app/geth-data" ethereum/client-go:v1.10.26 --datadir /app/geth-data account new
   ```
3. Spusťte Geth node:

   ```bash
   docker run -it --name eth_node -v "$(pwd)/geth_data_docker:/app/geth-data" -p 8545:8545 ethereum/client-go:v1.10.26 --http --mine
   ```

## Nasazení Smart Kontraktu

1. Otevřete Remix IDE.
2. Kompilujte kontrakt HashStorage.sol.
3. Nasazení pomocí Web3 Provideru na `http://127.0.0.1:8545`.

## Interakce s Kontraktem

* `storeHash(bytes32 _hash)`: Uloží hash.
* `getHash(uint256 _id)`: Načte uložený hash.

## Zastavení a Uložení Blockchainu

* Ukončení nodu:

  ```bash
  docker stop eth_node
  ```
