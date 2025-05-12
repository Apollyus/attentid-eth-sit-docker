// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract StringStorage {
    address public owner;
    mapping(uint256 => string) public storedStrings;
    uint256 public stringCount;

    event StringStored(uint256 indexed id, string value, address indexed storer);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "StringStorage: caller is not the owner");
        _;
    }

    /**
     * @dev Stores a string in the contract
     * @param _value The string to store
     * @return The ID assigned to the stored string
     */
    function storeString(string calldata _value) public onlyOwner returns (uint256) {
        stringCount++;
        storedStrings[stringCount] = _value;
        emit StringStored(stringCount, _value, msg.sender);
        return stringCount;
    }

    /**
     * @dev Retrieves a stored string by its ID
     * @param _id The ID of the string to retrieve
     */
    function getString(uint256 _id) public view returns (string memory) {
        require(_id > 0 && _id <= stringCount, "StringStorage: ID out of bounds");
        return storedStrings[_id];
    }

    /**
     * @dev Updates a previously stored string
     * @param _id The ID of the string to update
     * @param _newValue The new string value
     */
    function updateString(uint256 _id, string calldata _newValue) public onlyOwner {
        require(_id > 0 && _id <= stringCount, "StringStorage: ID out of bounds");
        storedStrings[_id] = _newValue;
        emit StringStored(_id, _newValue, msg.sender);
    }

    /**
     * @dev Transfers ownership of the contract to a new address
     * @param newOwner The address of the new owner
     */
    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "StringStorage: new owner is the zero address");
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }
}