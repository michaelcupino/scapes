import webapp2
import logging

def hello_world_map():
    self.response.out.write('hello')

def hello_world_reduce():
    pass

class HelloWorldPipeline(webapp2.RequestHandler):
    def run(self):
        yield mapreduce_pipeline.MapreducePipeline(
                                                   "hello_world",
                                                   "hello_world_map",
                                                   "hello_world_reduce",
                                                   "mapreduce.input_readers.BlobstoreZipInputReader",
                                                   "mapreduce.output_writers.BlobstoreOutputWriter",
                                                   mapper_params = {
                                                                    "blob_key": blobkey,
                                                                    },
                                                   reducer_params = {
                                                                     "mime_type": "text/plain",
                                                                     },
                                                   shards = 16)

class HelloWorldHandler(webapp2.RequestHandler):
    def get(self):
        HelloWorldPipeline.run()

