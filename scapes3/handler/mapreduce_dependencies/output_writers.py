#!/usr/bin/env python
#
# Copyright 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Output writers for MapReduce."""

from __future__ import with_statement



__all__ = [
    "BlobstoreOutputWriter",
    "BlobstoreOutputWriterBase",
    "BlobstoreRecordsOutputWriter",
    "FileOutputWriter",
    "FileOutputWriterBase",
    "FileRecordsOutputWriter",
    "KeyValueBlobstoreOutputWriter",
    "KeyValueFileOutputWriter",
    "COUNTER_IO_WRITE_BYTES",
    "COUNTER_IO_WRITE_MSEC",
    "OutputWriter",
    "RecordsPool",
    ]

# pylint: disable=g-bad-name
# pylint: disable=protected-access

import cStringIO
import gc
import logging
import pickle
import string
import time

from google.appengine.api import files
from google.appengine.api.files import file_service_pb
from handler.mapreduce_dependencies import context
from handler.mapreduce_dependencies import errors
from handler.mapreduce_dependencies import model
from handler.mapreduce_dependencies import operation
from handler.mapreduce_dependencies import records

# pylint: disable=g-import-not-at-top
# TODO(user): Cleanup imports if/when cloudstorage becomes part of runtime.
try:
  # Check if the full cloudstorage package exists. The stub part is in runtime.
  import cloudstorage
  if hasattr(cloudstorage, "_STUB"):
    cloudstorage = None
except ImportError:
  pass  # CloudStorage library not available


# Counter name for number of bytes written.
COUNTER_IO_WRITE_BYTES = "io-write-bytes"

# Counter name for time spent writing data in msec
COUNTER_IO_WRITE_MSEC = "io-write-msec"


class OutputWriter(model.JsonMixin):
  """Abstract base class for output writers.

  Output writers process all mapper handler output, which is not
  the operation.

  OutputWriter's lifecycle is the following:
    0) validate called to validate mapper specification.
    1) init_job is called to initialize any job-level state.
    2) create() is called, which should create a new instance of output
       writer for a given shard
    3) from_json()/to_json() are used to persist writer's state across
       multiple slices.
    4) write() method is called to write data.
    5) finalize() is called when shard processing is done.
    6) finalize_job() is called when job is completed.
    7) get_filenames() is called to get output file names.
  """

  @classmethod
  def validate(cls, mapper_spec):
    """Validates mapper specification.

    Output writer parameters are expected to be passed as "output_writer"
    subdictionary of mapper_spec.params. To be compatible with previous
    API output writer is advised to check mapper_spec.params and issue
    a warning if "output_writer" subdicationary is not present.
    _get_params helper method can be used to simplify implementation.

    Args:
      mapper_spec: an instance of model.MapperSpec to validate.
    """
    raise NotImplementedError("validate() not implemented in %s" % cls)

  @classmethod
  def init_job(cls, mapreduce_state):
    """Initialize job-level writer state.

    This method is only to support the deprecated feature which is shared
    output files by many shards. New output writers should not do anything
    in this method.

    Args:
      mapreduce_state: an instance of model.MapreduceState describing current
      job. MapreduceState.writer_state can be modified during initialization
      to save the information about the files shared by many shards.
    """
    pass

  @classmethod
  def finalize_job(cls, mapreduce_state):
    """Finalize job-level writer state.

    This method is only to support the deprecated feature which is shared
    output files by many shards. New output writers should not do anything
    in this method.

    This method should only be called when mapreduce_state.result_status shows
    success. After finalizing the outputs, it should save the info for shard
    shared files into mapreduce_state.writer_state so that other operations
    can find the outputs.

    Args:
      mapreduce_state: an instance of model.MapreduceState describing current
      job. MapreduceState.writer_state can be modified during finalization.
    """
    pass

  @classmethod
  def from_json(cls, state):
    """Creates an instance of the OutputWriter for the given json state.

    Args:
      state: The OutputWriter state as a dict-like object.

    Returns:
      An instance of the OutputWriter configured using the values of json.
    """
    raise NotImplementedError("from_json() not implemented in %s" % cls)

  def to_json(self):
    """Returns writer state to serialize in json.

    Returns:
      A json-izable version of the OutputWriter state.
    """
    raise NotImplementedError("to_json() not implemented in %s" %
                              self.__class__)

  @classmethod
  def create(cls, mapreduce_state, shard_state):
    """Create new writer for a shard.

    Args:
      mapreduce_state: an instance of model.MapreduceState describing current
      job. State can NOT be modified.
      shard_state: shard state can NOT be modified. Output file state should
      be contained in the output writer instance. The serialized output writer
      instance will be saved by mapreduce across slices.
    """
    raise NotImplementedError("create() not implemented in %s" % cls)

  def write(self, data):
    """Write data.

    Args:
      data: actual data yielded from handler. Type is writer-specific.
    """
    raise NotImplementedError("write() not implemented in %s" %
                              self.__class__)

  def finalize(self, ctx, shard_state):
    """Finalize writer shard-level state.

    This should only be called when shard_state.result_status shows success.
    After finalizing the outputs, it should save per-shard output file info
    into shard_state.writer_state so that other operations can find the
    outputs.

    Args:
      ctx: an instance of context.Context.
      shard_state: shard state. ShardState.writer_state can be modified.
    """
    raise NotImplementedError("finalize() not implemented in %s" %
                              self.__class__)

  @classmethod
  def get_filenames(cls, mapreduce_state):
    """Obtain output filenames from mapreduce state.

    This method should only be called when a MR is finished. Implementors of
    this method should not assume any other methods of this class have been
    called. In the case of no input data, no other method except validate
    would have been called.

    Args:
      mapreduce_state: an instance of model.MapreduceState

    Returns:
      List of filenames this mapreduce successfully wrote to. The list can be
    empty if no output file was successfully written.
    """
    raise NotImplementedError("get_filenames() not implemented in %s" % cls)

  # pylint: disable=unused-argument
  def _can_be_retried(self, tstate):
    """Whether this output writer instance supports shard retry.

    Args:
      tstate: model.TransientShardState for current shard.

    Returns:
      boolean. Whether this output writer instance supports shard retry.
    """
    return False

