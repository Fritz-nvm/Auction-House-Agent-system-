from spade.behaviour import CyclicBehaviour
from spade.message import Message
import ast
import random


class BiddingBehaviour(CyclicBehaviour):

    async def on_start(self):
        print(f"!!! BEHAVIOR STARTED FOR {self.agent.jid} !!!")
        register_msg = Message(to="auctioneer@localhost")
        register_msg.set_metadata("performative", "register")
        register_msg.body = str(self.agent.jid)
        await self.send(register_msg)
        print(f"[{self.agent.jid}] Sent registration to auctioneer")

    async def run(self):
        # We wait for a message from the auctioneer
        msg = await self.receive(timeout=0.1)

        if msg and msg.metadata.get("performative") == "cfp":

            # print(f"[{self.agent.jid}] RECEIVED MESSAGE!")
            # print(f"    From: {msg.sender}")
            # print(f"    Performative: {msg.metadata.get('performative')}")
            # print(f"    Body: {msg.body}")
            try:
                # Safely convert the string body back into a dictionary
                data = ast.literal_eval(msg.body)

                item_name = data.get("item")
                current_price = data.get("current_price")
                time_left = data.get("time_left")

                print(
                    f"[{self.agent.jid}] Received CFP for {item_name} at {current_price}. Time left: {time_left}s"
                )

                # Don't bid if the price is already at or above our budget
                if current_price >= self.agent.budget:
                    return

                strategy = self.agent.strategy
                bid = None

                # Execute strategy logic
                if strategy == "aggressive":
                    bid = self.aggressive(current_price)
                elif strategy == "conservative":
                    bid = self.conservative(current_price)
                elif strategy == "random":
                    bid = self.random_strategy(current_price)
                elif strategy == "sniper":
                    bid = self.sniper(current_price, time_left)

                # Send bid if one was generated and it's higher than current price
                if bid and bid > current_price:
                    reply = Message(to=str(msg.sender).split("/")[0])
                    reply.set_metadata("performative", "propose")
                    reply.body = str(int(bid))

                    # record last bid and item so WinBehaviour can reconcile if needed
                    self.agent.last_bid = int(bid)
                    self.agent.last_item = item_name

                    await self.send(reply)
                    print(f"[{self.agent.jid}] Submitted bid: {bid}")

            except Exception as e:
                print(f"[{self.agent.jid}] Error processing message: {e}")

    # --- Strategy Methods ---
    def aggressive(self, current_price):
        # Always outbid by a large margin (200k)
        new_bid = current_price + 5000
        return new_bid if new_bid <= self.agent.budget else self.agent.budget

    def conservative(self, current_price):
        # Small increments (50k)
        new_bid = current_price + 2000
        return new_bid if new_bid <= self.agent.budget else None

    def random_strategy(self, current_price):
        if self.agent.budget > current_price + 5000:
            return random.randint(int(current_price + 1000), int(self.agent.budget))
        return None

    def sniper(self, current_price, time_left):
        if time_left <= 10:
            new_bid = current_price + 6000
            return new_bid if new_bid <= self.agent.budget else self.agent.budget
        return None
