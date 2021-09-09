PROJECT=$1
REGION=$2
TEMP_BUCKET=$3
SUBSCRIPTION=$4

EXTERNAL_TRANSFORM_JAR="${PWD}/../java-pipelines/dataflow-xlang-transforms/target/xlang-ptransforms-bundled-0.0.1.jar"

python3 pubsub_to_jvmprinter.py \
  --project=$PROJECT \
  --region=$REGION \
  --experiments=use_runner_v2 \
  --job_name=xlang-jvmprinter \
  --input_subscription=$SUBSCRIPTION \
  --setup_file=./setup.py \
  --runner=DataflowRunner \
  --temp_location=$TEMP_BUCKET/temp \
  --staging_location=$TEMP_BUCKET/staging \
  --no_use_public_ips \
  --external_transforms_jar=$EXTERNAL_TRANSFORM_JAR $5
  