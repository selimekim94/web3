import json
import requests
from eth_abi import decode_single, encode_single
from eth_utils import decode_hex
from web3 import Web3

if __name__ == '__main__':
    from_address = Web3.toChecksumAddress('0xe15c53bd99ff828ad155c45c0fa2a5506744b143')
    to_address = Web3.toChecksumAddress('0x021F48697343a6396BaFC01795a4C140b637F4B4')
    slot = 5  # mapping(address => uint256) public lastTransaction

    endpoint_uri = 'https://bsc-dataseed.binance.org/'
    web3 = Web3(provider=Web3.HTTPProvider(endpoint_uri=endpoint_uri))
    if web3.isConnected():
        contract_address = Web3.toChecksumAddress(to_address)
        key = encode_single('address', from_address)
        index = encode_single('uint256', slot)
        new_key = web3.sha3(key + index)
        storage = web3.toHex(new_key)
        storage = decode_single('uint256', decode_hex(storage))
        slot = storage
        print(slot)
        # get storage from block
        storage_value = web3.eth.getStorageAt(contract_address,
                                              storage)
        storage_value = Web3.toHex(storage_value)
        storage_value = decode_hex(storage_value)
        decoded = decode_single('uint256', storage_value)
        print(decoded)
        #
        # state override
        contract_func_data = web3.toHex(web3.sha3(text='lastTransaction(address)'))
        contract_func_data = contract_func_data[0:10]
        encoded_address = encode_single('address', from_address)
        data = contract_func_data + encoded_address.hex()
        payload = json.dumps(
            {
                "jsonrpc": "2.0", "id": 1, "method": "eth_call",
                "params": [
                    {"to": to_address,
                     "from": from_address,
                     "gas": hex(Web3.toWei(0.1, 'ether')),
                     "data": data
                     }, "latest",
                    {
                        from_address: {"balance": hex(Web3.toWei(100, 'ether'))},
                        to_address: {
                            "stateDiff": {
                                f"{web3.toHex(encode_single('uint256', slot))}": f"{Web3.toHex(encode_single('uint256', web3.eth.block_number))}",
                            }
                        }
                    }
                ]
            })
        response = requests.post(endpoint_uri,
                                 headers={
                                     'Content-Type': 'application/json'
                                 }, data=payload)
        json_data = response.json()
        result = json_data['result']
        response = decode_hex(
            result)
        decoded = decode_single('uint256', response)
        print(decoded)
    else:
        print('Can not connect to chain')
