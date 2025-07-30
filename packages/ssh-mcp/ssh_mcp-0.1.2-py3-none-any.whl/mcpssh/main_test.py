import asyncio
import json

from main import run_query_script

async def amain():
    res = await run_query_script(
        '172.31.241.185',
        'ls -la',
        username='root',
        port=22,
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(amain())
