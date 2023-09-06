import asyncio
import json

from aiosseclient import aiosseclient

wiki = "enwiki"


def on_edit(title):
    print(title)


async def main():
    async for event in aiosseclient("https://stream.wikimedia.org/v2/stream/recentchange"):
        if event.event == "message":
            try:
                change = json.loads(event.data)
            except ValueError:
                continue
            if change["wiki"] == wiki:
                print(change)
                on_edit(change["title"])


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
