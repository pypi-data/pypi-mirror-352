import io
import typing
from typing import *
from typing import BinaryIO
from .scpi_type_base import ScpiTypeBase


class ScpiChars(ScpiTypeBase):
    """
    Class representing IEEE488.2 Character program data (7.7.1) and response data (8.7.1)

        This functional element is used to convey parameter information best expressed mnemonically
        as a short alpha or alphanumeric string. It is useful in cases where numeric parameters are inappropriate.
    """

    def __init__(self, s: str) -> None:
        """Initializes the object from a str type"""
        super().__init__()
        self._data = s

    def __str__(self) -> str:
        return self.as_string()

    def as_string(self) -> str:
        """Returns the char data as a Python str-object"""
        return self._data

    def as_bytes(self) -> bytes:
        """Returns the char data as a Python bytes-object"""
        return self._data.encode(self._encoding)

    def compose(self) -> bytes:
        """Composes the object into a SCPI string to be used as a parameter"""
        return self._data.encode(self._encoding)

    @classmethod
    def parse(cls, transport: BinaryIO) -> 'ScpiChars':
        """Parses stream data from the device and creates a `ScpiChars` object"""
        s = transport.readline().rstrip(cls._newline).decode(cls._encoding)
        return ScpiChars(s)


class ScpiNumber(ScpiTypeBase):
    """
    Class representing IEEE488.2 flexible Decimal/Nondecimal numeric NRf program data (7.7.2/7.7.4) and
    NR1/NR2/NR3 response data (8.7.2/8.7.3/8.7.4)
    """

    strfuncs = {10: str, 16: hex, 8: oct, 2: bin}
    prefixes = {10: '', 16: '#H', 8: '#Q', 2: '#B'}
    formats = {10: 'd', 16: 'X', 8: 'o', 2: 'b'}

    def __init__(self, value: Union[int, float], unit: Optional[str] = None, base: int = 10):
        """Initializes the object from either an int (NR1) or float (NR2/NR3) value with an optional unit string"""
        super().__init__()
        self._value = value
        self._unit = unit

        if base not in self.strfuncs:
            raise ValueError(f'Base {base} is not in {list(self.strfuncs.keys())}.')

        self._base = base
        self._strfunc = self.strfuncs[base]
        self._prefix = self.prefixes[base]
        self._format = self.formats[base]

    def __int__(self) -> int:
        return self.as_int()

    def __float__(self) -> float:
        return self.as_float()

    def __str__(self) -> str:
        value = self._strfunc(self._value)
        unit = f' {self._unit}' if self._unit is not None else ''
        return f'{str(value)}{unit}'

    def as_int(self) -> int:
        """Returns the numeric data as a Python int-object """
        return int(self._value)

    def as_float(self) -> float:
        """Returns the numeric data as a Python float-object"""
        return float(self._value)

    @property
    def unit(self) -> str:
        """Returns the unit as a Python str-object"""
        return self._unit

    @property
    def base(self) -> int:
        """Returns the base of the number as integer"""
        return self._base

    def compose(self) -> bytes:
        """Composes the object into a SCPI string to be used as a parameter"""
        if type(self._value) == int:
            # Compose into NR1 representation
            return f'{self._prefix}{self._value:{self._format}}{(" " + self._unit) if self._unit is not None else ""}'.encode(self._encoding)
        elif type(self._value) == float:
            # Compose into NR2/3 representation
            return f'{self._value:.15g}{(" " + self._unit) if self._unit is not None else ""}'.encode(self._encoding)
        else:
            raise TypeError

    @classmethod
    def parse(cls, transport: BinaryIO):
        """Parses stream data from the device and creates a `ScpiNumber` object"""
        data = transport.readline().rstrip(cls._newline).decode(cls._encoding)
        substrs = data.split(' ')
        base = 10
        prefix = substrs[0][:2] if substrs[0].startswith('#') else None
        numstr = substrs[0] if prefix is None else substrs[0][2:]

        # Parse prefix
        if prefix is not None:
            if prefix not in cls.prefixes.values():
                raise TypeError(f'Prefix {prefix} is not in {list(cls.prefixes.values())}.')

            base = [k for k, v in cls.prefixes.items() if v == prefix][0]

        try:
            # Try parsing as NR1 representation first
            value = int(numstr, base)
        except ValueError:
            try:
                # Otherwise NR2 or NR3 representation
                value = float(substrs[0])
            except ValueError:
                raise TypeError(f'Invalid Number format: {data}')

        # Unit available?
        if len(substrs) > 1:
            unit = substrs[1]
        else:
            unit = None

        return ScpiNumber(value, unit, base)