# Flush size for files api write requests. Approximately one block of data.
_FILES_API_FLUSH_SIZE = 128*1024

# Maximum size of files api request. Slightly less than 1M.
_FILES_API_MAX_SIZE = 1000*1024


def _get_params(mapper_spec, allowed_keys=None, allow_old=True):
  """Obtain output writer parameters.

  Utility function for output writer implementation. Fetches parameters
  from mapreduce specification giving appropriate usage warnings.

  Args:
    mapper_spec: The MapperSpec for the job
    allowed_keys: set of all allowed keys in parameters as strings. If it is not
      None, then parameters are expected to be in a separate "output_writer"
      subdictionary of mapper_spec parameters.
    allow_old: Allow parameters to exist outside of the output_writer
      subdictionary for compatability.

  Returns:
    mapper parameters as dict

  Raises:
    BadWriterParamsError: if parameters are invalid/missing or not allowed.
  """
  if "output_writer" not in mapper_spec.params:
    message = (
        "Output writer's parameters should be specified in "
        "output_writer subdictionary.")
    if not allow_old or allowed_keys:
      raise errors.BadWriterParamsError(message)
    params = mapper_spec.params
    params = dict((str(n), v) for n, v in params.iteritems())
  else:
    if not isinstance(mapper_spec.params.get("output_writer"), dict):
      raise errors.BadWriterParamsError(
          "Output writer parameters should be a dictionary")
    params = mapper_spec.params.get("output_writer")
    params = dict((str(n), v) for n, v in params.iteritems())
    if allowed_keys:
      params_diff = set(params.keys()) - allowed_keys
      if params_diff:
        raise errors.BadWriterParamsError(
            "Invalid output_writer parameters: %s" % ",".join(params_diff))
  return params


