import asyncio
from agents.auctioneer_agent import AuctioneerAgent
from agents.bidder_agent import BidderAgent
from agents.monitor_agent import MonitorAgent


async def main():
    print("Starting Auction House Multi-Agent System...\n")

    #  Initialize Bidders first
    bidders = [
        BidderAgent(
            "aggressive_agent@localhost",
            "password",
            strategy="aggressive",
            budget=500000,
        ),
        BidderAgent(
            "conservative_agent@localhost",
            "password",
            strategy="conservative",
            budget=300000,
        ),
        BidderAgent(
            "randon_agent@localhost", "password", strategy="random", budget=400000
        ),
        BidderAgent(
            "sniper_agent@localhost", "password", strategy="sniper", budget=600000
        ),
    ]

    # Initialize Auctioneer
    auctioneer = AuctioneerAgent("auctioneer@localhost", "password")

    # initialize monitor agent
    monitor = MonitorAgent("monitor@localhost", "password")

    auctioneer.items = [
        {
            "id": 1,
            "name": "Custom Gaming Desktop",
            "description": "Intel i9, RTX 4090, 64GB RAM, Liquid Cooled",
            "current_price": 350000,
        },
        {
            "id": 2,
            "name": "Ultra-Wide Curved Monitor",
            "description": "49-inch OLED, 240Hz Refresh Rate, 1ms Response",
            "current_price": 120000,
        },
        {
            "id": 3,
            "name": "Mechanical Keyboard",
            "description": "Hot-swappable switches, Aluminum Case, RGB",
            "current_price": 15000,
        },
        {
            "id": 4,
            "name": "Vintage Film Camera",
            "description": "35mm SLR with 50mm f/1.8 Lens, Excellent Condition",
            "current_price": 45000,
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

    # Assign unique ports manually
    for i, bidder in enumerate(bidders):
        bidder.web_port = 10001 + i  # Ports 10001, 10002, 10003, 10004

    auctioneer = AuctioneerAgent("auctioneer@localhost", "password")
    auctioneer.web_port = 10000  # Auctioneer on its own port

    monitor = MonitorAgent("monitor@localhost", "password")
    monitor.web_port = 10005

    print("\nStopping agents...")
    for bidder in bidders:
        await bidder.stop()
    await auctioneer.stop()
    await monitor.stop()
    print("Auction system terminated.")


if __name__ == "__main__":
    asyncio.run(main())
