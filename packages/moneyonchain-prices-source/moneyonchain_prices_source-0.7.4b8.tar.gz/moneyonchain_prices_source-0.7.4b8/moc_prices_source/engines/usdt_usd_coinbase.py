from engine_base import Base, USDT_USD


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Coinbase"
    _uri         = "https://api.coinbase.com/v2/exchange-rates?currency=USDT"
    _coinpair    = USDT_USD

    def _map(self, data):
        return {
            'price':  data['data']['rates']['USD']
            }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