class _FilePool(context.Pool):
  """Pool of file append operations."""

  def __init__(self, flush_size_chars=_FILES_API_FLUSH_SIZE, ctx=None):
    """Constructor.

    Args:
      flush_size_chars: buffer flush size in bytes as int. Internal buffer
        will be flushed once this size is reached.
      ctx: mapreduce context as context.Context. Can be null.
    """
    self._flush_size = flush_size_chars
    self._append_buffer = {}
    self._size = 0
    self._ctx = ctx

  def __append(self, filename, data):
    """Append data to the filename's buffer without checks and flushes."""
    self._append_buffer[filename] = (
        self._append_buffer.get(filename, "") + data)
    self._size += len(data)

  def append(self, filename, data):
    """Append data to a file.

    Args:
      filename: the name of the file as string.
      data: data as string.
    """
    if self._size + len(data) > self._flush_size:
      self.flush()

    if len(data) > _FILES_API_MAX_SIZE:
      raise errors.Error(
          "Can't write more than %s bytes in one request: "
          "risk of writes interleaving." % _FILES_API_MAX_SIZE)
    else:
      self.__append(filename, data)

    if self._size > self._flush_size:
      self.flush()

  def flush(self):
    """Flush pool contents."""
    start_time = time.time()
    for filename, data in self._append_buffer.iteritems():
      with files.open(filename, "a") as f:
        if len(data) > _FILES_API_MAX_SIZE:
          raise errors.Error("Bad data of length: %s" % len(data))
        if self._ctx:
          operation.counters.Increment(
              COUNTER_IO_WRITE_BYTES, len(data))(self._ctx)
        f.write(data)
    if self._ctx:
      operation.counters.Increment(
          COUNTER_IO_WRITE_MSEC,
          int((time.time() - start_time) * 1000))(self._ctx)
    self._append_buffer = {}
    self._size = 0


class RecordsPool(context.Pool):
  """Pool of append operations for records files."""

  # Approximate number of bytes of overhead for storing one record.
  _RECORD_OVERHEAD_BYTES = 10

  def __init__(self, filename,
               flush_size_chars=_FILES_API_FLUSH_SIZE,
               ctx=None,
               exclusive=False):
    """Constructor.

    Args:
      filename: file name to write data to as string.
      flush_size_chars: buffer flush threshold as int.
      ctx: mapreduce context as context.Context.
      exclusive: a boolean flag indicating if the pool has an exclusive
        access to the file. If it is True, then it's possible to write
        bigger chunks of data.
    """
    self._flush_size = flush_size_chars
    self._buffer = []
    self._size = 0
    self._filename = filename
    self._ctx = ctx
    self._exclusive = exclusive

  def append(self, data):
    """Append data to a file."""
    data_length = len(data)
    if self._size + data_length > self._flush_size:
      self.flush()

    if not self._exclusive and data_length > _FILES_API_MAX_SIZE:
      raise errors.Error(
          "Too big input %s (%s)."  % (data_length, _FILES_API_MAX_SIZE))
    else:
      self._buffer.append(data)
      self._size += data_length

    if self._size > self._flush_size:
      self.flush()

  def flush(self):
    """Flush pool contents."""
    # Write data to in-memory buffer first.
    buf = cStringIO.StringIO()
    with records.RecordsWriter(buf) as w:
      for record in self._buffer:
        w.write(record)
      w._pad_block()
    str_buf = buf.getvalue()
    buf.close()

    if not self._exclusive and len(str_buf) > _FILES_API_MAX_SIZE:
      # Shouldn't really happen because of flush size.
      raise errors.Error(
          "Buffer too big. Can't write more than %s bytes in one request: "
          "risk of writes interleaving. Got: %s" %
          (_FILES_API_MAX_SIZE, len(str_buf)))

    # Write data to file.
    start_time = time.time()
    with files.open(self._filename, "a", exclusive_lock=self._exclusive) as f:
      f.write(str_buf)
      if self._ctx:
        operation.counters.Increment(
            COUNTER_IO_WRITE_BYTES, len(str_buf))(self._ctx)
    if self._ctx:
      operation.counters.Increment(
          COUNTER_IO_WRITE_MSEC,
          int((time.time() - start_time) * 1000))(self._ctx)

    # reset buffer
    self._buffer = []
    self._size = 0
    gc.collect()

  def __enter__(self):
    return self

  def __exit__(self, atype, value, traceback):
    self.flush()


