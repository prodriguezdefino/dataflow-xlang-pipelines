import typing

from apache_beam.transforms.external import BeamJarExpansionService
from apache_beam.transforms.external import JavaJarExpansionService
from apache_beam.transforms.external import ExternalTransform
from apache_beam.transforms.external import NamedTupleBasedPayloadBuilder

def default_io_expansion_service():
    return BeamJarExpansionService('sdks:java:io:expansion-service:shadowJar')

def expansion_service_from_path(path):
    return JavaJarExpansionService(path)


JVMPrinterSchema = typing.NamedTuple(
    'JVMPrinterSchema',
    [
        ('print_format', str),
    ])


class JVMPrinter(ExternalTransform):

  URN = 'examples:external:java:print:v1'

  def __init__(
      self,
      print_format,
      expansion_service_jar_path=None):

    super(JVMPrinter, self).__init__(
        self.URN,
        NamedTupleBasedPayloadBuilder(
            JVMPrinterSchema(
                print_format=print_format,
            )),
        expansion_service_from_path(expansion_service_jar_path) 
            if expansion_service_jar_path else default_io_expansion_service())