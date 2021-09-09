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
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.transforms.ExternalTransformBuilder;
import org.apache.beam.sdk.transforms.PTransform;
import org.apache.beam.sdk.transforms.ParDo;
import org.apache.beam.sdk.values.PCollection;
import org.apache.beam.sdk.values.PDone;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Simple example for a JVM Printer or Logger, this PTransform will be exposed by the Expansion Service and can be used from a Python
 * pipeline.
 */
@AutoValue
public abstract class JVMPrinter extends PTransform<PCollection<String>, PDone> {

  private static final Logger LOG = LoggerFactory.getLogger(JVMPrinter.class);

  abstract String getPrintFormat();

  abstract Builder toBuilder();

  @AutoValue.Builder
  abstract static class Builder implements
          ExternalTransformBuilder<
          JVMPrinterExternalTransformRegistrar.Configuration, PCollection<String>, PDone> {

    abstract Builder setPrintFormat(String printFormat);

    abstract JVMPrinter build();

    @Override
    public PTransform<PCollection<String>, PDone> buildExternal(
            JVMPrinterExternalTransformRegistrar.Configuration configuration) {

      return JVMPrinter.printer().withPrintFormat(configuration.getPrintFormat());
    }
  }

  public static JVMPrinter printer() {
    return new AutoValue_JVMPrinter.Builder()
            .setPrintFormat("%s")
            .build();
  }

  public JVMPrinter withPrintFormat(String printFormat) {
    return toBuilder().setPrintFormat(printFormat).build();
  }

  @Override
  public PDone expand(PCollection<String> input) {

    input.apply("Print", ParDo.of(new Printer(getPrintFormat())));

    return PDone.in(input.getPipeline());
  }

  static class Printer extends DoFn<String, Void> {

    private final String printFormat;

    public Printer(String printFormat) {
      this.printFormat = printFormat;
    }

    @ProcessElement
    public void processElement(ProcessContext context) {
      LOG.info(String.format(printFormat, context.element()));
      context.output((Void) null);
    }
  }

  @AutoService(ExternalTransformRegistrar.class)
  static public class JVMPrinterExternalTransformRegistrar implements ExternalTransformRegistrar {

    public static final String URN = "examples:external:java:print:v1";

    @Override
    public Map<String, ExternalTransformBuilder<?, ?, ?>> knownBuilderInstances() {
      return ImmutableMap.of(
              URN,
              new AutoValue_JVMPrinter.Builder());
    }

    /**
     * Parameters class to expose the Read transform to an external SDK.
     */
    public static class Configuration {

      private String printFormat;

      public void setPrintFormat(String printFormat) {
        this.printFormat = printFormat;
      }

      public String getPrintFormat() {
        return printFormat;
      }
    }
  }

}
