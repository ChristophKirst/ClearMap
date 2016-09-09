#!/usr/bin/env python
# encoding: utf-8
"""
Interface to NRRD volumetric image data files.

The interface is based on nrrd.py, an all-python (and numpy) 
implementation for reading and writing nrrd files.
See http://teem.sourceforge.net/nrrd/format.html for the specification.

Example:
    >>> import os, numpy
    >>> import ClearMap.Settings as settings
    >>> import ClearMap.IO.NRRD as nrrd
    >>> filename = os.path.join(settings.ClearMapPath, 'Test/Data/Nrrd/test.nrrd');
    >>> data = nrrd.readData(filename);  
    >>> print data.shape
    (20, 50, 10)

Author
""""""
    Copyright 2011 Maarten Everts and David Hammond.

    Modified to integrate into ClearMap framework by Christoph Kirst, The Rockefeller University, New York City, 2015
"""

import numpy as np
import gzip
import bz2
import os.path
from datetime import datetime

import ClearMap.IO as io

class NrrdError(Exception):
    """Exceptions for Nrrd class."""
    pass

#This will help prevent loss of precision
#IEEE754-1985 standard says that 17 decimal digits is enough in all cases.
def _convert_to_reproducible_floatingpoint( x ):
    if type(x) == float:
        value = '{:.16f}'.format(x).rstrip('0').rstrip('.') # Remove trailing zeros, and dot if at end
    else:
        value = str(x)
    return value

_TYPEMAP_NRRD2NUMPY = {
    'signed char': 'i1',
    'int8': 'i1',
    'int8_t': 'i1',
    'uchar': 'u1',
    'unsigned char': 'u1',
    'uint8': 'u1',
    'uint8_t': 'u1',
    'short': 'i2',
    'short int': 'i2',
    'signed short': 'i2',
    'signed short int': 'i2',
    'int16': 'i2',
    'int16_t': 'i2',
    'ushort': 'u2',
    'unsigned short': 'u2',
    'unsigned short int': 'u2',
    'uint16': 'u2',
    'uint16_t': 'u2',
    'int': 'i4',
    'signed int': 'i4',
    'int32': 'i4',
    'int32_t': 'i4',
    'uint': 'u4',
    'unsigned int': 'u4',
    'uint32': 'u4',
    'uint32_t': 'u4',
    'longlong': 'i8',
    'long long': 'i8',
    'long long int': 'i8',
    'signed long long': 'i8',
    'signed long long int': 'i8',
    'int64': 'i8',
    'int64_t': 'i8',
    'ulonglong': 'u8',
    'unsigned long long': 'u8',
    'unsigned long long int': 'u8',
    'uint64': 'u8',
    'uint64_t': 'u8',
    'float': 'f4',
    'double': 'f8',
    'block': 'V'
}

_TYPEMAP_NUMPY2NRRD = {
    'i1': 'int8',
    'u1': 'uint8',
    'i2': 'int16',
    'u2': 'uint16',
    'i4': 'int32',
    'u4': 'uint32',
    'i8': 'int64',
    'u8': 'uint64',
    'f4': 'float',
    'f8': 'double',
    'V': 'block'
}

_NUMPY2NRRD_ENDIAN_MAP = {
    '<': 'little',
    'L': 'little',
    '>': 'big',
    'B': 'big'
}

def parse_nrrdvector(inp):
    """Parse a vector from a nrrd header, return a list."""
    assert inp[0] == '(', "Vector should be enclosed by parenthesis."
    assert inp[-1] == ')', "Vector should be enclosed by parenthesis."
    return [_convert_to_reproducible_floatingpoint(x) for x in inp[1:-1].split(',')]

def parse_optional_nrrdvector(inp):
    """Parse a vector from a nrrd header that can also be none."""
    if (inp == "none"):
        return inp
    else:
        return parse_nrrdvector(inp)