class FileOutputWriterBase(OutputWriter):
  """Base class for all file output writers."""

  # Parameter to specify output sharding strategy.
  OUTPUT_SHARDING_PARAM = "output_sharding"

  # Output should not be sharded and should go into single file.
  OUTPUT_SHARDING_NONE = "none"

  # Separate file should be created for each input reader shard.
  OUTPUT_SHARDING_INPUT_SHARDS = "input"

  OUTPUT_FILESYSTEM_PARAM = "filesystem"

  GS_BUCKET_NAME_PARAM = "gs_bucket_name"
  GS_ACL_PARAM = "gs_acl"

  class _State(object):
    """Writer state. Stored in MapreduceState.

    State list all files which were created for the job.
    """

    def __init__(self, filenames, request_filenames):
      """State initializer.

      Args:
        filenames: writable or finalized filenames as returned by the files api.
        request_filenames: filenames as given to the files create api.
      """
      self.filenames = filenames
      self.request_filenames = request_filenames

    def to_json(self):
      return {
          "filenames": self.filenames,
          "request_filenames": self.request_filenames
      }

    @classmethod
    def from_json(cls, json):
      return cls(json["filenames"], json["request_filenames"])

  def __init__(self, filename, request_filename):
    """Init.

    Args:
      filename: writable filename from Files API.
      request_filename: in the case of GCS files, we need this to compute
        finalized filename. In the case of blobstore, this is useless as
        finalized filename can be retrieved from a Files API internal
        name mapping.
    """
    self._filename = filename
    self._request_filename = request_filename

  @classmethod
  def _get_output_sharding(cls, mapreduce_state=None, mapper_spec=None):
    """Get output sharding parameter value from mapreduce state or mapper spec.

    At least one of the parameters should not be None.

    Args:
      mapreduce_state: mapreduce state as model.MapreduceState.
      mapper_spec: mapper specification as model.MapperSpec
    """
    if mapper_spec:
      return _get_params(mapper_spec).get(
          FileOutputWriterBase.OUTPUT_SHARDING_PARAM,
          FileOutputWriterBase.OUTPUT_SHARDING_NONE).lower()
    if mapreduce_state:
      mapper_spec = mapreduce_state.mapreduce_spec.mapper
      return cls._get_output_sharding(mapper_spec=mapper_spec)
    raise errors.Error("Neither mapreduce_state nor mapper_spec specified.")

  @classmethod
  def validate(cls, mapper_spec):
    """Validates mapper specification.

    Args:
      mapper_spec: an instance of model.MapperSpec to validate.
    """
    if mapper_spec.output_writer_class() != cls:
      raise errors.BadWriterParamsError("Output writer class mismatch")

    output_sharding = cls._get_output_sharding(mapper_spec=mapper_spec)
    if (output_sharding != cls.OUTPUT_SHARDING_NONE and
        output_sharding != cls.OUTPUT_SHARDING_INPUT_SHARDS):
      raise errors.BadWriterParamsError(
          "Invalid output_sharding value: %s" % output_sharding)

    params = _get_params(mapper_spec)
    filesystem = cls._get_filesystem(mapper_spec)
    if filesystem not in files.FILESYSTEMS:
      raise errors.BadWriterParamsError(
          "Filesystem '%s' is not supported. Should be one of %s" %
          (filesystem, files.FILESYSTEMS))
    if filesystem == files.GS_FILESYSTEM:
      if not cls.GS_BUCKET_NAME_PARAM in params:
        raise errors.BadWriterParamsError(
            "%s is required for Google store filesystem" %
            cls.GS_BUCKET_NAME_PARAM)
    else:
      if params.get(cls.GS_BUCKET_NAME_PARAM) is not None:
        raise errors.BadWriterParamsError(
            "%s can only be provided for Google store filesystem" %
            cls.GS_BUCKET_NAME_PARAM)

  @classmethod
  def init_job(cls, mapreduce_state):
    """Initialize job-level writer state.

    Args:
      mapreduce_state: an instance of model.MapreduceState describing current
      job.
    """
    output_sharding = cls._get_output_sharding(mapreduce_state=mapreduce_state)
    if output_sharding == cls.OUTPUT_SHARDING_INPUT_SHARDS:
      # Each shard creates its own file to support shard retry.
      mapreduce_state.writer_state = cls._State([], []).to_json()
      return

    mapper_spec = mapreduce_state.mapreduce_spec.mapper
    params = _get_params(mapper_spec)
    mime_type = params.get("mime_type", "application/octet-stream")
    filesystem = cls._get_filesystem(mapper_spec=mapper_spec)
    bucket = params.get(cls.GS_BUCKET_NAME_PARAM)
    acl = params.get(cls.GS_ACL_PARAM)  # When None using default object ACLs.

    filename = (mapreduce_state.mapreduce_spec.name + "-" +
                mapreduce_state.mapreduce_spec.mapreduce_id + "-output")
    if bucket is not None:
      filename = "%s/%s" % (bucket, filename)
    request_filenames = [filename]
    filenames = [cls._create_file(filesystem, filename, mime_type, acl=acl)]
    mapreduce_state.writer_state = cls._State(
        filenames, request_filenames).to_json()

  @classmethod
  def _get_filesystem(cls, mapper_spec):
    return _get_params(mapper_spec).get(cls.OUTPUT_FILESYSTEM_PARAM, "").lower()

  @classmethod
  def _create_file(cls, filesystem, filename, mime_type, **kwargs):
    """Creates a file and returns its created filename."""
    if filesystem == files.BLOBSTORE_FILESYSTEM:
      return files.blobstore.create(mime_type, filename)
    elif filesystem == files.GS_FILESYSTEM:
      return files.gs.create("/gs/%s" % filename, mime_type, **kwargs)
    else:
      raise errors.BadWriterParamsError(
          "Filesystem '%s' is not supported" % filesystem)

  @classmethod
  def _get_finalized_filename(cls, fs, create_filename, request_filename):
    """Returns the finalized filename for the created filename."""
    if fs == "blobstore":
      return files.blobstore.get_file_name(
          files.blobstore.get_blob_key(create_filename))
    elif fs == "gs":
      return "/gs/" + request_filename
    else:
      raise errors.BadWriterParamsError(
          "Filesystem '%s' is not supported" % fs)

  @classmethod
  def finalize_job(cls, mapreduce_state):
    """See parent class."""
    output_sharding = cls._get_output_sharding(mapreduce_state=mapreduce_state)
    if output_sharding != cls.OUTPUT_SHARDING_INPUT_SHARDS:
      state = cls._State.from_json(mapreduce_state.writer_state)
      files.finalize(state.filenames[0])

  @classmethod
  def from_json(cls, state):
    """Creates an instance of the OutputWriter for the given json state.

    Args:
      state: The OutputWriter state as a json object (dict like).

    Returns:
      An instance of the OutputWriter configured using the values of json.
    """
    return cls(state["filename"], state["request_filename"])


  def to_json(self):
    """Returns writer state to serialize in json.

    Returns:
      A json-izable version of the OutputWriter state.
    """
    return {"filename": self._filename,
            "request_filename": self._request_filename}

  def _can_be_retried(self, tstate):
    """Inherit doc.

    Only shard with output per shard can be retried.
    """
    output_sharding = self._get_output_sharding(
        mapper_spec=tstate.mapreduce_spec.mapper)
    if output_sharding == self.OUTPUT_SHARDING_INPUT_SHARDS:
      return True
    return False

  @classmethod
  def create(cls, mapreduce_state, shard_state):
    """Create new writer for a shard.

    Args:
      mapreduce_state: an instance of model.MapreduceState describing current
        job.
      shard_state: an instance of mode.ShardState describing the shard
        outputing this file.

    Returns:
      an output writer instance for this shard.
    """
    output_sharding = cls._get_output_sharding(mapreduce_state=mapreduce_state)
    shard_number = shard_state.shard_number
    if output_sharding == cls.OUTPUT_SHARDING_INPUT_SHARDS:
      mapper_spec = mapreduce_state.mapreduce_spec.mapper
      params = _get_params(mapper_spec)
      mime_type = params.get("mime_type", "application/octet-stream")
      filesystem = cls._get_filesystem(mapper_spec=mapper_spec)
      bucket = params.get(cls.GS_BUCKET_NAME_PARAM)
      acl = params.get(cls.GS_ACL_PARAM)  # When None using default object ACLs.
      retries = shard_state.retries

      request_filename = (
          mapreduce_state.mapreduce_spec.name + "-" +
          mapreduce_state.mapreduce_spec.mapreduce_id + "-output-" +
          str(shard_number) + "-retry-" + str(retries))
      if bucket is not None:
        request_filename = "%s/%s" % (bucket, request_filename)
      filename = cls._create_file(filesystem,
                                  request_filename,
                                  mime_type,
                                  acl=acl)
    else:
      state = cls._State.from_json(mapreduce_state.writer_state)
      filename = state.filenames[0]
      request_filename = state.request_filenames[0]
    return cls(filename, request_filename)

  def finalize(self, ctx, shard_state):
    """Finalize writer shard-level state.

    Args:
      ctx: an instance of context.Context.
      shard_state: shard state.
    """
    mapreduce_spec = ctx.mapreduce_spec
    output_sharding = self.__class__._get_output_sharding(
        mapper_spec=mapreduce_spec.mapper)
    if output_sharding == self.OUTPUT_SHARDING_INPUT_SHARDS:
      filesystem = self._get_filesystem(mapreduce_spec.mapper)
      files.finalize(self._filename)
      finalized_filenames = [self._get_finalized_filename(
          filesystem, self._filename, self._request_filename)]

      shard_state.writer_state = self._State(
          finalized_filenames, []).to_json()

      # Log to help debug empty blobstore key.
      # b/8302363
      if filesystem == "blobstore":
        logging.info(
            "Shard %s-%s finalized blobstore file %s.",
            mapreduce_spec.mapreduce_id,
            shard_state.shard_number,
            self._filename)
        logging.info("Finalized name is %s.", finalized_filenames[0])

  @classmethod
  def get_filenames(cls, mapreduce_state):
    """See parent class."""
    finalized_filenames = []
    output_sharding = cls._get_output_sharding(mapreduce_state=mapreduce_state)
    if output_sharding != cls.OUTPUT_SHARDING_INPUT_SHARDS:
      if (mapreduce_state.writer_state and mapreduce_state.result_status ==
          model.MapreduceState.RESULT_SUCCESS):
        state = cls._State.from_json(mapreduce_state.writer_state)
        filesystem = cls._get_filesystem(mapreduce_state.mapreduce_spec.mapper)
        finalized_filenames = [cls._get_finalized_filename(
            filesystem, state.filenames[0], state.request_filenames[0])]
    else:
      shards = model.ShardState.find_all_by_mapreduce_state(mapreduce_state)
      for shard in shards:
        if shard.result_status == model.ShardState.RESULT_SUCCESS:
          state = cls._State.from_json(shard.writer_state)
          finalized_filenames.append(state.filenames[0])

    return finalized_filenames


