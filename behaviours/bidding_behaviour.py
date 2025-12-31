from spade.behaviour import CyclicBehaviour
from spade.message import Message
import random

import time


class BiddingBehaviour(CyclicBehaviour):

    async def run(self):
        msg = await self.receive(timeout=5)

        if not msg or msg.metadata.get("performative") != "cfp":
            return

        data = eval(msg.body)

        item = data["item"]
        current_price = data["current_price"]
        time_left = data["time_left"]

        print(
            f"{self.agent.jid} received CFP\n"
            f"  Item: {item['name']}\n"
            f"  Current Price: {current_price}\n"
            f"  Time Left: {time_left}s"
        )

        strategy = self.agent.strategy

        if strategy == "aggressive":
            bid = self.aggressive(current_price)

        elif strategy == "conservative":
            bid = self.conservative(current_price)

        elif strategy == "random":
            bid = self.random_strategy(current_price)

        elif strategy == "sniper":
            bid = self.sniper(current_price, time_left)

        else:
            bid = None

        if bid is None:
            return

        reply = Message(to=str(msg.sender))
        reply.set_metadata("performative", "propose")
        reply.body = str(bid)

        await self.send(reply)
        print(f"{self.agent.jid} ({strategy}) bids {bid}")

    # ===============================
    # Strategy implementations
    # ===============================

    def aggressive(self, current_price):
        bid = current_price + 200_000
        return min(bid, self.agent.budget)

    def conservative(self, current_price):
        bid = current_price + 80_000
        return bid if bid <= self.agent.budget else None

    def random_strategy(self, current_price):
        return random.randint(current_price, self.agent.budget)

    def sniper(self, current_price, time_left):
        if time_left > 2:
            return None
        bid = current_price + 150_000
        return min(bid, self.agent.budget)
