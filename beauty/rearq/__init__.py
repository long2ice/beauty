import asyncio

from rearq.worker import TimerWorker, Worker

from beauty.rearq.tasks import rearq


async def start():
    w = Worker(
        rearq,
    )
    t = TimerWorker(rearq)
    await asyncio.gather(w.run(), t.run())
