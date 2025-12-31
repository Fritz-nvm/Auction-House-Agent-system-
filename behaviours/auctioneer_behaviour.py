from spade.behaviour import OneShotBehaviour
from spade.message import Message
import time


class AuctionBehaviour(OneShotBehaviour):
    async def run(self):
        item = self.agent.item

        print("\n=== AUCTION STARTED ===")
        print(f"Item: {item['name']}")
        print(f"Description: {item['description']}")
        print(f"Starting Price: {item['current_price']}\n")

        # Broadcast item to bidders
        for bidder in self.agent.bidders:
            msg = Message(to=bidder)
            msg.set_metadata("performative", "cfp")
            msg.body = f"ITEM:{item['name']};" f"PRICE:{item['current_price']}"
            await self.send(msg)

        start_time = time.time()
        highest_bidder = None

        while time.time() - start_time < self.agent.auction_time:
            msg = await self.receive(timeout=1)
            if msg and msg.metadata.get("performative") == "propose":
                bid = int(msg.body)

                if bid > item["current_price"]:
                    item["current_price"] = bid
                    highest_bidder = str(msg.sender)
                    print(f"New highest bid: {bid} " f"by {msg.sender}")

        print("\n=== AUCTION ENDED ===")
        if highest_bidder:
            print(f"Item: {item['name']}")
            print(f"Final Price: {item['current_price']}")
            print(f"Winner: {highest_bidder}")

            win_msg = Message(to=highest_bidder)
            win_msg.set_metadata("performative", "accept")
            win_msg.body = f"You won {item['name']} " f"for {item['current_price']}"
            await self.send(win_msg)
        else:
            print("No bids received.")
