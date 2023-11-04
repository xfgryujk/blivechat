# -*- coding: utf-8 -*-
import asyncio
import sys

import blcsdk


async def main():
    print('hello world!', blcsdk.__version__)
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
