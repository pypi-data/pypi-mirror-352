# SPDX-FileCopyrightText: 2025 Elektroline a.s.
#
# SPDX-License-Identifier: MIT

"""RPC Exchange usage and implementation utility."""

from __future__ import annotations

import abc
import collections.abc

from .rpcmethod import RpcMethodAccess, RpcMethodDesc
from .shvbase import SHVBase
from .value import SHVMapType, SHVType, is_shvmap


class RpcExchange:
    """RPC Exchange connection over :class:`SimpleBase`."""

    BLOCK_SIZE: int = 1024
    """The block size signaled as ready to be received.

    This can control how big and thus how many messages will be exchanged. It
    should be something reasonable, not that small (causing too many messages to
    be generated) as well as not too big (causing huge messages which is
    discouraged in SHV).
    """

    def __init__(
        self,
        client: SHVBase,
        path: str,
        idle_timeout: int = 30,
    ) -> None:
        self.client: SHVBase = client
        """The client used to access the RPC file."""
        self._path = path
        self._counter: int = 0
        self._to_receive: int = 0
        self._to_send: int = 0
        self._wbuf: bytearray = bytearray()
        self._rbuf: bytearray = bytearray()

    async def _exchange(self) -> None:
        """Perform exchange by sending wbuf and adding data to rbuf."""
        # TODO wait for signal in case we can't do anything instead of polling
        param: dict[int, SHVType] = {0: self._counter, 1: self.BLOCK_SIZE}
        if self._to_receive > 0:
            param[3] = self._wbuf[self._to_receive :]
            self._wbuf = self._wbuf[: self._to_receive]
        data = await self.client.call(self._path, "exchange", param)
        if not isinstance(data, bytes):
            raise Exception("Invalid response for exchange method received")
        self._rbuf += data
        self._counter += 1

    def _rbuf_take(self, n: int | None = None) -> bytes:
        result = self._rbuf[:n]
        del self._rbuf[:n]
        return result

    async def read(self, n: int = -1) -> bytes:
        """Read bytes from the exchange stream.

        This also sends any bytes that were previously written.

        :param n: Number of bytes to read. Zero or less is interpreted as
          unconstrained read (read everything until nothing is available to
          read at the moment).
        :return: Received bytes.
        """
        if n > 0:
            while len(self._rbuf) < n:
                await self._exchange()
        else:
            while True:
                prev_size = len(self._rbuf)
                await self._exchange()
                if prev_size == len(self._rbuf):
                    break
        return self._rbuf_take(n if n > 0 else None)

    async def readexactly(self, n: int) -> bytes:
        """Read exactly given number of bytes.

        See :meth:`read` for other implications on using this method.

        :param n: Number of bytes to be read.
        :return: Received bytes.
        """
        while len(self._rbuf) < n:
            await self._exchange()
        return self._rbuf_take(n)

    async def readuntil(self, separator: bytes = b"\n") -> bytes:
        """Read until given byte sequence is received.

        See :meth:`read` for other implications on using this method.

        :param separator: The separator to be located in the sequence.
        :return: Received bytes before separator and separator.
        """
        while separator not in self._rbuf:
            await self._exchange()
        return self._rbuf_take(self._rbuf.find(separator) + len(separator))

    def write(self, data: bytes) -> None:
        """Write bytes to the exchange stream.

        :param data: Data to be written to the exchange stream.
        """
        self._wbuf += data

    async def drain(self) -> None:
        """Drain all written bytes to the exchange stream.

        RPC Exchange is designed to do read and write with a single operation
        where reading is required to be performed before write is allowed. This
        means that this function must buffer read data. In most cases it is
        better to use :meth:`read`, :meth:`readexactly`, or :meth:`readuntil`
        directly instead of this one.
        """
        while self._wbuf:
            await self._exchange()

    async def options(self) -> SHVMapType:
        """Get the current options."""
        result = await self.client.call(self._path, "options")
        return result if is_shvmap(result) else {}

    async def set_options(self, options: SHVMapType) -> None:
        """Set the provided options."""
        await self.client.call(self._path, "setOptions", options)

    async def close(self) -> None:
        """Close the exchange stream."""
        await self.client.call(self._path, "close")

    @classmethod
    async def new(
        cls, client: SHVBase, path: str, options: SHVMapType | None = None
    ) -> RpcExchange:
        """Establish a new RPC Exchange connection."""
        token = await client.call(path, "newExchange", options)
        if not isinstance(token, str):
            raise Exception("Returned token of invalid type.")
        # if options and "idleTimeOut" in options: TODO
        return cls(client, f"{path}/{token}")


class RpcExchangeServer:
    """The server side for the RPC Exchange."""

    class Connection(abc.ABC):
        """The RPC exchange server connection."""

        def __init__(self, server: RpcExchangeServer) -> None:
            self.server = server
            """The reference to the server this connection belongs to."""

        @abc.abstractmethod
        async def exchange(self, data: bytes) -> bytes:
            """Perform the exchange operation."""

    def __init__(self) -> None:
        self._connections: dict[str, RpcExchangeServer.Connection] = {}

    def _ls(self, node: str) -> collections.abc.Iterator[str]:
        pass

    def dir(self, node: str) -> collections.abc.Iterator[RpcMethodDesc]:
        pass

    def method_call(
        self,
        name: str,
        param: SHVType,
        access_level: RpcMethodAccess,
    ) -> SHVType:
        pass
