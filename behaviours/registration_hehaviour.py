from spade.behaviour import CyclicBehaviour
from spade.message import Message


class RegistrationBehaviour(CyclicBehaviour):
    """Handle bidder registration messages"""

    async def run(self):
        # Check for registration messages
        msg = await self.receive(timeout=1)
        if msg:
            if msg.metadata.get("performative") == "register":
                bidder_jid = str(msg.sender).split("/")[0]  # Get base JID
                if bidder_jid not in self.agent.bidders:
                    self.agent.bidders.append(bidder_jid)
                    print(f"[Auctioneer] Registered bidder: {bidder_jid}")

                    # Send confirmation
                    confirm = Message(to=bidder_jid)
                    confirm.set_metadata("performative", "confirm")
                    confirm.body = "Registration confirmed"
                    await self.send(confirm)