class FileOutputWriter(FileOutputWriterBase):
  """An implementation of OutputWriter which outputs data into file."""

  def write(self, data):
    """Write data.

    Args:
      data: actual data yielded from handler. Type is writer-specific.
    """
    ctx = context.get()
    if ctx.get_pool("file_pool") is None:
      ctx.register_pool("file_pool", _FilePool(ctx=ctx))
    ctx.get_pool("file_pool").append(self._filename, str(data))


class FileRecordsOutputWriter(FileOutputWriterBase):
  """A File OutputWriter which outputs data using leveldb log format."""

  @classmethod
  def validate(cls, mapper_spec):
    """Validates mapper specification.

    Args:
      mapper_spec: an instance of model.MapperSpec to validate.
    """
    if cls.OUTPUT_SHARDING_PARAM in _get_params(mapper_spec):
      raise errors.BadWriterParamsError(
          "output_sharding should not be specified for %s" % cls.__name__)
    super(FileRecordsOutputWriter, cls).validate(mapper_spec)

  @classmethod
  def _get_output_sharding(cls, mapreduce_state=None, mapper_spec=None):
    return cls.OUTPUT_SHARDING_INPUT_SHARDS

  def write(self, data):
    """Write data.

    Args:
      data: actual data yielded from handler. Type is writer-specific.
    """
    ctx = context.get()
    if ctx.get_pool("records_pool") is None:
      ctx.register_pool("records_pool",
                        # we can have exclusive pool because we create one
                        # file per shard.
                        RecordsPool(self._filename, ctx=ctx, exclusive=True))
    ctx.get_pool("records_pool").append(str(data))


