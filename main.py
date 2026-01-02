import asyncio
from agents.auctioneer_agent import AuctioneerAgent
from agents.bidder_agent import BidderAgent
from agents.monitor_agent import MonitorAgent


async def main():
    print("Starting Auction House Multi-Agent System...\n")

    # =========================
    # Create Auctioneer Agent
    # =========================
    auctioneer = AuctioneerAgent("auctioneer@localhost", "password")

    auctioneer.item = {
        "id": 1,
        "name": "Gaming Laptop",
        "description": "16GB RAM, RTX 3060",
        "current_price": 200000,
    }

    # Auction configuration
    auctioneer.start_price = 100000
    auctioneer.auction_time = 10  # seconds

    # =========================
    # Create Bidder Agents
    # =========================
    bidders = [
        BidderAgent(
            "bidder1@localhost", "password", strategy="aggressive", budget=500000
        ),
        BidderAgent(
            "bidder2@localhost", "password", strategy="conservative", budget=200000
        ),
        BidderAgent("bidder3@localhost", "password", strategy="random", budget=400000),
        BidderAgent("bidder4@localhost", "password", strategy="sniper", budget=600000),
    ]

    # List of bidder JIDs (used by auctioneer)
    auctioneer.bidders = [b.jid for b in bidders]

    # =========================
    # Create Monitor Agent
    # =========================
    monitor = MonitorAgent("monitor@localhost", "password")

    # =========================
    # Start All Agents
    # =========================

    for bidder in bidders:
        await bidder.start(auto_register=True)

    await asyncio.sleep(1)

    await auctioneer.start(auto_register=True)
    await monitor.start(auto_register=True)

    print("\nAll agents started. Auction running...\n")

    # =========================
    # Keep System Alive
    # =========================
    # Auction runs inside AuctionBehaviour
    await asyncio.sleep(auctioneer.auction_time + 5)

    # =========================
    # Stop All Agents
    # =========================
    print("\nStopping agents...\n")

    for bidder in bidders:
        await bidder.stop()

    await auctioneer.stop()
    await monitor.stop()

    print("Auction system terminated.")


if __name__ == "__main__":
    asyncio.run(main())
