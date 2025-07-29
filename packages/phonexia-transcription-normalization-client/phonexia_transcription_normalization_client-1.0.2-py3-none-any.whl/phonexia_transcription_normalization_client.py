"""Phonexia transcription normalization client.

This module provides a transcription normalization client.
This client can be used to communicate with the transcription normalization server.
"""

import argparse
import json
import logging
import pathlib
from collections.abc import Iterator
from contextlib import nullcontext
from typing import Union

import grpc
from google.protobuf.json_format import MessageToDict, ParseDict
from more_itertools import chunked
from phonexia.grpc.technologies.transcription_normalization.v1.transcription_normalization_pb2 import (
    NormalizeConfig,
    NormalizeRequest,
    NormalizeResponse,
    Segment,
    Word,
)
from phonexia.grpc.technologies.transcription_normalization.v1.transcription_normalization_pb2_grpc import (
    TranscriptionNormalizationStub,
)


def read_json_segments(file: str) -> Iterator[Segment]:
    with open(file, encoding="utf-8") as fd:
        for seg in json.load(fd)["segments"]:
            yield ParseDict(seg, Segment())


def read_txt_segments(file: str) -> Iterator[Segment]:
    with open(file, encoding="utf-8") as fd:
        for line in fd:
            yield Segment(text=line.strip(), words=[Word(text=w) for w in line.strip().split()])


def make_request(
    file: str,
    language: Union[str, None],
) -> Iterator[NormalizeRequest]:
    read_json = pathlib.Path(file).suffix == ".json"
    logging.debug(f"Reading {file} as {'json' if read_json else 'txt'} format")

    segments = read_json_segments(file) if read_json else read_txt_segments(file)
    for segments_chunk in chunked(segments, 1000):
        yield NormalizeRequest(segments=segments_chunk, config=NormalizeConfig(language=language))


def normalize(
    channel: grpc.Channel,
    file: str,
    output_file: Union[str, None],
    json_format: bool,
    metadata: Union[list[str], None],
    language: Union[str, None],
) -> None:
    logging.info(f"Normalizing '{file}'")
    stub = TranscriptionNormalizationStub(channel)  # type: ignore[no-untyped-call]
    response_it: Iterator[NormalizeResponse] = stub.Normalize(
        make_request(file, language=language),
        metadata=metadata,
    )

    segments: list[Segment] = [segment for response in response_it for segment in response.segments]

    with open(output_file, "w", encoding="utf-8") if output_file else nullcontext() as fd:
        if json_format:
            print(
                json.dumps(
                    {
                        "segments": [
                            MessageToDict(
                                seg,
                                preserving_proto_field_name=True,
                            )
                            for seg in segments
                        ]
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                file=fd,
            )
        else:
            for segment in segments:
                print(segment.text, file=fd)


def existing_file(file: str) -> str:
    if not pathlib.Path(file).exists():
        raise argparse.ArgumentError(argument=None, message=f"File {file} does not exist")
    return file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Text normalization gRPC client. Reads text from file and writes normalized text to stdout."
    )
    parser.add_argument(
        "-H",
        "--host",
        type=str,
        default="localhost:8080",
        help="Server address, default: localhost:8080.",
    )
    parser.add_argument(
        "-l",
        "--log_level",
        type=str,
        default="error",
        choices=["critical", "error", "warning", "info", "debug"],
    )
    parser.add_argument(
        "--metadata",
        metavar="key=value",
        nargs="+",
        type=lambda x: tuple(x.split("=")),
        help="Custom client metadata.",
    )
    parser.add_argument(
        "--language",
        help="Language of the input text. If not specified, some of the functionality (digit conversion, etc.) "
        "will be disabled.",
    )
    parser.add_argument(
        "--to_json",
        action="store_true",
        help="Specify that the output file is in JSON format.",
    )
    parser.add_argument("--use_ssl", action="store_true", help="Use SSL connection")
    parser.add_argument(
        "file",
        type=existing_file,
        help="Input file. JSON or plain text formats are supported based on the file extension. Plain text format "
        "defines multiple sentences, each on a separate line. The JSON format defines a list of segments with "
        "optional per word segmentation (the output format of Phonexia speech to text technology). The JSON "
        'structure is the following: {"segments": [{"text": "text", "words": [{"text": "word"}]}]}. Additionally, '
        "segmentation timestamps (start_time and end_time) can be added to both segments and words.",
    )
    parser.add_argument("output_file", nargs="?", help="Output file.")

    args = parser.parse_args()

    logging.basicConfig(
        level=args.log_level.upper(),
        format="[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        logging.info(f"Connecting to {args.host}")
        with (
            grpc.secure_channel(target=args.host, credentials=grpc.ssl_channel_credentials())
            if args.use_ssl
            else grpc.insecure_channel(target=args.host)
        ) as channel:
            normalize(
                channel=channel,
                file=args.file,
                output_file=args.output_file,
                json_format=args.to_json,
                metadata=args.metadata,
                language=args.language,
            )
    except grpc.RpcError as e:
        logging.exception(f"RPC failed: {e}")  # noqa: TRY401
        exit(1)
    except Exception:
        logging.exception("Unknown error")
        exit(1)


if __name__ == "__main__":
    main()
