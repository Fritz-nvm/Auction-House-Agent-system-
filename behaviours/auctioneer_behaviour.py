from spade.behaviour import CyclicBehaviour
from spade.message import Message
import time
import asyncio


class AuctionBehaviour(CyclicBehaviour):
    async def run(self):
        # support list of items provided by main.py, fallback to single item (legacy)
        items = getattr(self.agent, "items", None)
        if items is None:
            if hasattr(self.agent, "item"):
                items = [self.agent.item]
            else:
                print("No items configured for auctioneer. Stopping behaviour.")
                self.kill()
                return

        # initialize current item index
        if not hasattr(self.agent, "current_item_index"):
            self.agent.current_item_index = 0

        # if all items processed, stop
        if self.agent.current_item_index >= len(items):
            print("All auctions completed.")
            self.kill()
            return

        item = items[self.agent.current_item_index]
        now = time.time()

        # First run for this item: announce auction
        if not hasattr(self.agent, "auction_started") or not self.agent.auction_started:
            self.agent.auction_started = True
            self.agent.auction_end_time = now + self.agent.auction_time
            self.agent.highest_bidder = None

            print("\n=== AUCTION STARTED ===")
            print(f"Item: {item.get('name')}")
            print(f"Description: {item.get('description', '')}")
            print(f"Starting Price: {item.get('current_price')}\n")

        # End auction if time expired for current item
        if now >= self.agent.auction_end_time:
            print("\n=== AUCTION ENDED ===")
            if self.agent.highest_bidder:
                print(f"Item: {item.get('name')}")
                print(f"Final Price: {item.get('current_price')}")
                print(f"Winner: {self.agent.highest_bidder}")

                win_msg = Message(to=self.agent.highest_bidder)
                win_msg.set_metadata("performative", "accept")
                win_msg.body = (
                    f"You won {item.get('name')} for {item.get('current_price')}"
                )
                await self.send(win_msg)
            else:
                print("No bids received.")

            # advance to next item
            self.agent.current_item_index += 1
            # reset per-item flags
            self.agent.auction_started = False

            if self.agent.current_item_index >= len(items):
                print("No more items. Stopping auction behaviour.")
                await self.agent.stop()
                self.kill()
                return

            return

        # New auction round (CFP) for current item
        time_left = int(self.agent.auction_end_time - now)

        for bidder in self.agent.bidders:
            clean_jid = str(bidder).split("/")[0]
            msg = Message(to=clean_jid)
            msg.set_metadata("performative", "cfp")
            msg.body = str(
                {
                    "item": item.get("name"),
                    "current_price": item.get("current_price"),
                    "time_left": time_left,
                }
            )
            await self.send(msg)

        print(
            f"[Auctioneer] Round | "
            f"Item: {item.get('name')} | "
            f"Price: {item.get('current_price')} | "
            f"Time left: {time_left}s"
        )

        # Inside AuctionBehaviour
        round_end = time.time() + self.agent.round_duration
        while time.time() < round_end:
            # Use a very short timeout to catch all messages in the queue rapidly
            msg = await self.receive(timeout=0.1)
            if msg:
                if msg.metadata.get("performative") == "propose":
                    try:
                        bid = int(float(msg.body))  # float handles cases like "200.0"
                        if bid > item.get("current_price", 0):
                            item["current_price"] = bid
                            self.agent.highest_bidder = str(msg.sender)
                            print(f"New highest bid: {bid} by {msg.sender}")
                    except Exception as e:
                        print(f"Error parsing bid: {e}")

        # Pause before next round
        await asyncio.sleep(self.agent.round_pause)
