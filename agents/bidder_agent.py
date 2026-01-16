from spade.agent import Agent
from behaviours.bidding_behaviour import BiddingBehaviour
from behaviours.win_behaviour import WinBehaviour
from spade.template import Template


class BidderAgent(Agent):
    def __init__(self, jid, password, strategy, budget):
        super().__init__(jid, password)
        self.strategy = strategy
        self.budget = budget

        self.spent = 0  # Track money spent
        self.wins = 0  # Track auctions won
        self.bid_history = []  # Track all bids
        self.last_bid = 0  # Track last bid amount
        self.last_item = ""  # Track last item bid on

    def can_afford(self, amount):
        """Check if agent has enough budget remaining"""
        return self.spent + amount <= self.budget

    def record_win(self, amount, item_name):
        """Record a win and update spending"""
        self.spent += amount
        self.wins += 1
        print(
            f"💰 [{self.jid}] WON {item_name} for {amount} | "
            f"Total spent: {self.spent}/{self.budget}"
        )

    async def setup(self):
        port = getattr(self, "web_port", 10000)
        self.web.start(hostname="127.0.0.1", port=port)
        self.presence.set_available()
        print(f"Bidder {self.jid} started | " f"Strategy: {self.strategy} | ")

        self.add_behaviour(BiddingBehaviour())
        self.add_behaviour(WinBehaviour())
