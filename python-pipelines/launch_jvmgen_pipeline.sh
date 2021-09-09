PROJECT=$1
REGION=$2
SUBSCRIPTION=$3
OUTPUT_BUCKET_LOCATION=$4
TEMP_BUCKET=$5

EXTERNAL_TRANSFORM_JAR="${PWD}/../java-pipelines/dataflow-xlang-transforms/target/xlang-ptransforms-bundled-0.0.1.jar"

python3 data_from_jvm.py \
  --project=$PROJECT \
  --region=$REGION \
  --experiments=use_runner_v2 \
  --job_name=xlang-jvmgen-dataframe \
  --origin=$SUBSCRIPTION \
  --csv_output_location=$OUTPUT_BUCKET_LOCATION \
  --avro_schema_file=./avro-schema.json \
  --setup_file=./setup.py \
  --runner=DataflowRunner \
  --temp_location=$TEMP_BUCKET/temp \
  --staging_location=$TEMP_BUCKET/staging \
  --no_use_public_ips \
  --external_transforms_jar=$EXTERNAL_TRANSFORM_JAR $6
  