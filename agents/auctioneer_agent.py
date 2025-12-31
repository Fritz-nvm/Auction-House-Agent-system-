from spade.agent import Agent
from behaviours.auctioneer_behaviour import AuctionBehaviour


class AuctioneerAgent(Agent):
    async def setup(self):
        print(f"Auctioneer {self.jid} started")

        self.current_price = 100
        self.auction_time = 10
        self.bids = {}

        self.add_behaviour(AuctionBehaviour())
