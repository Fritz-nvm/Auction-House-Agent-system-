import asyncio
from agents.auctioneer_agent import AuctioneerAgent
from agents.bidder_agent import BidderAgent
from agents.monitor_agent import MonitorAgent


async def main():
    print("Starting Auction House Multi-Agent System...\n")

    #  Initialize Bidders first
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

    # Initialize Auctioneer
    auctioneer = AuctioneerAgent("auctioneer@localhost", "password")

    # initialize monitor agent
    monitor = MonitorAgent("monitor@localhost", "password")

    auctioneer.items = [
        {
            "id": 1,
            "name": "Gaming Laptop",
            "description": "16GB RAM, RTX 3060",
            "current_price": 200000,
        },
        {
            "id": 2,
            "name": "Smartphone",
            "description": "Flagship model",
            "current_price": 80000,
        },
    ]

    # Store preconfigured bidders (for backup if registration fails)
    auctioneer.preconfigured_bidders = [str(b.jid).split("/")[0] for b in bidders]

    auctioneer.bidders = [str(b.jid) for b in bidders]

    await asyncio.sleep(0.5)

    auctioneer.auction_time = 30  # Total time per item
    auctioneer.round_duration = 5  # Time to wait for bids per round
    auctioneer.round_pause = 1  # Time between rounds

    # Start auctioneer FIRST
    print("Starting auctioneer first...")
    await auctioneer.start()
    await asyncio.sleep(2)  # Give auctioneer time to set up behaviors

    # Then start bidders
    print("Starting bidders...")
    for bidder in bidders:
        await bidder.start()
        await asyncio.sleep(0.5)  # Stagger connections

    # Start monitor
    print("Starting monitor...")
    await monitor.start()

    print("\n=== System Ready ===\n")

    while auctioneer.is_alive():
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break

    print("\nStopping agents...")
    for bidder in bidders:
        await bidder.stop()
    await auctioneer.stop()
    await monitor.stop()
    print("Auction system terminated.")


if __name__ == "__main__":
    asyncio.run(main())
