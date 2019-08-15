class Urls:
    _base = "https://api.tdameritrade.com/v1/"
    accounts = _base + "accounts"

    quote = _base + "marketdata/quotes"
    option_chain = _base + "marketdata/chains"

    search = _base + "instruments"
    fundamental = search
    history = _base + "marketdata/%s/pricehistory"

    auth = _base + "oauth2/token"

    all_orders = _base + "orders"
    order_for_account = _base + "accounts/%s/orders"
    transactions = _base + "accounts/%s/transactions"

    hours = _base + "marketdata/hours"
    movers = _base + "marketdata/%s/movers"
