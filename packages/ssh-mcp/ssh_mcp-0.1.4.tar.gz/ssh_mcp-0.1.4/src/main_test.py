import asyncio
import json
import os

from mcpssh.main import run_query_script

async def amain():
    os.environ["PASSMAN_TOKEN"] = "xC0msc3tXyDUJvdS9DK2IvhubRjqMbC2FrDcmF-eQ_Y="
    res = await run_query_script(
        'devinteg',
        'ls -la',
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(amain())
