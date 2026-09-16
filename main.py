import asyncio
import aiohttp
import functools
import time
from typing import Callable, Any


def async_timed():
    def wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            print(f"Executing {func.__name__} with args {args} {kwargs}")
            start = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                total = time.perf_counter() - start
                print(f"Func {func.__name__} finished in {total:.4f} secs")
        return wrapped
    return wrapper


URL = "https://www.esa.int/var/esa/storage/images/esa_multimedia/images/2025/04/solar_orbiter_s_widest_high-res_view_of_the_sun/26672644-4-eng-GB/Solar_Orbiter_s_widest_high-res_view_of_the_Sun.jpg"


@async_timed()
async def download_image(session: aiohttp.ClientSession, url: str) -> tuple[int, float]:
    start = time.perf_counter()
    async with session.get(url) as response:
        data = await response.read()
    elapsed = time.perf_counter() - start
    size = len(data)
    speed_mbps = (size * 8) / elapsed / 1_000_000
    speed_mb_s = (size / 1024 / 1024) / elapsed
    print(
        f"Downloaded {size} bytes in {elapsed:.4f} secs | "
        f"{speed_mb_s:.2f} MB/s | {speed_mbps:.2f} Mbit/s"
    )
    return size, elapsed


async def main():
    async with aiohttp.ClientSession() as session:
        start = time.perf_counter()
        tasks = [download_image(session, URL) for _ in range(10)]
        results = await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start

        total_bytes = sum(size for size, _ in results)
        total_mb = total_bytes / 1024 / 1024

        print(f"Sizes: {[s for s, _ in results]}")
        print(f"Total bytes: {total_bytes} ({total_mb:.3f} MB)")
        print(f"Total concurrent: {total_time:.4f} secs")
        print(f"Average speed: {total_mb / total_time:.2f} MB/s "
              f"({total_bytes * 8 / total_time / 1_000_000:.2f} Mbit/s)")


if __name__ == "__main__":
    asyncio.run(main())