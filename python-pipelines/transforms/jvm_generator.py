import typing

from apache_beam.transforms.external import BeamJarExpansionService
from apache_beam.transforms.external import JavaJarExpansionService
from apache_beam.transforms.external import ExternalTransform
from apache_beam.transforms.external import NamedTupleBasedPayloadBuilder

def default_io_expansion_service():
    return BeamJarExpansionService('sdks:java:io:expansion-service:shadowJar')

def expansion_service_from_path(path):
    return JavaJarExpansionService(path)


JVMDataGeneratorSchema = typing.NamedTuple(
    'JVMDataGeneratorSchema',
    [
        ('origin', str),
        ('avro_schema', str),
    ])


class JVMDataGenerator(ExternalTransform):

  URN = 'examples:external:java:generator:v1'

  def __init__(
      self,
      origin,
      avro_schema,
      expansion_service_jar_path=None):

    super(JVMDataGenerator, self).__init__(
        self.URN,
        NamedTupleBasedPayloadBuilder(
            JVMDataGeneratorSchema(
                origin=origin,
                avro_schema=avro_schema,
            )),
        expansion_service_from_path(expansion_service_jar_path) 
            if expansion_service_jar_path else default_io_expansion_service())