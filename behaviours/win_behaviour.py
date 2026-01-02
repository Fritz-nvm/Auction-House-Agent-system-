from spade.behaviour import OneShotBehaviour


class WinBehaviour(OneShotBehaviour):
    async def run(self):
        msg = await self.receive(timeout=5)
        if msg:
            print(f"\n🏆 {self.agent.jid} WON THE AUCTION!")
            print(msg.body)
