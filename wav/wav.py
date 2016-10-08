#https://ccrma.stanford.edu/courses/422/projects/WaveFormat/
#Note: seems to calc chunksize+2 over source file? (wav's still readable)
import _io, struct, os

class wav:
  """Dirty wav class"""
  
  ChunkID         = b'RIFF'
  Format          = b'WAVE'
  SubChunk1ID     = b'fmt '
  SubChunk1Size   = 16 #for PCM
  SubChunk2ID     = b'data'
  __header_smask  = '4sL4s4sLHHLLHH4sL'
  __header_slist  = ['4s','L','4s','4s','L','H','H','L','L','H','H','4s','L']

  def __init__(self, filename, SampleRate=8000, BitsPerSample=8, NumChannels=1, NumSamples=0):
    """Create a wav object from file (ignore other args), or empty with the specified args"""
    self.filename = filename
    try:
      file = _io.open(filename, 'rb')
      header_raw = file.read(44)
      header_chunks = struct.unpack(self.__header_smask, header_raw)
      d, d, d, d, d, \
      self.AudioFormat, \
      self.NumChannels, \
      self.SampleRate, \
      d, \
      self.BlockAlign, \
      self.BitsPerSample, \
      d,d = header_chunks
      self.data = file.readall()
      file.close()
      if header_chunks[0] != self.ChunkID \
          or header_chunks[2] != self.Format \
          or header_chunks[3] != self.SubChunk1ID \
          or header_chunks[11] != self.SubChunk2ID:
        raise TypeError('{} is not a wav file'.format(filename))
      if self.AudioFormat != 1: raise TypeError('Compressed wav files not supported')
    except OSError:
      if not type(SampleRateBits) == type(BitsPerSample) == type(NumChannels) == int:
        raise TypeError('SampleRateBits, BitsPerSample & NumChannels must be integers')
      if BitsPerSample%8 != 0: 
        raise ValueError('BitsPerSample must be a multiple of 8')
      self.AudioFormat = 1 #PCM
      self.NumChannels = NumChannels
      self.SampleRate = SampleRate
      self.BlockAlign = NumChannels * int(BitsPerSample/8)
      self.BitsPerSample = BitsPerSample
      self.data = bytes(NumSamples * self.BlockAlign)
    self.__sample_mask = {1:'B',2:'H',4:'I',8:'Q'}[int(self.BitsPerSample/8)]
    self.__sample_mask = self.__sample_mask * self.NumChannels

  def SubChunk2Size(self):
    """Return SubChunk2Size (part of wav header)"""
    return len(self) + self.NumChannels + int(self.BitsPerSample/8)
  
  def ChunkSize(self):
    """Return ChunkSize (part of wav header)"""
    return 36 + self.SubChunk2Size()

  def ByteRate(self):
    """Return ByteRate"""
    return self.SampleRate * self.NumChannels * int(self.BitsPerSample/8)
  
  def __get_header_values(self):
    """Return list of header values, matched to self.__header_slist"""
    return [self.ChunkID, \
            self.ChunkSize(), \
            self.Format, \
            self.SubChunk1ID, \
            self.SubChunk1Size, \
            self.AudioFormat, \
            self.NumChannels, \
            self.SampleRate, \
            self.ByteRate(), \
            self.BlockAlign, \
            self.BitsPerSample, \
            self.SubChunk2ID, \
            self.SubChunk2Size()]

  def write(self, overwrite=False):
    """Write file to disk"""
    #dirty, dirty hack
    cwd = os.listdir()[0][0:3] if self.filename[0:3] not in ['0:/','1:/'] else ''
    if cwd+self.filename in os.listdir() and not overwrite: raise IOError('File exists')
    file = _io.open(cwd+self.filename,'wb')
    header = b''
    for t in zip(self.__header_slist, self.__get_header_values()):
      header += struct.pack(t[0], t[1])
    file.write(header)
    file.write(self.data)
    file.close()
    return len(header)+len(self.data)
    
  def append(self, other):
    """Append frame, as tuple of NumChannel samples, of size BitsPerSample)"""
    if self.__validate_frame(other):
      samplebytes = b''
      for sample in other:
        samplebytes += bytes([sample])
      self.data = self.data + samplebytes
    return
    
  def __len__(self):
    """Return length, number of frames"""
    return int(len(self.data)/self.BlockAlign)
        
  def __iter__(self):
    """Iterate over frames, as tuples of len NumChannels"""
    p=-1
    while p < (len(self)/self.BlockAlign)-self.BlockAlign:
      p += 1
      chunk = self.data[p * self.BlockAlign:(p * self.BlockAlign) + self.BlockAlign]
      yield struct.unpack(self.__sample_mask, chunk)
    else:
      raise StopIteration

  def __getitem__(self, key):
    """Return frame, as tuple of len NumChannels"""
    if type(key) != int: raise TypeError
    if key > len(self): raise KeyError
    chunk = self.data[key * self.BlockAlign:(key * self.BlockAlign) + self.BlockAlign]
    return struct.unpack(self.__sample_mask, chunk)

  def __validate_frame(self, other):
    """Validate a frame against wav format"""
    #this is not nice
    if not type(other) == tuple: 
      raise TypeError('sample must be type tuple')
    elif not len(other) == self.NumChannels: 
      raise ValueError('{} channel wav requires tuple of len {}'.format(self.NumChannels,self.NumChannels)) 
    else:
      for indx,sample in enumerate(other):
        if not type(sample) == int: 
          raise TypeError('discrete sample must be type int')
        if sample >= 256**int(self.BitsPerSample/8): 
          raise ValueError('sample[{}]=({}), > max. sample size({})'.format(indx,sample,(256**self.BytesPerSample)-1))
        if sample < 0: 
          raise ValueError('sample[{}]={}, < zero'.format(indx,sample))
      else:
        return True