class KeyValueFileOutputWriter(FileRecordsOutputWriter):
  """A file output writer for KeyValue records."""

  def write(self, data):
    if len(data) != 2:
      logging.error("Got bad tuple of length %d (2-tuple expected): %s",
                    len(data), data)

    try:
      key = str(data[0])
      value = str(data[1])
    except TypeError:
      logging.error("Expecting a tuple, but got %s: %s",
                    data.__class__.__name__, data)

    proto = file_service_pb.KeyValue()
    proto.set_key(key)
    proto.set_value(value)
    FileRecordsOutputWriter.write(self, proto.Encode())


class BlobstoreOutputWriterBase(FileOutputWriterBase):
  """A base class of OutputWriter which outputs data into blobstore."""

  @classmethod
  def _get_filesystem(cls, mapper_spec):
    return "blobstore"


class BlobstoreOutputWriter(FileOutputWriter, BlobstoreOutputWriterBase):
  """An implementation of OutputWriter which outputs data into blobstore."""


class BlobstoreRecordsOutputWriter(FileRecordsOutputWriter,
                                   BlobstoreOutputWriterBase):
  """An OutputWriter which outputs data into records format."""


class KeyValueBlobstoreOutputWriter(KeyValueFileOutputWriter,
                                    BlobstoreOutputWriterBase):
  """Output writer for KeyValue records files in blobstore."""


