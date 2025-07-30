import numpy as np
import pytest

from blissdata.lima.client import Lima2Client
from blissdata.streams.lima2.stream import Lima2Stream


def test_lima2_client_protocol_version():
    lima_info = {
        "protocol_version": Lima2Client.PROTOCOL_VERSION,
        "server_urls": ["a/b/c", "d/e/f"],
        "name": "frame",
    }

    client = Lima2Client(**lima_info)
    assert client._source == "frame"

    with pytest.raises(Exception) as exc_info:
        Lima2Client(
            protocol_version=Lima2Client.PROTOCOL_VERSION + 123,
            server_urls=["a/b/c", "d/e/f"],
            name="frame",
        )

    assert "lima2 json protocol" in str(exc_info.value)


def test_lima2_stream_definition():
    lima_info = {
        "protocol_version": Lima2Client.PROTOCOL_VERSION,
        "server_urls": ["a/b/c", "d/e/f"],
        "name": "frame",
    }
    stream_def = Lima2Stream.make_definition(
        name="frame_stream",
        dtype=np.int32,
        shape=(1, 1024, 2048),
        lima_info=lima_info,
        info={},
    )

    assert stream_def.info["lima_info"] == lima_info
