from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import random
import asyncio


class BidderAgent(Agent):

    class BiddingBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg and msg.metadata.get("performative") == "cfp":
                current_price = int(msg.body)

                bid = self.agent.generate_bid(current_price)
                if bid is not None:
                    reply = Message(to=str(msg.sender))
                    reply.set_metadata("performative", "propose")
                    reply.body = str(bid)
                    await self.send(reply)

                    print(f"{self.agent.jid} bids {bid}")

            elif msg and msg.metadata.get("performative") == "accept":
                print(f"{self.agent.jid} received WIN message: {msg.body}")
                self.kill()

    def generate_bid(self, current_price):
        if self.strategy == "aggressive":
            return current_price + 20

        elif self.strategy == "conservative":
            if current_price + 5 <= self.budget:
                return current_price + 5
            return None

        elif self.strategy == "random":
            return random.randint(current_price, self.budget)

        elif self.strategy == "sniper":
            asyncio.create_task(asyncio.sleep(8))
            return current_price + 30

    async def setup(self):
        print(f"Bidder {self.jid} started with {self.strategy} strategy")
        self.add_behaviour(self.BiddingBehaviour())
