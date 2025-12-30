from spade.behaviour import CyclicBehaviour


class MonitoringBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            print(f"[MONITOR] {msg.sender} → {msg.body}")
