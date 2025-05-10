docker run -it --name my_local_geth_node \
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
    --miner.etherbase "0xE8027148Da1726e6C8dd176f034008E4921D6Fc0" \
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