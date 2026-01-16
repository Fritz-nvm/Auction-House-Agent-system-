from spade.behaviour import CyclicBehaviour
from spade.message import Message
import ast
import random
import re
import time


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

        if msg:
            # Handle registration confirmation
            if msg.metadata.get("performative") == "confirm":
                print(f"[{self.agent.jid}] ✅ Registration confirmed")
                return

            # Handle win notification (in case WinBehaviour doesn't catch it)
            if msg.metadata.get("performative") == "accept":
                self._handle_win_notification(msg)
                return

            # Handle CFP (auction call for proposals)
            if msg.metadata.get("performative") == "cfp":
                await self._handle_cfp(msg)

    async def _handle_cfp(self, msg):
        """Handle Call For Proposal (auction round)"""
        try:
            # Safely convert the string body back into a dictionary
            data = ast.literal_eval(msg.body)

            item_name = data.get("item")
            current_price = data.get("current_price")
            time_left = data.get("time_left")

            # Calculate remaining budget
            remaining_budget = self.agent.budget - self.agent.spent

            print(
                f"[{self.agent.jid}] Received CFP for {item_name} at {current_price:,}. "
                f"Time left: {time_left}s | Remaining budget: {remaining_budget:,}"
            )

            # Don't bid if the price is already at or above our remaining budget
            if current_price >= remaining_budget:
                print(
                    f"[{self.agent.jid}] ❌ Price {current_price:,} exceeds remaining budget {remaining_budget:,}"
                )
                return

            strategy = self.agent.strategy
            bid = None

            # Execute strategy logic with remaining budget consideration
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
                # Check if we can afford this bid
                if self.agent.can_afford(bid):
                    reply = Message(to=str(msg.sender).split("/")[0])
                    reply.set_metadata("performative", "propose")
                    reply.body = str(int(bid))

                    # Record bid information
                    self.agent.last_bid = int(bid)
                    self.agent.last_item = item_name

                    # Add to bid history
                    self.agent.bid_history.append(
                        {
                            "item": item_name,
                            "bid_amount": bid,
                            "current_price": current_price,
                            "remaining_budget_before": remaining_budget,
                            "remaining_budget_after": remaining_budget - bid,
                            "timestamp": time.time() if hasattr(time, "time") else None,
                        }
                    )

                    await self.send(reply)

                    # Calculate new remaining budget after this bid
                    new_remaining = remaining_budget - bid
                    print(
                        f"[{self.agent.jid}] ✅ Bid {bid:,} on {item_name} "
                        f"(Remaining after bid: {new_remaining:,})"
                    )
                else:
                    print(
                        f"[{self.agent.jid}] ❌ Cannot afford bid {bid:,} "
                        f"(Spent: {self.agent.spent:,}, "
                        f"Remaining: {remaining_budget:,}, "
                        f"Budget: {self.agent.budget:,})"
                    )

        except Exception as e:
            print(f"[{self.agent.jid}] Error processing message: {e}")
            import traceback

            traceback.print_exc()

    def _handle_win_notification(self, msg):
        """Handle win notification messages"""
        try:
            body = msg.body
            print(f"[{self.agent.jid}] 🎉 WIN NOTIFICATION: {body}")

            # Extract price and item name using regex
            price_match = re.search(r"for (\d+)", body)
            item_match = re.search(r"won (.+?) for", body)

            if price_match and item_match:
                price = int(price_match.group(1))
                item_name = item_match.group(1)

                # Record the win using agent's method
                self.agent.record_win(price, item_name)
            else:
                # Fallback parsing
                if "for" in body:
                    parts = body.split("for")
                    if len(parts) >= 2:
                        item_part = parts[0].replace("You won", "").strip()
                        price_part = parts[1].strip()
                        # Extract numbers from price
                        price_numbers = re.findall(r"\d+", price_part)
                        if price_numbers:
                            price = int(price_numbers[0])
                            self.agent.record_win(price, item_part)
        except Exception as e:
            print(f"[{self.agent.jid}] Error processing win notification: {e}")

    # --- Strategy Methods (Updated for realistic bidding) ---
    # THESE METHODS NEED TO BE INDENTED TO BE INSIDE THE CLASS!

    def aggressive(self, current_price):
        """Aggressive but realistic: 10-20% increases"""
        remaining_budget = self.agent.budget - self.agent.spent

        # Aggressive: 15-25% increase
        increase_percentage = random.uniform(0.15, 0.25)
        new_bid = int(current_price * (1 + increase_percentage))

        # Cap at remaining budget
        new_bid = min(new_bid, remaining_budget)

        # Ensure minimum increase
        min_bid = current_price + 5000
        new_bid = max(new_bid, min_bid)

        return new_bid if new_bid <= remaining_budget else None

    def conservative(self, current_price):
        """Conservative: small, predictable increases"""
        remaining_budget = self.agent.budget - self.agent.spent

        # Conservative: 5-10% increase
        increase_percentage = random.uniform(0.05, 0.10)
        new_bid = int(current_price * (1 + increase_percentage))

        # Cap at remaining budget
        new_bid = min(new_bid, remaining_budget)

        # Ensure minimum increase
        min_bid = current_price + 2000
        new_bid = max(new_bid, min_bid)

        return new_bid if new_bid <= remaining_budget else None

    def random_strategy(self, current_price):
        """Random but bounded: 0-20% increases"""
        remaining_budget = self.agent.budget - self.agent.spent

        # Random chance to bid (60%)
        if random.random() > 0.6:
            return None

        # Random increase between 0% and 20%
        increase_percentage = random.uniform(0, 0.20)
        new_bid = int(current_price * (1 + increase_percentage))

        # Cap at remaining budget
        new_bid = min(new_bid, remaining_budget)

        # Ensure minimum increase of 1%
        min_bid = int(current_price * 1.01)
        new_bid = max(new_bid, min_bid)

        return new_bid if new_bid <= remaining_budget else None

    def sniper(self, current_price, time_left):
        """Sniper: waits until last moment, then bids aggressively"""
        if time_left <= 10:
            remaining_budget = self.agent.budget - self.agent.spent

            # Sniper: 20-30% increase in last 10 seconds
            increase_percentage = random.uniform(0.20, 0.30)
            new_bid = int(current_price * (1 + increase_percentage))

            # Cap at remaining budget
            new_bid = min(new_bid, remaining_budget)

            # Ensure minimum increase
            min_bid = current_price + 6000
            new_bid = max(new_bid, min_bid)

            return new_bid if new_bid <= remaining_budget else None
        return None