_NRRD_FIELD_PARSERS = {
    'dimension': int,
    'type': str,
    'sizes': lambda fieldValue: [int(x) for x in fieldValue.split()],
    'endian': str,
    'encoding': str,
    'min': float,
    'max': float,
    'oldmin': float,
    'old min': float,
    'oldmax': float,
    'old max': float,
    'lineskip': int,
    'line skip': int,
    'byteskip': int,
    'byte skip': int,
    'content': str,
    'sample units': str,
    'datafile': str,
    'data file': str,
    'spacings': lambda fieldValue: [_convert_to_reproducible_floatingpoint(x) for x in fieldValue.split()],
    'thicknesses': lambda fieldValue: [_convert_to_reproducible_floatingpoint(x) for x in fieldValue.split()],
    'axis mins': lambda fieldValue: [_convert_to_reproducible_floatingpoint(x) for x in fieldValue.split()],
    'axismins': lambda fieldValue: [_convert_to_reproducible_floatingpoint(x) for x in fieldValue.split()],
    'axis maxs': lambda fieldValue: [_convert_to_reproducible_floatingpoint(x) for x in fieldValue.split()],
    'axismaxs': lambda fieldValue: [_convert_to_reproducible_floatingpoint(x) for x in fieldValue.split()],
    'centerings': lambda fieldValue: [str(x) for x in fieldValue.split()],
    'labels': lambda fieldValue: [str(x) for x in fieldValue.split()],
    'units': lambda fieldValue: [str(x) for x in fieldValue.split()],
    'kinds': lambda fieldValue: [str(x) for x in fieldValue.split()],
    'space': str,
    'space dimension': int,
    'space units': lambda fieldValue: [str(x) for x in fieldValue.split()],
    'space origin': parse_nrrdvector,
    'space directions': lambda fieldValue:
                        [parse_optional_nrrdvector(x) for x in fieldValue.split()],
    'measurement frame': lambda fieldValue:
                        [parse_nrrdvector(x) for x in fieldValue.split()],
}

_NRRD_REQUIRED_FIELDS = ['dimension', 'type', 'encoding', 'sizes']

# The supported field values
_NRRD_FIELD_ORDER = [
    'type',
    'dimension',
    'space dimension',
    'space',
    'sizes',
    'space directions',
    'kinds',
    'endian',
    'encoding',
    'min',
    'max',
    'oldmin',
    'old min',
    'oldmax',
    'old max',
    'content',
    'sample units',
    'spacings',
    'thicknesses',
    'axis mins',
    'axismins',
    'axis maxs',
    'axismaxs',
    'centerings',
    'labels',
    'units',
    'space units',
    'space origin',
    'measurement frame',
    'data file']


def _determine_dtype(fields):
    """Determine the numpy dtype of the data."""
    # Check whether the required fields are there
    for field in _NRRD_REQUIRED_FIELDS:
        if field not in fields:
            raise NrrdError('Nrrd header misses required field: "%s".' % (field))
    # Process the data type
    np_typestring = _TYPEMAP_NRRD2NUMPY[fields['type']]
    if np.dtype(np_typestring).itemsize > 1:
        if 'endian' not in fields:
            raise NrrdError('Nrrd header misses required field: "endian".')
        if fields['endian'] == 'big':
            np_typestring = '>' + np_typestring
        elif fields['endian'] == 'little':
            np_typestring = '<' + np_typestring

    return np.dtype(np_typestring)


def _read_data(fields, filehandle, filename=None):
    """Read the actual data into a numpy structure."""
    data = np.zeros(0)
    # Determine the data type from the fields
    dtype = _determine_dtype(fields)
    # determine byte skip, line skip, and data file (there are two ways to write them)
    lineskip = fields.get('lineskip', fields.get('line skip', 0))
    byteskip = fields.get('byteskip', fields.get('byte skip', 0))
    datafile = fields.get("datafile", fields.get("data file", None))
    datafilehandle = filehandle
    if datafile is not None:
        # If the datafile path is absolute, don't muck with it. Otherwise
        # treat the path as relative to the directory in which the detached
        # header is in
        if os.path.isabs(datafile):
            datafilename = datafile
        else:
            datafilename = os.path.join(os.path.dirname(filename), datafile)
        datafilehandle = open(datafilename,'rb')
    numPixels=np.array(fields['sizes']).prod()
    totalbytes = dtype.itemsize * numPixels

    if fields['encoding'] == 'raw':
        if byteskip == -1: # This is valid only with raw encoding
            datafilehandle.seek(-totalbytes, 2)
        else:
            for _ in range(lineskip):
                datafilehandle.readline()
            datafilehandle.read(byteskip)
        data = np.fromfile(datafilehandle, dtype)
    elif fields['encoding'] == 'gzip' or\
         fields['encoding'] == 'gz':
        gzipfile = gzip.GzipFile(fileobj=datafilehandle)
        # Again, unfortunately, np.fromfile does not support
        # reading from a gzip stream, so we'll do it like this.
        # I have no idea what the performance implications are.
        data = np.fromstring(gzipfile.read(), dtype)
    elif fields['encoding'] == 'bzip2' or\
         fields['encoding'] == 'bz2':
        bz2file = bz2.BZ2File(fileobj=datafilehandle)
        # Again, unfortunately, np.fromfile does not support
        # reading from a gzip stream, so we'll do it like this.
        # I have no idea what the performance implications are.
        data = np.fromstring(bz2file.read(), dtype)
    else:
        raise NrrdError('Unsupported encoding: "%s"' % fields['encoding'])

    if numPixels != data.size:
       raise NrrdError('ERROR: {0}-{1}={2}'.format(numPixels,data.size,numPixels-data.size))

    # dkh : eliminated need to reverse order of dimensions. nrrd's
    # data layout is same as what numpy calls 'Fortran' order,
    shape_tmp = list(fields['sizes'])
    data = np.reshape(data, tuple(shape_tmp), order='F')
    return data

