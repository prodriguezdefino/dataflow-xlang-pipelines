/*
 * Copyright (C) 2021 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */
package com.example.dataflow.transforms;

import avro.shaded.com.google.common.collect.ImmutableMap;
import com.google.auto.service.AutoService;
import com.google.auto.value.AutoValue;
import java.util.Map;
import org.apache.beam.sdk.expansion.ExternalTransformRegistrar;
import org.apache.beam.sdk.io.gcp.pubsub.PubsubIO;
import org.apache.beam.sdk.schemas.Schema;
import org.apache.beam.sdk.schemas.utils.AvroUtils;
import org.apache.beam.sdk.transforms.ExternalTransformBuilder;
import org.apache.beam.sdk.transforms.JsonToRow;
import org.apache.beam.sdk.transforms.MapElements;
import org.apache.beam.sdk.transforms.PTransform;
import org.apache.beam.sdk.values.PBegin;
import org.apache.beam.sdk.values.PCollection;
import org.apache.beam.sdk.values.Row;
import org.apache.beam.sdk.values.TypeDescriptors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Simple example for a JVM Data Generator that captures messages from pubsub and produces Beam Rows based on a provided AVRO schema for the
 * messages (which will come as JSON messages, sorry for the complexity). This PTransform will be exposed by the Expansion Service and can
 * be used from a Python pipeline.
 */
@AutoValue
public abstract class JVMDataGenerator extends PTransform<PBegin, PCollection<Row>> {

  private static final Logger LOG = LoggerFactory.getLogger(JVMDataGenerator.class);

  abstract String getAvroSchema();

  abstract String getOrigin();

  @AutoValue.Builder
  abstract static class Builder implements
          ExternalTransformBuilder<
          JVMDataGeneratorExternalTransformRegistrar.Configuration, PBegin, PCollection<Row>> {

    abstract Builder setAvroSchema(String avroSchema);

    abstract Builder setOrigin(String origin);

    abstract JVMDataGenerator build();

    @Override
    public PTransform<PBegin, PCollection<Row>> buildExternal(
            JVMDataGeneratorExternalTransformRegistrar.Configuration configuration) {
      return JVMDataGenerator.withOriginAndAvroSchema(
              configuration.getOrigin(),
              configuration.getAvroSchema());
    }
  }

  public static JVMDataGenerator withOriginAndAvroSchema(String origin, String avroSchema) {
    return new AutoValue_JVMDataGenerator.Builder()
            .setAvroSchema(avroSchema)
            .setOrigin(origin)
            .build();
  }

  @Override
  public PCollection<Row> expand(PBegin input) {
    Schema rowSchema = AvroUtils.toBeamSchema(new org.apache.avro.Schema.Parser().parse(getAvroSchema()));
    return input
            .apply("ReadFromPubsubData", PubsubIO.readMessages().fromSubscription(getOrigin()))
            .apply("ExtractBody", MapElements.into(TypeDescriptors.strings()).via(psMsg -> new String(psMsg.getPayload())))
            .apply("TransformIntoBeamRow", JsonToRow.withSchema(rowSchema));
  }

  @AutoService(ExternalTransformRegistrar.class)
  static public class JVMDataGeneratorExternalTransformRegistrar implements ExternalTransformRegistrar {

    public static final String URN = "examples:external:java:generator:v1";

    @Override
    public Map<String, ExternalTransformBuilder<?, ?, ?>> knownBuilderInstances() {
      return ImmutableMap.of(
              URN,
              new AutoValue_JVMDataGenerator.Builder());
    }

    /**
     * Parameters class to expose the Read transform to an external SDK.
     */
    public static class Configuration {

      private String avroSchema;
      private String origin;

      public void setAvroSchema(String printFormat) {
        this.avroSchema = printFormat;
      }

      public String getAvroSchema() {
        return avroSchema;
      }

      public String getOrigin() {
        return origin;
      }

      public void setOrigin(String origin) {
        this.origin = origin;
      }
    }
  }

}
