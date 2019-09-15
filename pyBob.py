import cbpro


class MyWebSocketClient(cbpro.WebsocketClient):
    def __init__(self):
        self.url = "wss://ws-feed.pro.coinbase.com/"
        self.products = ["BTC-USD"]
        self.channels = ['ticker', 'user', 'matches', 'level2', 'full']
        self.type = "subscribe"
        self.stop = True
        self.error = None
        self.ws = None
        self.thread = None
        self.auth = False
        self.api_key = ""
        self.api_secret = ""
        self.api_passphrase = ""
        self.should_print = True
        self.mongo_collection = None

        # Additional variables
        self.last_trades = []
        self.last_actions = []
        self.euros = 100
        self.coins = 0
        self.last_deal = 0
        self.selling_price = 0
        self.buying_price = 0
        self.avg_price = 0
        self.profit = 0

    def on_message(self, msg):
        if 'price' in msg and 'match' in msg["type"]:
            if 'sell' in msg["side"]:
                action = 'buy'
            elif 'buy' in msg["side"]:
                action = 'sell'

            total_trades = len(self.last_trades) + 1
            self.last_trades.insert(0, float(msg["price"]))
            self.last_actions.insert(0, msg["side"])
            total_buys = self.last_actions.count('sell') / total_trades * 100
            total_sells = self.last_actions.count('buy') / total_trades * 100
            if len(self.last_trades) > 10:
                self.last_trades = self.last_trades[:10]
                self.last_actions = self.last_actions[:10]
                if not max(self.last_trades) == self.last_trades[0]:
                    self.buy()
                elif self.last_trades[0] > self.buying_price:
                    self.sell()
            min_price = min(self.last_trades)
            max_price = max(self.last_trades)
            self.avg_price = sum(self.last_trades) / len(self.last_trades)

            # print('current', self.last_trades[0], 'buy', int(total_buys), '%', 'sell', int(total_sells), '%')

            # print('min', min_price, 'avg', int(self.avg_price), 'max', max_price, 'flux', max_price - min_price)

            # print ('sales per trade',int(total_sells),'%','buys per trade', int(total_buys),'%')
        # except: print()
    def buy(self):

        if self.euros > int(0):
            self.buying_price = self.last_trades[0]
            self.coins = self.euros / self.buying_price
            self.euros = self.euros - self.euros
            self.last_deal = 'buy'
            print("I bought", self.coins, "coins at", self.buying_price, "I now have", self.euros, "euros")

    def sell(self):

        if self.coins > 0 and self.last_deal == 'buy':
            self.selling_price = self.last_trades[0]
            self.euros = self.coins * self.selling_price
            self.profit += self.last_trades[0] - self.buying_price
            self.last_deal = 'sell'
            print("I sold", self.coins, "coins at", self.selling_price, "I made profit of ", self.profit)
            self.coins = 0


wsClient = MyWebSocketClient()
wsClient.start()
