import sys
import asyncio
import unittest
from unittest import IsolatedAsyncioTestCase
import aiobastion
import random
import tests
from aiobastion import CyberarkAPIException, CyberarkException, AiobastionException


class TestSystemHealth(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.vault = aiobastion.EPV(tests.CONFIG)
        await self.vault.login()

    async def asyncTearDown(self):
        await self.vault.logoff()

    async def test_summary(self):
        summary = await self.vault.system_health.summary()
        self.assertIsInstance(summary, list)
        print(summary)

    async def test_details(self):
        # PVWA, SessionManagement, CPM, PTA or AIM
        summary = await self.vault.system_health.details("PVWA")
        self.assertIsInstance(summary, list)

        summary = await self.vault.system_health.details("SessionManagement")
        self.assertIsInstance(summary, list)

        summary = await self.vault.system_health.details("CPM")
        self.assertIsInstance(summary, list)

        summary = await self.vault.system_health.details("AIM")
        self.assertIsInstance(summary, list)

if __name__ == '__main__':
    if sys.platform == 'win32':
        # Turned out, using WindowsSelectorEventLoop has functionality issues such as:
        #     Can't support more than 512 sockets
        #     Can't use pipe
        #     Can't use subprocesses
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    unittest.main()

