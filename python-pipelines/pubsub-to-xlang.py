# Copyright 2019 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START pubsub_to_gcs]
import argparse
import logging
import typing

from apache_beam import DoFn, io, ParDo, Pipeline
from apache_beam.options.pipeline_options import PipelineOptions

from transforms.jvm_printer import JVMPrinter
from transforms.group_messages import GroupMessagesByFixedWindows

class EnsureTypeSafety(DoFn):
    def process(self, key_value, window=DoFn.WindowParam) -> typing.Iterable[str]:
        shard, batch = key_value

        for message_body, publish_time in batch:
            yield f'got {str(shard)} with message received at : {publish_time}, payload: {message_body}'


class PrintData(DoFn):
    def process(self, key_value, window=DoFn.WindowParam):
        """Write messages in a batch to Google Cloud Storage."""

        ts_format = "%H:%M"
        window_start = window.start.to_utc_datetime().strftime(ts_format)
        window_end = window.end.to_utc_datetime().strftime(ts_format)
        _, batch = key_value

        for message_body, publish_time in batch:
            logging.info('at : %s received message: %s, on window [%s - %s]', 
                            publish_time, 
                            message_body, 
                            window_start, 
                            window_end)


def run(input_subscription, window_size=1.0, external_transforms_jar=None, pipeline_args=None):
    # Set `save_main_session` to True so DoFns can access globally imported modules.
    pipeline_options = PipelineOptions(
        pipeline_args, streaming=True, save_main_session=True
    )

    with Pipeline(options=pipeline_options) as pipeline:
        prints = (
            pipeline
            # Because `timestamp_attribute` is unspecified in `ReadFromPubSub`, Beam
            # binds the publish time returned by the Pub/Sub server for each message
            # to the element's timestamp parameter, accessible via `DoFn.TimestampParam`.
            # https://beam.apache.org/releases/pydoc/current/apache_beam.io.gcp.pubsub.html#apache_beam.io.gcp.pubsub.ReadFromPubSub
            | "Read from Pub/Sub" >> io.ReadFromPubSub(subscription=input_subscription)
            | "Window into" >> GroupMessagesByFixedWindows(window_size)
            | "TypeSafeness" >> ParDo(EnsureTypeSafety())
            | "PrintMessagesJVM" >> JVMPrinter('%s', external_transforms_jar)
        )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_subscription",
        help="The Cloud Pub/Sub subscription to read from."
        '"projects/<PROJECT_ID>/subscriptions/<SUB_ID>".',
        required=True,
    )
    parser.add_argument(
        "--window_size",
        type=float,
        default=1.0,
        help="Output file's window size in minutes.",
    )
    parser.add_argument(
        "--external_transforms_jar",
        type=str,
        default=None,
        help="The absolute location of the JAR file containing externalized JVM PTransforms",
    )
    known_args, pipeline_args = parser.parse_known_args()

    run(
        known_args.input_subscription,
        known_args.window_size,
        known_args.external_transforms_jar,
        pipeline_args,
    )
# [END pubsub_to_gcs]