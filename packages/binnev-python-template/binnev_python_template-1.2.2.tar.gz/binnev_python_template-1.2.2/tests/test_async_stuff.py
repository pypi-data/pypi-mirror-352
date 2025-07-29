import asyncio
import time

import pytest

N = 100


@pytest.mark.parametrize("n", range(N))
async def test_blocking(n: int):
    """These tests won't benefit from asyncio.gather"""
    time.sleep(0.1)


@pytest.mark.parametrize("n", range(N))
async def test_non_blocking(n: int):
    """These tests won't benefit from asyncio.gather"""
    await asyncio.sleep(0.1)