class _GoogleCloudStorageOutputWriter(OutputWriter):
  """Output writer to Google Cloud Storage using the cloudstorage library.

  This class is expected to be subclassed with a writer that applies formatting
  to user-level records.

  Required configuration in the mapper_spec.output_writer dictionary.
    BUCKET_NAME_PARAM: name of the bucket to use (with no extra delimiters or
      suffixes such as directories. Directories/prefixes can be specifed as
      part of the NAMING_FORMAT_PARAM).

  Optional configuration in the mapper_spec.output_writer dictionary:
    ACL_PARAM: acl to apply to new files, else bucket default used.
    NAMING_FORMAT_PARAM: prefix format string for the new files (there is no
      required starting slash, expected formats would look like
      "directory/basename...", any starting slash will be treated as part of
      the file name) that should use the following substitutions:
        $name - the name of the job
        $id - the id assigned to the job
        $num - the shard number
        $retry - the retry count for this shard
      If there is more than one shard $num must be used. An arbitrary suffix may
      be applied by the writer.
    CONTENT_TYPE_PARAM: mime type to apply on the files. If not provided, Google
      Cloud Storage will apply its default.
  """

  # Supported parameters
  BUCKET_NAME_PARAM = "bucket_name"
  ACL_PARAM = "acl"
  NAMING_FORMAT_PARAM = "naming_format"
  CONTENT_TYPE_PARAM = "content_type"

  # Default settings
  DEFAULT_NAMING_FORMAT = "$name-$id-output-$num-retry-$retry"

  # Internal parameters
  _ACCOUNT_ID_PARAM = "account_id"
  _JSON_FILENAME = "filename"
  _JSON_GCS_BUFFER = "buffer"

  # writer_spec only used by subclasses, pylint: disable=unused-argument
  def __init__(self, streaming_buffer, filename, writer_spec=None):
    """Initialize a GoogleCloudStorageOutputWriter instance.

    Args:
      streaming_buffer: an instance of writable buffer from cloudstorage_api.
      filename: the GCS client filename this writer is writing to.
      writer_spec: the specification for the writer, useful for subclasses.
    """
    self._streaming_buffer = streaming_buffer
    self._filename = filename

  @classmethod
  def _generate_filename(cls, writer_spec, name, job_id, num,
                         retry):
    """Generates a filename for a shard / retry count.

    Args:
      writer_spec: specification dictionary for the output writer.
      name: name of the job.
      job_id: the ID number assigned to the job.
      num: shard number.
      retry: the retry number.

    Returns:
      a string containing the filename.

    Raises:
      BadWriterParamsError if the template contains any errors such as invalid
        syntax or contains unknown substitution placeholders.
    """
    naming_format = writer_spec.get(cls.NAMING_FORMAT_PARAM,
                                    cls.DEFAULT_NAMING_FORMAT)
    template = string.Template(naming_format)
    try:
      # Check that template doesn't use undefined mappings and is formatted well
      return template.substitute(name=name, id=job_id, num=num, retry=retry)
    except ValueError, error:
      raise errors.BadWriterParamsError("Naming template is bad, %s" % (error))
    except KeyError, error:
      raise errors.BadWriterParamsError("Naming template '%s' has extra "
                                        "mappings, %s" % (naming_format, error))

  @classmethod
  def validate(cls, mapper_spec):
    """Validate mapper specification.

    Args:
      mapper_spec: an instance of model.MapperSpec.

    Raises:
      BadWriterParamsError if the specification is invalid for any reason such
        as missing the bucket name or providing an invalid bucket name.
    """
    writer_spec = _get_params(mapper_spec, allow_old=False)

    # Bucket Name is required
    if cls.BUCKET_NAME_PARAM not in writer_spec:
      raise errors.BadWriterParamsError(
          "%s is required for Google Cloud Storage" %
          cls.BUCKET_NAME_PARAM)
    try:
      cloudstorage.validate_bucket_name(
          writer_spec[cls.BUCKET_NAME_PARAM])
    except ValueError, error:
      raise errors.BadWriterParamsError("Bad bucket name, %s" % (error))

    # Validate the naming format does not throw any errors using dummy values
    cls._generate_filename(writer_spec, "name", "id", 0, 0)

  @classmethod
  def create(cls, mapreduce_state, shard_state):
    """Create new writer for a shard.

    Args:
      mapreduce_state: an instance of model.MapreduceState describing current
        job. State can NOT be modified.
      shard_state: an instance of model.ShardState.

    Returns:
      an output writer for the requested shard.
    """
    # Get the current job state
    job_spec = mapreduce_state.mapreduce_spec
    writer_spec = _get_params(job_spec.mapper, allow_old=False)

    # Determine parameters
    key = cls._generate_filename(writer_spec, job_spec.name,
                                 job_spec.mapreduce_id,
                                 shard_state.shard_number, shard_state.retries)
    # GoogleCloudStorage format for filenames, Initial slash is required
    filename = "/%s/%s" % (writer_spec[cls.BUCKET_NAME_PARAM], key)

    content_type = writer_spec.get(cls.CONTENT_TYPE_PARAM, None)

    options = {}
    if cls.ACL_PARAM in writer_spec:
      options["x-goog-acl"] = writer_spec.get(cls.ACL_PARAM)

    account_id = writer_spec.get(cls._ACCOUNT_ID_PARAM, None)

    writer = cloudstorage.open(filename, mode="w",
                               content_type=content_type,
                               options=options,
                               _account_id=account_id)

    return cls(writer, filename, writer_spec=writer_spec)

  @classmethod
  def _get_filename(cls, shard_state):
    return shard_state.writer_state["filename"]

  @classmethod
  def get_filenames(cls, mapreduce_state):
    filenames = []
    for shard in model.ShardState.find_all_by_mapreduce_state(mapreduce_state):
      if shard.result_status == model.ShardState.RESULT_SUCCESS:
        filenames.append(cls._get_filename(shard))
    return filenames

  @classmethod
  def from_json(cls, state):
    return cls(pickle.loads(state[cls._JSON_GCS_BUFFER]),
               state[cls._JSON_FILENAME])

  def to_json(self):
    return {self._JSON_GCS_BUFFER: pickle.dumps(self._streaming_buffer),
            self._JSON_FILENAME: self._filename}

  def write(self, data):
    """Write data to the GoogleCloudStorage file.

    Args:
      data: string containing the data to be written.
    """
    start_time = time.time()
    self._streaming_buffer.write(data)
    ctx = context.get()
    operation.counters.Increment(COUNTER_IO_WRITE_BYTES, len(data))(ctx)
    operation.counters.Increment(
        COUNTER_IO_WRITE_MSEC, int((time.time() - start_time) * 1000))(ctx)

  def finalize(self, ctx, shard_state):
    self._streaming_buffer.close()
    # Save filename to shard_state
    shard_state.writer_state = {"filename": self._filename}