class ScpiNumberArray(ScpiTypeBase):
    """
    Class representing an array of IEEE488.2 flexible Decimal/Nondecimal numeric NRf program data (7.7.2/7.7.4) and
    NR1/NR2/NR3 response data (8.7.2/8.7.3/8.7.4)
    """

    def __init__(self, numbers: Iterable[Union[ScpiNumber, int, float]], **kwargs) -> None:
        """Initializes the object from a list of either an int (NR1) or float (NR2/NR3) values"""
        super().__init__()

        # Convert to ScpiNumber if not already
        self._numbers = [n if isinstance(n, ScpiNumber) else ScpiNumber(n, **kwargs) for n in numbers]

    def __str__(self) -> str:
        return '[' + ', '.join([str(number) for number in self._numbers]) + ']'

    def as_int_list(self) -> List[int]:
        """Returns the numeric data as a Python list of ints"""
        return [x.as_int() for x in self._numbers]

    def as_float_list(self) -> List[float]:
        """Returns the numeric data as a Python list of floats"""
        return [x.as_float() for x in self._numbers]

    def compose(self) -> bytes:
        """Composes the object into a SCPI string to be used as a parameter"""
        return b','.join([x.compose() for x in self._numbers])

    @classmethod
    def parse(cls, transport: BinaryIO):
        """Parses stream data from the device and creates a `ScpiNumberArray` object"""
        data = transport.readline().rstrip(cls._newline)
        substrs = data.split(b',')
        numbers = [ScpiNumber.parse(io.BytesIO(substr)) for substr in substrs]
        return ScpiNumberArray(numbers)


class ScpiString(ScpiTypeBase):
    """"
    Class representing IEEE488.2 String program data (7.7.5) and response data (8.7.8)

        This element allows any character in the ASCII 7-bit code to be transmitted as a message.
        This data field is particularly useful where text is to be displayed.
    """

    def __init__(self, data: str) -> None:
        """Initializes the object from a str type"""
        super().__init__()
        self._data = data

    def __str__(self) -> str:
        # Shorten string for str() display
        s = self._data.replace('\r', '').replace('\n', ' ')
        s = s[:40] + (s[40:] and '...')
        return s

    def __bytes__(self) -> bytes:
        return self.as_bytes()

    def as_string(self) -> str:
        """Returns the char data as a Python str-object"""
        return self._data

    def as_bytes(self) -> bytes:
        """Returns the char data as a Python bytes-object"""
        return self._data.encode(self._encoding)

    def compose(self) -> bytes:
        """Composes the object into a SCPI string to be used as a parameter"""
        return f'"{self._data}"'.encode(self._encoding)

    @classmethod
    def parse(cls, transport: BinaryIO):
        """Parses stream data from the device and creates a `ScpiString` object"""
        quotes = 0
        string = b""
        while 1:
            chunk = transport.readline().rstrip(cls._newline)
            quotes += chunk.count(b'"')
            string += chunk + b'\r\n'

            if (quotes % 2 == 0) and (string != b''):
                break

        string = string.strip(b'\r\n\t"')
        string = string.replace(b'""', b'"')

        return ScpiString(string.decode(cls._encoding))


