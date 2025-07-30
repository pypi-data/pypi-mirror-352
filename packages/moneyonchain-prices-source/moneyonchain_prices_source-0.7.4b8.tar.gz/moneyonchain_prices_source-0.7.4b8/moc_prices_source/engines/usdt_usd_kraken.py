from engine_base import Base, USDT_USD


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Kraken"
    _uri         = "https://api.kraken.com/0/public/Ticker?pair=USDTZUSD"
    _coinpair    = USDT_USD

    def _map(self, data):
        return {
            'price':  data['result']['USDTZUSD']['c'][0],
            'volume': data['result']['USDTZUSD']['v'][1] }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