class _GoogleCloudStorageRecordOutputWriter(_GoogleCloudStorageOutputWriter):
  """Write data to the Google Cloud Storage file using LevelDB format.

  Data are written to cloudstorage in record format. On writer serializaton,
  up to 32KB padding may be added to ensure the next slice aligns with
  record boundary.

  See the _GoogleCloudStorageOutputWriter for configuration options.
  """

  def __init__(self,
               streaming_buffer,
               filename,
               writer_spec=None):
    """Initialize a CloudStorageOutputWriter instance.

    Args:
      streaming_buffer: an instance of writable buffer from cloudstorage_api.
      filename: the GCS client filename this writer is writing to.
      writer_spec: the specification for the writer.
    """
    super(_GoogleCloudStorageRecordOutputWriter, self).__init__(
        streaming_buffer, filename, writer_spec)
    self._record_writer = records.RecordsWriter(
        super(_GoogleCloudStorageRecordOutputWriter, self))

  def to_json(self):
    # Pad if this is not the to_json call after finalization.
    if not self._streaming_buffer.closed:
      self._record_writer._pad_block()
    return super(_GoogleCloudStorageRecordOutputWriter, self).to_json()

  def write(self, data):
    """Write a single record of data to the file using LevelDB format.

    Args:
      data: string containing the data to be written.
    """
    self._record_writer.write(data)

