from engine_base import BaseOnChain, BPRO_BTC, get_env
from decimal import Decimal



moc_sc_addr_options = {
    'mainnet': '0xb9C42EFc8ec54490a37cA91c423F7285Fa01e257', 
}

simplified_abi = """
[
  {
    "constant": true,
    "inputs": [],
    "name": "bproTecPrice",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "payable": false,
    "stateMutability": "view",
    "type": "function"
  }
]
"""

class Engine(BaseOnChain):

    _name          = BaseOnChain._name_from_file(__file__)
    _description   = "MOC onchain"
    _coinpair      = BPRO_BTC
    _uri           = get_env('RSK_NODE', 'https://public-node.rsk.co')
    _sc_addr       = get_env('MOC_STATE_ADDR', 'mainnet')

    def _get_price(self):

        sc_addr = self.to_checksum_address(
            moc_sc_addr_options.get(
                self._sc_addr.lower().strip(),
                self._sc_addr.lower().strip()
            )
        )

        try:            

            w3 = self.make_web3_obj_with_uri()

            sc = w3.eth.contract(address=sc_addr, abi=simplified_abi)

            value = sc.functions.bproTecPrice().call()

            value = Decimal(int(value))/Decimal(10**18)
            
            return value

        except Exception as e:
            self._error = str(e)
            return None


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    if engine.error:
        print(f"{engine} Error: {engine.error}")
    else:
        print(engine)
