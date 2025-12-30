from spade.agent import Agent
from spade.behaviour import CyclicBehaviour


class MonitorAgent(Agent):

    class MonitorBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print(f"[MONITOR] {msg.sender}: {msg.body}")

    async def setup(self):
        print(f"Monitor {self.jid} started")
        self.add_behaviour(self.MonitorBehaviour())
