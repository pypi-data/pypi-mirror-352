import sys
from os.path  import dirname, abspath
from flask import Flask, request, redirect, jsonify
from flask_restx import Api, Resource, reqparse, abort
from decimal import Decimal
from flask_cors import CORS
from flask_caching import Cache

bkpath   = sys.path[:]
base_dir = dirname(abspath(__file__))
sys.path.insert(0, dirname(base_dir))

from moc_prices_source import get_price, ALL, version
from moc_prices_source.cli import command, option
from moc_prices_source.redis_conn import use_redis

sys.path = bkpath


title='MoC prices source API Rest webservice'
description="""

<br>
### Description

This is the API Rest webservice that comes integrated in the python **moc_prices_source** package.

<br>
### Purpose

Simplify integrations with other environments than **Python**.

<br>
### Refrences

* [Source code in Github](https://github.com/money-on-chain/moc_prices_source)
* [Package from Python package index (PyPI)](https://pypi.org/project/moneyonchain-prices-source)

<br>
<br>

## Endpoints
"""

all_coinpairs = list([str(x) for x in ALL])

app = Flask(__name__)

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app)


class HashMethod():

    def __init__(self, *options, info=lambda x: None, pre="") -> None:
        self._pre = pre
        self.info = info
        self.options = list(map(lambda x: str(x).strip().lower(), list(options)))
        self.out = []

    def __call__(self, x) -> None:
        self.out = []
        for key, value in eval(x):
            key=str(key).strip().lower()
            if key in self.options:
                value=str(value).strip().lower()
                self.out.append((key, value))
        return self

    def hexdigest(self):
        hash_ = repr(self.out) if self.out else ""
        if self._pre:
            hash_ = f"{self._pre}{hash_}"
        self.info(f"hash = {repr(hash_)}")
        return hash_


api = Api(
    app,
    prefix='/api',
    doc='/api/doc',
    version=f"v{version}",
    title=title,
    description=description,
)

CORS(app, resources={r'/*': {'origins': '*'}})



@app.after_request
def add_header(response):
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Cache-Control"] = 'public, max-age=0'
    return response



@app.before_request
def before_request_func():
    if request.path.startswith('/api/doc'):
        if request.args.get('url'):
            return redirect('/api/doc')



@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith('/api/'):
        return jsonify(
            code=e.code,
            name=e.name,
            description=e.description
        ), 404
    return redirect('/api/doc')



@app.route('/')
def index():
    return redirect('/api/doc')



coinpairs_ns = api.namespace('coinpairs', description='Coinpairs related operations')



@coinpairs_ns.route('/')
class CoinPairsList(Resource):

    def get(self):
        """Shows a list of all supported coinpairs"""
        return all_coinpairs



coinpair_value_get = reqparse.RequestParser()
coinpair_value_get.add_argument(
    'coinpair',
    choices = all_coinpairs,
    type = str,
    help = 'Coinpair symbols')

bad_coinpair_choice = (400, 'Bad coinpair choice')
coinpair_value_not_found = (404, 'Coinpair value not found')

@coinpairs_ns.route('/get_value')
@coinpairs_ns.response(200, 'Success!')
@coinpairs_ns.response(*bad_coinpair_choice)
@coinpairs_ns.response(*coinpair_value_not_found)
class CoinPairValue(Resource):

    @coinpairs_ns.expect(coinpair_value_get)
    @cache.cached(
        timeout=5,
        query_string=True,
        hash_method=HashMethod(
            'coinpair',
            pre="get_coinpair_value",
            #info=lambda x: app.logger.info(f"Cache: {x}")
        )
    )
    def get(self):
        """Get the price of a specific coinpair"""

        args = coinpair_value_get.parse_args()
        coinpair = args['coinpair']

        if coinpair not in all_coinpairs:
            abort(*bad_coinpair_choice)

        detail = {}
        value = get_price(
            coinpairs=coinpair,
            detail=detail,
            serializable=True,
            ignore_zero_weighing=True)

        if isinstance(value, dict):
            value = dict([(str(k), float(v)) for (k, v) in value.items()])

        if isinstance(value, Decimal):
            value = float(value)

        sources_count = {}
        sources_count_ok = {}
        for p in detail.get('prices', []):
            sub_coinpair = p.get('coinpair', 'unknown')
            sources_count[sub_coinpair] = sources_count.get(sub_coinpair, 0) + 1
            if p.get('ok'):
                sources_count_ok[sub_coinpair] = sources_count_ok.get(sub_coinpair, 0) + 1
            else:
                source = p.get('description', 'unknown')
                error = p.get('error', 'unknown')
                if coinpair==sub_coinpair:
                    app.logger.warning(f"{coinpair} --> {source} {error}")
                else:
                    app.logger.warning(f"{sub_coinpair} for {coinpair} --> {source} {error}")

        for sub_coinpair, p in detail.get('values', {}).items():
            error = p.get('error')
            if error:
                if coinpair==sub_coinpair:
                    app.logger.warning(f"{coinpair} --> {error}")
                else:
                    app.logger.warning(f"{sub_coinpair} for {coinpair} --> {error}")

        if sources_count:
            sources_count_str = ', '.join([ f"{k}: {sources_count_ok[k]} of {v}" for (k, v) in sources_count.items()])
            if len(sources_count)>1:
                app.logger.info(f"Sources count for {coinpair}: {sources_count_str}")
            else:
                app.logger.info(f"Sources count for {sources_count_str}")

        if value:
            app.logger.info(f"Value for {coinpair}: {value}")
        else:
            app.logger.error(f"Not value for {coinpair}")
            abort(*coinpair_value_not_found)
            

        out = {}
        out['required_coinpair'] = coinpair 
        out['value'] = value
        out['detail'] = detail

        return out



@api.route('/info')
class Info(Resource):

    def get(self):
        """Shows API info related"""
        return {
            'name:': title,
            'version' : version,
            'use_redis': use_redis
        }



def main(host='0.0.0.0', port=7989, debug=False):
    #default_logger_level = app.logger.level
    app.logger.setLevel(1)
    app.logger.info(f"{title} (v{version})")
    app.logger.info(f"service at {host}:{port}")
    #app.logger.setLevel(default_logger_level)
    app.run(debug=debug, host=host, port=port)


@command()
@option('-a', '--addr', 'host', type=str, default='0.0.0.0', help='Server host addr.')
@option('-p', '--port', 'port', type=int, default=7989, help='Server port.')
def server_cli(host, port):
    """MoC prices source API Rest webservice"""
    main(host=host, port=port)



if __name__ == '__main__':
    main(debug=True)
