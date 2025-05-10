// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0; // Nebo novější, např. ^0.8.20

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