class ScpiArbBlock(ScpiTypeBase, typing.BinaryIO):
    """
    Class representing IEEE488.2 Arbitrary block program data (7.7.6) and
    definite length arbitrary block response (8.7.9)

        This element allows any 8 bit bytes to be transmitted in a message.
        This element is particularly helpful for sending large quantities of data.
    """
    def __init__(self, data: Union[bytes, memoryview]):
        super().__init__()
        self._data = data
        self._length = len(data)
        self._offset = 0
        self._remaining = self._length

    def __str__(self) -> str:
        return f'<block with {len(self._data)} bytes of binary data>'

    def __bytes__(self) -> bytes:
        return self.as_bytes()

    def __getitem__(self, item):
        if type(item) == slice:
            return ScpiArbBlock(self._data.__getitem__(item))
        else:
            raise KeyError()

    def close(self) -> None:
        pass

    def closed(self) -> bool:
        return False

    def readable(self) -> bool:
        return True

    def readline(self, __size: Optional[int] = -1) -> bytes:
        raise NotImplementedError()

    def readlines(self, __hint: int = -1) -> List[bytes]:
        raise NotImplementedError()

    def seekable(self) -> bool:
        return True

    def seek(self, __offset: int, __whence: int = io.SEEK_SET) -> int:
        if __whence == io.SEEK_SET:
            self._offset = __offset
            self._remaining = self._length - __offset
        elif __whence == io.SEEK_CUR:
            self._offset += __offset
            self._remaining -= __offset
        else:
            self._offset = self._length + __offset
            self._remaining = __offset

    def writable(self) -> bool:
        return False

    def writelines(self, lines: Iterable):
        raise NotImplementedError()

    def read(self, __size: int = -1) -> Union[bytes, memoryview]:
        if __size < 0:
            v = self._data[self._offset:]
        else:
            v = self._data[self._offset:self._offset + __size]

        self._remaining -= len(v)
        self._offset += len(v)
        return v

    def readall(self) -> Union[bytes, memoryview]:
        return self.read(self._remaining)

    def as_bytes(self) -> bytes:
        return bytes(self._data[self._offset:])

    def as_memoryview(self) -> memoryview:
        return memoryview(self._data[self._offset:])

    def compose(self) -> bytes:
        length = f'{len(self._data)}'
        head = f'{len(length)}'
        return ('#' + head + length).encode(self._encoding) + self._data

    @classmethod
    def parse(cls, transport: BinaryIO):
        """Parses stream data from the device and creates a `ScpiArbBlock` object"""
        head = transport.read(2)

        if head[0:1] != b'#':
            raise ValueError("Could not find hash sign (#) indicating the start of the block.")

        # read header size
        num = int(head[1:2])

        if num == 0:
            raise NotImplementedError("Indefinite length arbitrary block response not implemented")

        # read header
        length = int(transport.read(num))
        data = transport.read(length)

        # Swallow \r\n
        transport.readline()

        return ScpiArbBlock(memoryview(data))


class ScpiArbStream(ScpiTypeBase, typing.BinaryIO):
    """
    Class representing IEEE488.2 Arbitrary block program data (7.7.6) and
    in/definite length arbitrary block response (8.7.9/8.7.10)

        This element allows any 8 bit bytes to be transmitted in a message.
        This element is particularly helpful for sending large quantities of data.

    Note that this class is derived from io.RawIOBase and can be used for stream processing
    """

    def __init__(self, stream: BinaryIO, length: int, indefinite: bool = False) -> None:
        """Initialize object from a `ScpiTransportBase` object and length integer"""
        super().__init__()
        self._stream = stream
        self._length = length
        self._remaining = length
        self._indefinite = indefinite
        self._strip = True if not indefinite else False

    def __str__(self) -> str:
        return f'<stream with {self._length} bytes of binary data>'

    def fileno(self) -> int:
        return self._stream.fileno()

    def close(self) -> None:
        pass

    def closed(self) -> bool:
        return False

    def isatty(self) -> bool:
        return self._stream.isatty()

    def readable(self) -> bool:
        return self._stream.readable()

    def readline(self, __size: Optional[int] = -1) -> bytes:
        raise NotImplementedError()

    def readlines(self, __hint: int = -1) -> List[bytes]:
        raise NotImplementedError()

    def seekable(self) -> bool:
        return self._stream.seekable()

    def writable(self) -> bool:
        return False

    def writelines(self, lines: Iterable):
        raise NotImplementedError()

    def read(self, __size: int = -1) -> Optional[bytes]:
        if self._indefinite and __size == -1:
            raise ValueError('__size parameter must be present for indefinite arbitrary block')

        data = self._stream.read(__size)
        if not self._indefinite: self._remaining -= len(data)

        if self._strip and (self._remaining == 0):
            # eat newline
            self._stream.readline()

        return data

    def readall(self) -> bytes:
        return self.read(self._remaining)

    def compose(self) -> bytes:
        # Write all data in one go
        length = f'{self._length}'
        head = f'{len(length)}'
        data = self._stream.read(self._length)
        return ('#' + head + length).encode(self._encoding) + data

    @classmethod
    def parse(cls, transport: BinaryIO):
        """Parses stream data from the device and creates a `ScpiArbStream` object"""
        head = transport.read(2)

        if head[0:1] != b'#':
            raise ValueError("Could not find hash sign (#) indicating the start of the block.")

        # read header size
        num = int(head[1:2])

        if num == 0:
            # indefinite size arbitrary
            return ScpiArbStream(transport, 0, indefinite=True)

        # read header for definite size arbitrary block
        length = int(transport.read(num))
        return ScpiArbStream(transport, length)