def _validate_magic_line(line):
    """For NRRD files, the first four characters are always "NRRD", and
    remaining characters give information about the file format version
    """
    if not line.startswith('NRRD'):
        raise NrrdError('Missing magic "NRRD" word. Is this an NRRD file?')
    try:
        if int(line[4:]) > 5:
            raise NrrdError('NRRD file version too new for this library.')
    except:
        raise NrrdError('Invalid NRRD magic line: %s' % (line,))
    return len(line)

def readHeader(filename):
    """Parse the fields in the nrrd header

    nrrdfile can be any object which supports the iterator protocol and
    returns a string each time its next() method is called — file objects and
    list objects are both suitable. If csvfile is a file object, it must be
    opened with the ‘b’ flag on platforms where that makes a difference
    (e.g. Windows)

    >>> readHeader(("NRRD0005", "type: float", "dimension: 3"))
    {'type': 'float', 'dimension': 3, 'keyvaluepairs': {}}
    >>> readHeader(("NRRD0005", "my extra info:=my : colon-separated : values"))
    {'keyvaluepairs': {'my extra info': 'my : colon-separated : values'}}
    """
    
    if isinstance(filename, basestring):
        nrrdfile = open(filename,'rb');
    else:
        nrrdfile = filename;
    
    
    # Collect number of bytes in the file header (for seeking below)
    headerSize = 0

    it = iter(nrrdfile)

    headerSize += _validate_magic_line(next(it).decode('ascii'))

    header = { 'keyvaluepairs': {} }
    for raw_line in it:
        headerSize += len(raw_line)
        raw_line = raw_line.decode('ascii')

        # Trailing whitespace ignored per the NRRD spec
        line = raw_line.rstrip()

        # Comments start with '#', no leading whitespace allowed
        if line.startswith('#'):
            continue
        # Single blank line separates the header from the data
        if line == '':
            break

        # Handle the <key>:=<value> lines first since <value> may contain a
        # ': ' which messes up the <field>: <desc> parsing
        key_value = line.split(':=', 1)
        if len(key_value) is 2:
            key, value = key_value
            # TODO: escape \\ and \n ??
            # value.replace(r'\\\\', r'\\').replace(r'\n', '\n')
            header['keyvaluepairs'][key] = value
            continue

        # Handle the "<field>: <desc>" lines.
        field_desc = line.split(': ', 1)
        if len(field_desc) is 2:
            field, desc = field_desc
            ## preceeding and suffixing white space should be ignored.
            field = field.rstrip().lstrip()
            desc = desc.rstrip().lstrip()
            if field not in _NRRD_FIELD_PARSERS:
                raise NrrdError('Unexpected field in nrrd header: "%s".' % field)
            if field in header.keys():
                raise NrrdError('Duplicate header field: "%s"' % field)
            header[field] = _NRRD_FIELD_PARSERS[field](desc)
            continue

        # Should not reach here
        raise NrrdError('Invalid header line: "%s"' % line)

    # line reading was buffered; correct file pointer to just behind header:
    nrrdfile.seek(headerSize)

    return header


