PROJECT=$1
REGION=$2
TEMP_BUCKET=$3
SUBSCRIPTION=$4

python3 pubsub_to_printer.py \
  --project=$PROJECT \
  --region=$REGION \
  --experiments=use_runner_v2 \
  --job_name=pubsub-xlang \
  --input_subscription=$SUBSCRIPTION \
  --setup_file=./setup.py \
  --runner=DataflowRunner \
  --temp_location=$TEMP_BUCKET/temp \
  --staging_location=$TEMP_BUCKET/staging \
  --external_transforms_jar="/Users/pablor/projects/twitter/cdl/dataflow-xlang-pipelines/java-pipelines/dataflow-xlang-transforms/target/xlang-ptransforms-bundled-0.0.1.jar" $5
  