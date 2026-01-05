from spade.agent import Agent
from behaviours.auctioneer_behaviour import AuctionBehaviour
from behaviours.registration_hehaviour import RegistrationBehaviour


class AuctioneerAgent(Agent):
    async def setup(self):
        self.presence.set_available()
        print(f"Auctioneer {self.jid} started")

        self.bidders = []

        self.auction_time = 20  # total auction duration (seconds)
        self.round_duration = 5  # bidding window per round
        self.round_pause = 1  # pause between rounds
        self.bidders = []  # Make sure this is initialized here
        self.preconfigured_bidders = []  # Store bidders from main.py

        self.highest_bidder = None
        self.auction_started = False

        self.add_behaviour(RegistrationBehaviour())
        self.add_behaviour(AuctionBehaviour())
