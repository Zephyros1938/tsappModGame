import datetime
import decimal
import uuid
import struct

# --- Helper Functions ---


def _wrap_int(value, bits, signed=True):
    """
    Simulate C# unchecked arithmetic by wrapping the value to the given fixed width.
    """
    if signed:
        min_val = -(2 ** (bits - 1))
        range_size = 2**bits
        # Wrap the value into the range [min_val, min_val + range_size)
        value = ((value - min_val) % range_size) + min_val
    else:
        range_size = 2**bits
        value = value % range_size
    return value


def _check_int_range(value, bits, signed=True):
    """
    Ensure the value is within the valid range for the given number of bits.
    If not, raise an OverflowError.
    """
    value = int(value)
    if signed:
        if not (-(2 ** (bits - 1)) <= value < 2 ** (bits - 1)):
            raise OverflowError(
                f"Value {value} out of range for {bits}-bit signed integer"
            )
    else:
        if not (0 <= value < 2**bits):
            raise OverflowError(
                f"Value {value} out of range for {bits}-bit unsigned integer"
            )
    return value


class AutoCastDescriptor:
    def __init__(self, typ, default):
        self.typ = typ
        self.default = default
        self.private_name = None

    def __set_name__(self, owner, name):
        self.private_name = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        # If the private attribute hasn't been set yet, use the default.
        if not hasattr(instance, self.private_name):
            # Convert the default value using the type’s constructor.
            setattr(instance, self.private_name, self.typ(self.default))
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        setattr(instance, self.private_name, self.typ(value))


class AutoCastMeta(type):
    def __new__(mcls, name, bases, namespace):
        annotations = namespace.get("__annotations__", {})
        for attr, typ in annotations.items():
            # Get the default value if provided; otherwise, use None.
            default = namespace.get(attr, None)
            namespace[attr] = AutoCastDescriptor(typ, default)
        return super().__new__(mcls, name, bases, namespace)


# --- Numeric Types: Integer Base with Arithmetic Wrapping ---


class CSharpInt(int):
    """
    Base class for C# integer types. It enforces range on creation and
    simulates unchecked arithmetic (wrapping on overflow).
    """

    _bits = 32  # Default; override in subclasses.
    _signed = True  # Default; override in subclasses.

    def __new__(cls, value):
        value = int(value)
        # Ensure initial value is within range.
        value = _check_int_range(value, cls._bits, cls._signed)
        return super().__new__(cls, value)

    def __add__(self, other):
        result = int(self) + int(other)
        result = _wrap_int(result, self._bits, self._signed)
        return self.__class__(result)

    def __sub__(self, other):
        result = int(self) - int(other)
        result = _wrap_int(result, self._bits, self._signed)
        return self.__class__(result)

    def __mul__(self, other):
        result = int(self) * int(other)
        result = _wrap_int(result, self._bits, self._signed)
        return self.__class__(result)

    def __neg__(self):
        result = -int(self)
        result = _wrap_int(result, self._bits, self._signed)
        return self.__class__(result)

    MAX_VALUE = 2147483647
    MIN_VALUE = -2147483648


# --- Specific Integer Types (with appropriate bit sizes) ---


class SByte(CSharpInt):
    _bits = 8
    _signed = True
    MAX_VALUE = 127
    MIN_VALUE = -128


class Byte(CSharpInt):
    _bits = 8
    _signed = False
    MAX_VALUE = 0xFF
    MIN_VALUE = 0


class Int16(CSharpInt):
    _bits = 16
    _signed = True
    MAX_VALUE = 32767
    MIN_VALUE = -32767


class UInt16(CSharpInt):
    _bits = 16
    _signed = False
    _bits = 8
    _signed = False
    MAX_VALUE = 0xFFFF
    MIN_VALUE = 0


class Int32(CSharpInt):
    _bits = 32
    _signed = True
    MAX_VALUE = 2147483647
    MIN_VALUE = -2147483648


class UInt32(CSharpInt):
    _bits = 32
    _signed = False
    MAX_VALUE = 0xFFFFFFFF
    MIN_VALUE = 0


class Int64(CSharpInt):
    _bits = 64
    _signed = True
    MAX_VALUE = 9223372036854775807
    MIN_VALUE = -9223372036854775808


class UInt64(CSharpInt):
    _bits = 64
    _signed = False
    MAX_VALUE = 0xFFFFFFFFFFFFFFFF
    MIN_VALUE = 0


# --- Floating Point Types ---