def readData(filename, **args):
    """Read nrrd file image data
    
    Arguments:
        filename (str): file name as regular expression
        x,y,z (tuple): data range specifications
    
    Returns:
        array: image data
    """

    with open(filename,'rb') as filehandle:
        header = readHeader(filehandle)
        #print header
        data = _read_data(header, filehandle, filename)
        #return (data, header)
        #return data.transpose([1,0,2]);
        data = io.readData(data, **args);
        return data;
    



def _format_nrrd_list(fieldValue) :
    return ' '.join([_convert_to_reproducible_floatingpoint(x) for x in fieldValue])

def _format_nrrdvector(v) :
    return '(' + ','.join([_convert_to_reproducible_floatingpoint(x) for x in v]) + ')'

def _format_optional_nrrdvector(v):
    if (v == 'none') :
        return 'none'
    else :
        return _format_nrrdvector(v)

_NRRD_FIELD_FORMATTERS = {
    'dimension': str,
    'type': str,
    'sizes': _format_nrrd_list,
    'endian': str,
    'encoding': str,
    'min': str,
    'max': str,
    'oldmin': str,
    'old min': str,
    'oldmax': str,
    'old max': str,
    'lineskip': str,
    'line skip': str,
    'byteskip': str,
    'byte skip': str,
    'content': str,
    'sample units': str,
    'datafile': str,
    'data file': str,
    'spacings': _format_nrrd_list,
    'thicknesses': _format_nrrd_list,
    'axis mins': _format_nrrd_list,
    'axismins': _format_nrrd_list,
    'axis maxs': _format_nrrd_list,
    'axismaxs': _format_nrrd_list,
    'centerings': _format_nrrd_list,
    'labels': _format_nrrd_list,
    'units': _format_nrrd_list,
    'kinds': _format_nrrd_list,
    'space': str,
    'space dimension': str,
    'space units': _format_nrrd_list,
    'space origin': _format_nrrdvector,
    'space directions': lambda fieldValue: ' '.join([_format_optional_nrrdvector(x) for x in fieldValue]),
    'measurement frame': lambda fieldValue: ' '.join([_format_optional_nrrdvector(x) for x in fieldValue]),
}


def _write_data(data, filehandle, options):
    # Now write data directly
    #rawdata = data.transpose([2,0,1]).tostring(order = 'C')
    rawdata = data.transpose([2,1,0]).tostring(order = 'C');
    if options['encoding'] == 'raw':
        filehandle.write(rawdata)
    elif options['encoding'] == 'gzip':
        gzfileobj = gzip.GzipFile(fileobj = filehandle)
        gzfileobj.write(rawdata)
        gzfileobj.close()
    elif options['encoding'] == 'bz2':
        bz2fileobj = bz2.BZ2File(fileobj = filehandle)
        bz2fileobj.write(rawdata)
        bz2fileobj.close()
    else:
        raise NrrdError('Unsupported encoding: "%s"' % options['encoding'])


