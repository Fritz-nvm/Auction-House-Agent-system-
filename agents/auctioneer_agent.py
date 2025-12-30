from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
import time


class AuctioneerAgent(Agent):

    class AuctionBehaviour(CyclicBehaviour):
        async def run(self):
            # Announce auction (CFP)
            cfp = Message(to="bidders@localhost")
            cfp.set_metadata("performative", "cfp")
            cfp.body = str(self.agent.current_price)

            await self.send(cfp)
            print("Auctioneer: CFP sent")

            start_time = time.time()
            self.agent.bids = {}

            # Collect bids for auction duration
            while time.time() - start_time < self.agent.auction_time:
                msg = await self.receive(timeout=1)
                if msg and msg.metadata.get("performative") == "propose":
                    bid_value = int(msg.body)
                    self.agent.bids[str(msg.sender)] = bid_value
                    print(f"Received bid {bid_value} from {msg.sender}")

            # Decide winner
            if self.agent.bids:
                winner = max(self.agent.bids, key=self.agent.bids.get)
                winning_bid = self.agent.bids[winner]

                result = Message(to=winner)
                result.set_metadata("performative", "accept")
                result.body = f"You won with bid {winning_bid}"
                await self.send(result)

                print(f"Winner: {winner} with {winning_bid}")
            else:
                print("No bids received")

            await asyncio.sleep(5)
            self.kill()

    async def setup(self):
        print(f"Auctioneer {self.jid} started")
        self.current_price = 100
        self.auction_time = 10
        self.add_behaviour(self.AuctionBehaviour())
