from spade.agent import Agent
from behaviours.bidding_behaviour import BiddingBehaviour
from spade.template import Template


class BidderAgent(Agent):
    def __init__(self, jid, password, strategy, budget):
        super().__init__(jid, password)
        self.strategy = strategy
        self.budget = budget

    async def setup(self):
        print(
            f"Bidder {self.jid} started | "
            f"Strategy: {self.strategy} | "
            f"Budget: {self.budget}"
        )

        template = Template()
        template.set_metadata("performative", "cfp")
        self.add_behaviour(BiddingBehaviour(), template)