def writeData(filename, data, options={}, separateHeader=False, x = all, y = all, z = all):
    """Write data to nrrd file
    
    Arguments:
        filename (str): file name as regular expression
        data (array): image data
        options (dict): options dictionary
        separateHeader (bool): write a separate header file
    
    Returns:
        str: nrrd output file name

    To sample data use `options['spacings'] = [s1, s2, s3]` for
    3d data with sampling deltas `s1`, `s2`, and `s3` in each dimension.
    """
    
    data = io.dataToRange(data, x = x, y = y, z = z);
    
    # Infer a number of fields from the ndarray and ignore values
    # in the options dictionary.
    options['type'] = _TYPEMAP_NUMPY2NRRD[data.dtype.str[1:]]
    if data.dtype.itemsize > 1:
        options['endian'] = _NUMPY2NRRD_ENDIAN_MAP[data.dtype.str[:1]]
    # if 'space' is specified 'space dimension' can not. See http://teem.sourceforge.net/nrrd/format.html#space
    if 'space' in options.keys() and 'space dimension' in options.keys():
        del options['space dimension']
    options['dimension'] = data.ndim
    dsize = list(data.shape);
    #dsize[0:2] = [dsize[1], dsize[0]];
    options['sizes'] = dsize;

    # The default encoding is 'gzip'
    if 'encoding' not in options:
        options['encoding'] = 'gzip'

    # A bit of magic in handling options here.
    # If *.nhdr filename provided, this overrides `separate_header=False`
    # If *.nrrd filename provided AND separate_header=True, separate files
    #   written.
    # For all other cases, header & data written to same file.
    if filename[-5:] == '.nhdr':
        separate_header = True
        if 'data file' not in options:
            datafilename = filename[:-4] + str('raw')
            if options['encoding'] == 'gzip':
                datafilename += '.gz'
            options['data file'] = datafilename
        else:
            datafilename = options['data file']
    elif filename[-5:] == '.nrrd' and separate_header:
        separate_header = True
        datafilename = filename
        filename = filename[:-4] + str('nhdr')
    else:
        # Write header & data as one file
        datafilename = filename;
        separate_header = False;

    with open(filename,'wb') as filehandle:
        filehandle.write(b'NRRD0005\n')
        filehandle.write(b'# This NRRD file was generated by pynrrd\n')
        filehandle.write(b'# on ' +
                         datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S').encode('ascii') +
                         b'(GMT).\n')
        filehandle.write(b'# Complete NRRD file format specification at:\n');
        filehandle.write(b'# http://teem.sourceforge.net/nrrd/format.html\n');

        # Write the fields in order, this ignores fields not in _NRRD_FIELD_ORDER
        for field in _NRRD_FIELD_ORDER:
            if field in options:
                outline = (field + ': ' +
                           _NRRD_FIELD_FORMATTERS[field](options[field]) +
                           '\n').encode('ascii')
                filehandle.write(outline)
        d = options.get('keyvaluepairs', {})
        for (k,v) in sorted(d.items(), key=lambda t: t[0]):
            outline = (str(k) + ':=' + str(v) + '\n').encode('ascii')
            filehandle.write(outline)

        # Write the closing extra newline
        filehandle.write(b'\n')

        # If a single file desired, write data
        if not separate_header:
            _write_data(data, filehandle, options)

    # If separate header desired, write data to different file
    if separate_header:
        with open(datafilename, 'wb') as datafilehandle:
            _write_data(data, datafilehandle, options)
    
    return filename;


def dataSize(filename, **args):
    """Read data size from nrrd image
    
    Arguments:
        filename (str): file name as regular expression
        x,y,z (tuple): data range specifications
    
    Returns:
        tuple: data size
    """    
    
    header = readHeader(filename);
    dims = header['sizes'];
    #dims[0:2] = [dims[1], dims[0]];
    return io.dataSizeFromDataRange(dims, **args);

    
def dataZSize(filename, z = all, **args):
    """Read data z size from nrrd image
        
    Arguments:
        filename (str): file name as regular expression
        z (tuple): z data range specification
    
    Returns:
        int: z data size
    """
    
    header = readHeader(filename);
    dims = header['sizes'];
    
    if len(dims) > 2:
        return io.toDataSize(dims[2], r = z);
    else:
        return None;
        

    
def copyData(source, sink):
    """Copy an nrrd file from source to sink
    
    Arguments:
        source (str): file name pattern of source
        sink (str): file name pattern of sink
    
    Returns:
        str: file name of the copy
        
    Notes:
        Todo: dealt with nrdh header files!
    """ 
    io.copyFile(source, sink);

 

def test():
    """Test NRRD IO module"""
    import ClearMap.IO.NRRD as self 
    reload(self)
    
    from ClearMap.Settings import ClearMapPath
    import os
    import numpy
    
    """Test NRRD module"""
    basedir = ClearMapPath;
    fn = os.path.join(basedir, 'Test/Data/Nrrd/test.nrrd')

    data = numpy.random.rand(20,50,10);
    data[5:15, 20:45, 2:9] = 0;

    reload(self)
    print "writing nrrd image to: " + fn;    
    self.writeData(fn, data);
    
    ds = self.dataSize(fn);
    print "dataSize: %s" % str(ds);

    print "Loading raw image from: " + fn;
    img = self.readData(fn);  
    print "Image size: " + str(img.shape)
    
    diff = img - data;
    print (diff.max(), diff.min())

    #some uint type
    print "writing raw image to: " + fn;    
    udata = data * 10;
    udata = udata.astype('uint16');
    self.writeData(fn, udata);

    print "Loading raw image from: " + fn;
    img = self.readData(fn);  
    print "Image size: " + str(img.shape)
    
    diff = img - udata;
    print (diff.max(), diff.min())
    
    #dataSize
    print "dataSize  is %s" % str(self.dataSize(fn))
    print "dataZSize is %s" % str(self.dataZSize(fn))

if __name__ == "__main__":
    test();
