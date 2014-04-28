from mapreduce import base_handler
from mapreduce import mapreduce_pipeline
from handler.file_id_handler import documents_in_folder
from pipeline.scapes_store_output import ScapesStoreOutput
from handler.file_id_handler import documents_in_folder
from service import utils

class ScapesAnalysisPipeline(base_handler.PipelineBase):
  """A pipeline to run SCAPES demo. """

  def run(self, mapper_data_id):
    # print "\n"+"="*100, type(http), "\n", folder_id, "=" * 100
    output = yield mapreduce_pipeline.MapreducePipeline(
      "scapes_analyze",
      "service.utils.scapes_analyze_document",
      "service.utils.scapes_analyze_reduce",
      "mapreduce.input_readers.BlobstoreLineInputReader",
      "mapreduce.output_writers.BlobstoreOutputWriter",
      mapper_params={
        "blob_key": mapper_data_id,
      },
      reducer_params={
        "mime_type": "text/plain",
      },
      shards=16)
    # TODO: replace this with out own cleanup code.
    yield ScapesStoreOutput("scapes_analyze", folder_id, output)

def scapes_generate_blobstore_record(http, folder_id):
  # TODO: blocked on Fosters code
  map_contents = documents_in_folder(http, folder_id)
  blobstore_id = utils.scapes_write_to_blobstore(map_contents)
  return blobstore_id

