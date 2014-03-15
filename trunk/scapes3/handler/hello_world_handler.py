import webapp2
import logging
from mapreduce_dependencies import input_readers
from mapreduce_dependencies import output_writers
from mapreduce_dependencies import mapreduce_pipeline
from mapreduce_dependencies import base_handler

from mapreduce_dependencies import input_readers
from mapreduce_dependencies import output_writers
from mapreduce_dependencies import mapreduce_pipeline
from mapreduce_dependencies import base_handler

from google.appengine.ext import blobstore,db
from google.appengine.ext.webapp import blobstore_handlers

map_data = 'map fucntion'
reduce_data = 'reduce function'

def hello_world_map(map_data):
    print('map')

def hello_world_reduce(reduce_data):
    print('reduce')

class HelloWorldPipeline(webapp2.RequestHandler):
    def run(self):
        print('pipeline')
        yield mapreduce_pipeline.MapreducePipeline(
                                                   "hello_world",
                                                   "hello_world_map",
                                                   "hello_world_reduce",
                                                   "mapreduce.input_readers.BlobstoreZipInputReader",
                                                   "mapreduce.output_writers.BlobstoreOutputWriter",
                                                   mapper_params = {
                                                                    "blob_key": 'blobkey',
                                                                    },
                                                   reducer_params = {
                                                                     "mime_type": "text/plain",
                                                                     },
                                                   shards = 16)
        print('got to the end of run')

class HelloWorldHandler(webapp2.RequestHandler):
    def get(self):
        print('handler')
        self.response.out.write("HELLOOOELEROERWRWR")
        name = HelloWorldPipeline()
        for item in name.run():
            item.start()
            print('\n')
            print('args:')
            for thing in item.args:
                print(thing)
            print('\n')
            print('kwargs:')
            for key,value in item.kwargs.items():
                print(key, 'value is = to: ', value)
            