class CSharpFloat(float):
    """
    Base class for C# floating point types.
    For Single, we force a 32-bit precision conversion.
    """

    _precision = "64"  # Use '32' for Single; '64' for Double

    def __new__(cls, value):
        value = float(value)
        if cls._precision == "32":
            # Simulate conversion to a 32-bit float.
            packed = struct.pack("f", value)
            value = struct.unpack("f", packed)[0]
        return super().__new__(cls, value)

    def __add__(self, other):
        result = float(self) + float(other)
        return self.__class__(result)

    def __sub__(self, other):
        result = float(self) - float(other)
        return self.__class__(result)

    def __mul__(self, other):
        result = float(self) * float(other)
        return self.__class__(result)

    def __truediv__(self, other):
        result = float(self) / float(other)
        return self.__class__(result)


class Single(CSharpFloat):
    _precision = "32"


class Double(CSharpFloat):
    _precision = "64"


# --- Decimal Type ---


class Decimal(decimal.Decimal):
    """
    Mimics C#'s Decimal type.
    """

    def __new__(cls, value="0", *args, **kwargs):
        return super().__new__(cls, value, *args, **kwargs)


# --- Reference Types ---


class Object(object):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)


class String(str):
    def __new__(cls, value=""):
        return super().__new__(cls, value)


class Char(String):
    def __new__(cls, value):
        if not isinstance(value, str) or len(value) != 1:
            raise ValueError("Char must be a single character string")
        return super().__new__(cls, value)


class Boolean(bool.__base__):
    def __new__(cls, value):
        return super().__new__(cls, bool(value))


# --- Date and Time Types ---


class DateTime(datetime.datetime):
    """
    Mimics C#'s DateTime.
    Supports addition/subtraction with TimeSpan.
    """

    def __new__(
        cls, year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None
    ):
        return super().__new__(
            cls, year, month, day, hour, minute, second, microsecond, tzinfo
        )

    def __add__(self, other):
        if isinstance(other, TimeSpan):
            result = super().__add__(other)
            # Convert the result back into a DateTime instance.
            return DateTime(
                result.year,
                result.month,
                result.day,
                result.hour,
                result.minute,
                result.second,
                result.microsecond,
                result.tzinfo,
            )
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, TimeSpan):
            result = super().__sub__(other)
            return DateTime(
                result.year,
                result.month,
                result.day,
                result.hour,
                result.minute,
                result.second,
                result.microsecond,
                result.tzinfo,
            )
        elif isinstance(other, DateTime):
            result = super().__sub__(other)
            # The difference between two DateTime objects is a TimeSpan.
            return TimeSpan(
                days=result.days,
                seconds=result.seconds,
                microseconds=result.microseconds,
            )
        return NotImplemented


class TimeSpan(datetime.timedelta):
    """
    Mimics C#'s TimeSpan.
    Accepts parameters similar to C# (days, hours, minutes, seconds, milliseconds, etc.)
    """

    def __new__(
        cls,
        days=0,
        seconds=0,
        microseconds=0,
        milliseconds=0,
        minutes=0,
        hours=0,
        weeks=0,
    ):
        total_microseconds = microseconds + (milliseconds * 1000)
        total_seconds = seconds + minutes * 60 + hours * 3600 + weeks * 7 * 24 * 3600
        return super().__new__(cls, days, total_seconds, total_microseconds)


# --- Guid Type ---


class Guid(uuid.UUID):
    """
    Mimics C#'s Guid.
    If no hex string is provided, a new GUID is generated.
    """

    def __new__(cls, hex=None, *args, **kwargs):
        if hex is None:
            return uuid.uuid4()
        return super().__new__(cls, hex, *args, **kwargs)


# --- Collection Types ---


class Array(list):
    def __new__(cls, iterable=None):
        if iterable is None:
            iterable = []
        return super().__new__(cls, iterable)


class Map(dict):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)


# --- Example Usage ---

if __name__ == "__main__":
    # Integer arithmetic with wrapping (e.g., Int32)
    a = Int32(2147483640)
    b = Int32(10)
    c = a + b  # Expected to wrap around if unchecked
    print("Int32 wrapping:", c, int(c))

    # Single precision float arithmetic
    s1 = Single(3.141592653589793)
    s2 = Single(2.0)
    s3 = s1 * s2
    print("Single arithmetic:", s3, float(s3))

    # DateTime arithmetic
    dt = DateTime(2025, 3, 4, 12, 0, 0)
    ts = TimeSpan(hours=1, minutes=30)
    new_dt = dt + ts
    print("DateTime + TimeSpan:", new_dt)

    # Guid generation
    guid1 = Guid()
    guid2 = Guid("12345678123456781234567812345678")
    print("Generated Guid:", guid1)
    print("Specified Guid:", guid2)
