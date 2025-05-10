import asyncio

try:
    import uvloop
except ImportError:
    uvloop = None  # type: ignore


def activate_uvloop() -> None:
    if uvloop:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
