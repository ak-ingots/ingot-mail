"""
A server of SMTP for the tests, on asyncio: it keeps what it takes, and
replies what a test tells it to, a refusal or nothing at all.
"""

import asyncio
import base64
import dataclasses
import email.parser
import email.policy
import typing as t

from ingot_mail.mail import Mail


@dataclasses.dataclass
class SmtpServer:
    """``replies`` by command, ``RCPT`` by address too: ``"RCPT bo@b.c"``."""

    replies: dict[str, str] = dataclasses.field(default_factory=dict)
    is_silent: bool = False
    is_auth: bool = False
    logins: list[str] = dataclasses.field(default_factory=list)
    messages: list[bytes] = dataclasses.field(default_factory=list)
    port: int = 0

    async def start(self) -> asyncio.Server:
        server = await asyncio.start_server(self._serve, "127.0.0.1", 0)
        self.port = server.sockets[0].getsockname()[1]
        return server

    def get_delivered(self) -> tuple[Mail, ...]:
        return tuple(read_mail(message) for message in self.messages)

    async def _serve(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            if self.is_silent:
                await reader.read()
                return
            await self._reply(writer, self.replies.get("CONNECT", "220 ready"))
            while line := (await reader.readline()).decode().rstrip("\r\n"):
                verb, _, rest = line.partition(" ")
                verb = verb.upper()
                if verb == "EHLO":
                    extensions = ["250-test", "250-SMTPUTF8"]
                    if self.is_auth:
                        extensions.append("250-AUTH PLAIN")
                    await self._reply(
                        writer, "\r\n".join([*extensions, "250 8BITMIME"])
                    )
                elif verb == "AUTH":
                    self.logins.append(base64.b64decode(rest.split()[1]).decode())
                    await self._reply(writer, "235 ok")
                elif verb == "RCPT":
                    address = rest.partition(":")[2].strip("<> ").split(">")[0]
                    default = self.replies.get("RCPT", "250 ok")
                    await self._reply(
                        writer, self.replies.get(f"RCPT {address}", default)
                    )
                elif verb == "DATA":
                    await self._reply(writer, "354 go on")
                    data = b""
                    while (chunk := await reader.readline()) != b".\r\n":
                        data += chunk
                    reply = self.replies.get("DATA", "250 ok")
                    if reply.startswith("2"):
                        self.messages.append(data)
                    await self._reply(writer, reply)
                elif verb == "QUIT":
                    await self._reply(writer, "221 bye")
                    break
                else:
                    await self._reply(writer, self.replies.get(verb, "250 ok"))
        finally:
            writer.close()

    async def _reply(self, writer: asyncio.StreamWriter, reply: str) -> None:
        writer.write(reply.encode() + b"\r\n")
        await writer.drain()


def read_mail(data: bytes) -> Mail:
    """The mail of a message as a server took it."""
    message = email.parser.BytesParser(policy=email.policy.default).parsebytes(data)
    text = t.cast(str, message.get_content()).replace("\r\n", "\n")
    return Mail(
        to=tuple(address.strip() for address in str(message["To"]).split(",")),
        subject=str(message["Subject"]),
        text=text,
        sender=str(message["From"]),
    )