class ScpiBool(ScpiTypeBase):
    """
    Class representing SCPI-99 boolean (Vol. 1, 7.3)
    """

    def __init__(self, onoff: bool) -> None:
        """Initializes the object from a Python bool type"""
        super().__init__()
        self._onoff = onoff

    def __str__(self) -> str:
        return str(self._onoff)

    def __bool__(self) -> bool:
        return self.as_bool()

    def as_bool(self) -> bool:
        """Returns the boolean value as a Python bool type"""
        if self._onoff:
            return True
        else:
            return False

    def compose(self) -> bytes:
        """Composes the object into a SCPI string to be used as a parameter"""
        if self._onoff:
            return "ON".encode(self._encoding)
        else:
            return "OFF".encode(self._encoding)

    @classmethod
    def parse(cls, transport: BinaryIO):
        """Parses stream data from the device and creates a `ScpiBool` object"""
        data = transport.readline().rstrip(cls._newline)
        if int(data) == 0:
            return ScpiBool(False)
        else:
            return ScpiBool(True)


class ScpiNumList(ScpiTypeBase):
    """
    Class representing a SCPI-99 numeric list (Vol. 1, 8.8.3) using the
    IEEE488.2 Expression program data (7.7.7) and Expression response data (8.7.12) format.

        A numeric list is an expression format for compactly expressing
        numbers and ranges of numbers in a single parameter.
    """

    def __init__(self, numlist: List[int]) -> None:
        self._numlist = numlist

    def __str__(self) -> str:
        return str(self._numlist)

    def as_list(self) -> List[int]:
        """Returns the object as a Python list-object"""
        return self._numlist

    def compose(self) -> bytes:
        """Composes the numeric list into a SCPI string to be used as a parameter"""
        return ('(' + ','.join(map(str, self._numlist)) + ')').encode(self._encoding)

    @classmethod
    def parse(cls, transport: BinaryIO):
        """Parses stream data from the device and creates a `ScpiNumList` object"""
        data = transport.readline().rstrip(cls._newline)
        substrs = data.strip(b'()').split(b',')
        return ScpiNumList([int(e) for e in substrs])


class ScpiEvent(ScpiTypeBase):
    """
    Class representing a SCPI-99 error/event queue item (Vol. 2, 21.8)
    """

    def __init__(self, code: int, description: str, info: Optional[str] = None) -> None:
        self._code = code
        self._description = description
        self._info = info

    def __str__(self) -> str:
        return self.as_string()

    def as_string(self) -> str:
        """Return the event as Python str-object"""
        return f'{self._code:d}: {self._description}' + (f' ({self._info})' if self._info is not None else '')

    @property
    def code(self):
        return self._code

    @property
    def description(self):
        return self._description

    @property
    def info(self):
        return self._info

    def compose(self) -> str:
        raise NotImplementedError

    @classmethod
    def parse(cls, transport: BinaryIO):
        data = transport.readline().rstrip(cls._newline).decode(cls._encoding)
        substrs = data.split(',')
        event = substrs[1].strip('"').split(';')
        code = int(substrs[0])
        description = event[0]
        info = event[1] if len(event) > 1 else None
        return ScpiEvent(code, description, info)
