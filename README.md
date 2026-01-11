# 📝 Auction House Multi-Agent System (SPADE)

A distributed auction simulation built using the **SPADE** (Smart Python Agent Development Environment) framework. This project simulates an English Auction where an **Auctioneer** coordinates multiple **Bidders** with varying strategies (Aggressive, Conservative, Sniper, and Random).

## 🚀 Features

- **Auctioneer Agent**: Manages item listings, rounds, and bid collection.
- **Bidder Agents**: Four unique automated strategies:
- `Aggressive`: Large outbids to intimidate others.
- `Conservative`: Small, incremental price increases.
- `Sniper`: Waits until the last 10 seconds to bid.
- `Random`: Bids a random amount within its budget.

- **Monitor Agent**: Observes auction traffic and status.
- **XMPP Integration**: Real-time communication via `ejabberd`.

---

## 🛠 Prerequisites

Before running the project, ensure you have the following installed:

- **Python 3.8+**
- **ejabberd** (XMPP Server)

### 1. Configure ejabberd

Ensure your XMPP server is running on `localhost`. You need to register the agent accounts:

```bash
# install ejabberd on cmd
pip install ejabbberd
# Register the Auctioneer
sudo ejabberdctl register auctioneer localhost password

# Register the Bidders
sudo ejabberdctl register bidder1 localhost password
sudo ejabberdctl register bidder2 localhost password
sudo ejabberdctl register bidder3 localhost password
sudo ejabberdctl register bidder4 localhost password

# Register the Monitor
sudo ejabberdctl register monitor localhost password

```

---

## 📥 Installation

1. **Clone the repository:**

```bash
git clone https://github.com/fritz-nvm/Auction-House-Agent-system.git
cd Auction-House-Agent-system

```

2. **Create and activate a virtual environment:**

```bash
python3 -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate

```

3. **Install dependencies:**

```bash
pip install -r requiements.txt

```

---

## 🏃 Running the Simulation

1. **Start the ejabberd server:**

```bash
sudo ejabberdctl start

```

2. **Run the system:**

```bash
python main.py # for windows
python3 main.py # for linux

```

---

## 📂 Project Structure

```text
.
├── agents/
│   ├── auctioneer_agent.py   # Auctioneer logic & behaviors
│   ├── bidder_agent.py       # Bidder logic & strategy methods
│   └── monitor_agent.py      # Monitoring & logging
├── main.py                   # Entry point (Agent initialization)
└── README.md

```

---

## 🔍 Debugging & Logs

- **Agent Output**: Real-time bidding logs are printed to the console.
- **XMPP Logs**: Check the server status with `sudo ejabberdctl status`.
- **System Logs**: View server logs at `/var/log/ejabberd/ejabberd.log` (Linux).

## 🛑 Stopping the System

The simulation will automatically terminate once all items are auctioned. To force stop, use `Ctrl+C`. The script is configured to gracefully shut down all agent sessions upon exit.
