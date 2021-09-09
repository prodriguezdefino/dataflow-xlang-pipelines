# Copyright 2021 Google LLC.
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
import random

from apache_beam import DoFn, ParDo, Pipeline, WindowInto, window
from apache_beam.dataframe.convert import to_dataframe
from apache_beam.options.pipeline_options import PipelineOptions

from transforms.jvm_generator import JVMDataGenerator

class PrintData(DoFn):
    def process(self, data):
        if random.random() >= 0.1:
            logging.info('randomly sampled message: %s', 
                str(data))
        yield data

def run(origin, avro_schema_file, csv_output_location, external_transforms_jar=None, pipeline_args=None):
    # Set `save_main_session` to True so DoFns can access globally imported modules.
    pipeline_options = PipelineOptions(
        pipeline_args, streaming=True, save_main_session=True
    )

    avro_schema = None

    with open(avro_schema_file, 'r') as file:
        avro_schema = file.read()

    print(f'Using Avro Schema for generated data {avro_schema}')

    with Pipeline(options=pipeline_options) as pipeline:
        data_from_jvm = (
            pipeline
            | "ReadFromJVM" >> JVMDataGenerator(origin, avro_schema, external_transforms_jar)
            | "PrintData" >> ParDo(PrintData())
            | "60sWindow" >> WindowInto(window.FixedWindows(60))
        )

        # A Beam Dataframe is very similar to a Pandas Dataframe, but because of its parallelized backend (data may be distributed across multiple workers)
        # not all the supported operatios on Pandas are available to use in this context. 
        # Check on https://beam.apache.org/documentation/dsls/dataframes/differences-from-pandas for more clarity on the current limitations.
        people_data = to_dataframe(data_from_jvm)
        # count active people with a particular eye color
        counts_by_eyeColor_window = people_data.groupby('eyeColor').isActive.count()
        # generates as many files as eye colors seen in that particular window
        counts_by_eyeColor_window.to_csv(csv_output_location)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--origin",
        help="The Cloud Pub/Sub subscription to read from."
        '"projects/<PROJECT_ID>/subscriptions/<SUB_ID>".',
        required=True,
    )
    parser.add_argument(
        "--avro_schema_file",
        type=str,
        required=True,
        help="The file location for the avro schema of the data being generated.",
    )
    parser.add_argument(
        "--csv_output_location",
        type=str,
        required=True,
        help="The location for the CSV file with the counts by gender and window.",
    )
    parser.add_argument(
        "--external_transforms_jar",
        type=str,
        default=None,
        help="The absolute location of the JAR file containing externalized JVM PTransforms",
    )
    known_args, pipeline_args = parser.parse_known_args()

    run(
        known_args.origin,
        known_args.avro_schema_file,
        known_args.csv_output_location,
        known_args.external_transforms_jar,
        pipeline_args,
    )
# [END pubsub_to_gcs]