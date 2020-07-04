import asyncio
import socket
import struct
import sys
import functools
from .ctes import *

exceptions = True

# pigpio command numbers
_PI_CMD_MODES = 0
_PI_CMD_MODEG = 1
_PI_CMD_PUD = 2
_PI_CMD_READ = 3
_PI_CMD_WRITE = 4
_PI_CMD_PWM = 5
_PI_CMD_PRS = 6
_PI_CMD_PFS = 7
_PI_CMD_SERVO = 8
_PI_CMD_WDOG = 9
_PI_CMD_BR1 = 10
_PI_CMD_BR2 = 11
_PI_CMD_BC1 = 12
_PI_CMD_BC2 = 13
_PI_CMD_BS1 = 14
_PI_CMD_BS2 = 15
_PI_CMD_TICK = 16
_PI_CMD_HWVER = 17

_PI_CMD_NO = 18
_PI_CMD_NB = 19
_PI_CMD_NP = 20
_PI_CMD_NC = 21

_PI_CMD_PRG = 22
_PI_CMD_PFG = 23
_PI_CMD_PRRG = 24
_PI_CMD_HELP = 25
_PI_CMD_PIGPV = 26

_PI_CMD_WVCLR = 27
_PI_CMD_WVAG = 28
_PI_CMD_WVAS = 29
_PI_CMD_WVGO = 30
_PI_CMD_WVGOR = 31
_PI_CMD_WVBSY = 32
_PI_CMD_WVHLT = 33
_PI_CMD_WVSM = 34
_PI_CMD_WVSP = 35
_PI_CMD_WVSC = 36

_PI_CMD_TRIG = 37

_PI_CMD_PROC = 38
_PI_CMD_PROCD = 39
_PI_CMD_PROCR = 40
_PI_CMD_PROCS = 41

_PI_CMD_SLRO = 42
_PI_CMD_SLR = 43
_PI_CMD_SLRC = 44

_PI_CMD_PROCP = 45
_PI_CMD_MICRO = 46
_PI_CMD_MILLI = 47
_PI_CMD_PARSE = 48

_PI_CMD_WVCRE = 49
_PI_CMD_WVDEL = 50
_PI_CMD_WVTX = 51
_PI_CMD_WVTXR = 52
_PI_CMD_WVNEW = 53

_PI_CMD_I2CO = 54
_PI_CMD_I2CC = 55
_PI_CMD_I2CRD = 56
_PI_CMD_I2CWD = 57
_PI_CMD_I2CWQ = 58
_PI_CMD_I2CRS = 59
_PI_CMD_I2CWS = 60
_PI_CMD_I2CRB = 61
_PI_CMD_I2CWB = 62
_PI_CMD_I2CRW = 63
_PI_CMD_I2CWW = 64
_PI_CMD_I2CRK = 65
_PI_CMD_I2CWK = 66
_PI_CMD_I2CRI = 67
_PI_CMD_I2CWI = 68
_PI_CMD_I2CPC = 69
_PI_CMD_I2CPK = 70

_PI_CMD_SPIO = 71
_PI_CMD_SPIC = 72
_PI_CMD_SPIR = 73
_PI_CMD_SPIW = 74
_PI_CMD_SPIX = 75

_PI_CMD_SERO = 76
_PI_CMD_SERC = 77
_PI_CMD_SERRB = 78
_PI_CMD_SERWB = 79
_PI_CMD_SERR = 80
_PI_CMD_SERW = 81
_PI_CMD_SERDA = 82

_PI_CMD_GDC = 83
_PI_CMD_GPW = 84

_PI_CMD_HC = 85
_PI_CMD_HP = 86

_PI_CMD_CF1 = 87
_PI_CMD_CF2 = 88

_PI_CMD_FG = 97
_PI_CMD_FN = 98

_PI_CMD_NOIB = 99

_PI_CMD_BI2CC = 89
_PI_CMD_BI2CO = 90
_PI_CMD_BI2CZ = 91

_PI_CMD_I2CZ = 92

_PI_CMD_WVCHA = 93

_PI_CMD_SLRI = 94

_PI_CMD_BSPIC = 111
_PI_CMD_BSPIO = 112
_PI_CMD_BSPIX = 113

# pigpio error text

_errors = [
   [PI_INIT_FAILED, "pigpio initialisation failed"],
   [PI_BAD_USER_GPIO, "gpio not 0-31"],
   [PI_BAD_GPIO, "gpio not 0-53"],
   [PI_BAD_MODE, "mode not 0-7"],
   [PI_BAD_LEVEL, "level not 0-1"],
   [PI_BAD_PUD, "pud not 0-2"],
   [PI_BAD_PULSEWIDTH, "pulsewidth not 0 or 500-2500"],
   [PI_BAD_DUTYCYCLE, "dutycycle not 0-range (default 255)"],
   [PI_BAD_TIMER, "timer not 0-9"],
   [PI_BAD_MS, "ms not 10-60000"],
   [PI_BAD_TIMETYPE, "timetype not 0-1"],
   [PI_BAD_SECONDS, "seconds < 0"],
   [PI_BAD_MICROS, "micros not 0-999999"],
   [PI_TIMER_FAILED, "gpioSetTimerFunc failed"],
   [PI_BAD_WDOG_TIMEOUT, "timeout not 0-60000"],
   [PI_NO_ALERT_FUNC, "DEPRECATED"],
   [PI_BAD_CLK_PERIPH, "clock peripheral not 0-1"],
   [PI_BAD_CLK_SOURCE, "DEPRECATED"],
   [PI_BAD_CLK_MICROS, "clock micros not 1, 2, 4, 5, 8, or 10"],
   [PI_BAD_BUF_MILLIS, "buf millis not 100-10000"],
   [PI_BAD_DUTYRANGE, "dutycycle range not 25-40000"],
   [PI_BAD_SIGNUM, "signum not 0-63"],
   [PI_BAD_PATHNAME, "can't open pathname"],
   [PI_NO_HANDLE, "no handle available"],
   [PI_BAD_HANDLE, "unknown handle"],
   [PI_BAD_IF_FLAGS, "ifFlags > 3"],
   [PI_BAD_CHANNEL, "DMA channel not 0-14"],
   [PI_BAD_SOCKET_PORT, "socket port not 1024-30000"],
   [PI_BAD_FIFO_COMMAND, "unknown fifo command"],
   [PI_BAD_SECO_CHANNEL, "DMA secondary channel not 0-6"],
   [PI_NOT_INITIALISED, "function called before gpioInitialise"],
   [PI_INITIALISED, "function called after gpioInitialise"],
   [PI_BAD_WAVE_MODE, "waveform mode not 0-1"],
   [PI_BAD_CFG_INTERNAL, "bad parameter in gpioCfgInternals call"],
   [PI_BAD_WAVE_BAUD, "baud rate not 50-250000(RX)/1000000(TX)"],
   [PI_TOO_MANY_PULSES, "waveform has too many pulses"],
   [PI_TOO_MANY_CHARS, "waveform has too many chars"],
   [PI_NOT_SERIAL_GPIO, "no bit bang serial read in progress on gpio"],
   [PI_NOT_PERMITTED, "no permission to update gpio"],
   [PI_SOME_PERMITTED, "no permission to update one or more gpios"],
   [PI_BAD_WVSC_COMMND, "bad WVSC subcommand"],
   [PI_BAD_WVSM_COMMND, "bad WVSM subcommand"],
   [PI_BAD_WVSP_COMMND, "bad WVSP subcommand"],
   [PI_BAD_PULSELEN, "trigger pulse length not 1-100"],
   [PI_BAD_SCRIPT, "invalid script"],
   [PI_BAD_SCRIPT_ID, "unknown script id"],
   [PI_BAD_SER_OFFSET, "add serial data offset > 30 minute"],
   [PI_GPIO_IN_USE, "gpio already in use"],
   [PI_BAD_SERIAL_COUNT, "must read at least a byte at a time"],
   [PI_BAD_PARAM_NUM, "script parameter id not 0-9"],
   [PI_DUP_TAG, "script has duplicate tag"],
   [PI_TOO_MANY_TAGS, "script has too many tags"],
   [PI_BAD_SCRIPT_CMD, "illegal script command"],
   [PI_BAD_VAR_NUM, "script variable id not 0-149"],
   [PI_NO_SCRIPT_ROOM, "no more room for scripts"],
   [PI_NO_MEMORY, "can't allocate temporary memory"],
   [PI_SOCK_READ_FAILED, "socket read failed"],
   [PI_SOCK_WRIT_FAILED, "socket write failed"],
   [PI_TOO_MANY_PARAM, "too many script parameters (> 10)"],
   [PI_NOT_HALTED, "script already running or failed"],
   [PI_BAD_TAG, "script has unresolved tag"],
   [PI_BAD_MICS_DELAY, "bad MICS delay (too large)"],
   [PI_BAD_MILS_DELAY, "bad MILS delay (too large)"],
   [PI_BAD_WAVE_ID, "non existent wave id"],
   [PI_TOO_MANY_CBS, "No more CBs for waveform"],
   [PI_TOO_MANY_OOL, "No more OOL for waveform"],
   [PI_EMPTY_WAVEFORM, "attempt to create an empty waveform"],
   [PI_NO_WAVEFORM_ID, "No more waveform ids"],
   [PI_I2C_OPEN_FAILED, "can't open I2C device"],
   [PI_SER_OPEN_FAILED, "can't open serial device"],
   [PI_SPI_OPEN_FAILED, "can't open SPI device"],
   [PI_BAD_I2C_BUS, "bad I2C bus"],
   [PI_BAD_I2C_ADDR, "bad I2C address"],
   [PI_BAD_SPI_CHANNEL, "bad SPI channel"],
   [PI_BAD_FLAGS, "bad i2c/spi/ser open flags"],
   [PI_BAD_SPI_SPEED, "bad SPI speed"],
   [PI_BAD_SER_DEVICE, "bad serial device name"],
   [PI_BAD_SER_SPEED, "bad serial baud rate"],
   [PI_BAD_PARAM, "bad i2c/spi/ser parameter"],
   [PI_I2C_WRITE_FAILED, "I2C write failed"],
   [PI_I2C_READ_FAILED, "I2C read failed"],
   [PI_BAD_SPI_COUNT, "bad SPI count"],
   [PI_SER_WRITE_FAILED, "ser write failed"],
   [PI_SER_READ_FAILED, "ser read failed"],
   [PI_SER_READ_NO_DATA, "ser read no data available"],
   [PI_UNKNOWN_COMMAND, "unknown command"],
   [PI_SPI_XFER_FAILED, "SPI xfer/read/write failed"],
   [PI_BAD_POINTER, "bad (NULL) pointer"],
   [PI_NO_AUX_SPI, "need a A+/B+/Pi2 for auxiliary SPI"],
   [PI_NOT_PWM_GPIO, "gpio is not in use for PWM"],
   [PI_NOT_SERVO_GPIO, "gpio is not in use for servo pulses"],
   [PI_NOT_HCLK_GPIO, "gpio has no hardware clock"],
   [PI_NOT_HPWM_GPIO, "gpio has no hardware PWM"],
   [PI_BAD_HPWM_FREQ, "hardware PWM frequency not 1-125M"],
   [PI_BAD_HPWM_DUTY, "hardware PWM dutycycle not 0-1M"],
   [PI_BAD_HCLK_FREQ, "hardware clock frequency not 4689-250M"],
   [PI_BAD_HCLK_PASS, "need password to use hardware clock 1"],
   [PI_HPWM_ILLEGAL, "illegal, PWM in use for main clock"],
   [PI_BAD_DATABITS, "serial data bits not 1-32"],
   [PI_BAD_STOPBITS, "serial (half) stop bits not 2-8"],
   [PI_MSG_TOOBIG, "socket/pipe message too big"],
   [PI_BAD_MALLOC_MODE, "bad memory allocation mode"],
   [PI_TOO_MANY_SEGS, "too many I2C transaction segments"],
   [PI_BAD_I2C_SEG, "an I2C transaction segment failed"],
   [PI_BAD_SMBUS_CMD, "SMBus command not supported"],
   [PI_NOT_I2C_GPIO, "no bit bang I2C in progress on gpio"],
   [PI_BAD_I2C_WLEN, "bad I2C write length"],
   [PI_BAD_I2C_RLEN, "bad I2C read length"],
   [PI_BAD_I2C_CMD, "bad I2C command"],
   [PI_BAD_I2C_BAUD, "bad I2C baud rate, not 50-500k"],
   [PI_CHAIN_LOOP_CNT, "bad chain loop count"],
   [PI_BAD_CHAIN_LOOP, "empty chain loop"],
   [PI_CHAIN_COUNTER, "too many chain counters"],
   [PI_BAD_CHAIN_CMD, "bad chain command"],
   [PI_BAD_CHAIN_DELAY, "bad chain delay micros"],
   [PI_CHAIN_NESTING, "chain counters nested too deeply"],
   [PI_CHAIN_TOO_BIG, "chain is too long"],
   [PI_DEPRECATED, "deprecated function removed"],
   [PI_BAD_SER_INVERT, "bit bang serial invert not 0 or 1"],
]


class ApigpioError(Exception):
    """pigpio module exception"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def error_text(errnum):
    """
    Returns a text description of a pigpio error.

    errnum:= <0, the error number

    ...
    print(pigpio.error_text(-5))
    level not 0-1
    ...
    """
    for e in _errors:
        if e[0] == errnum:
            return e[1]
    return "unknown error ({})".format(errnum)


# A couple of hacks to cope with different string handling
# between various Python versions
# 3 != 2.7.8 != 2.7.3
# fixme : remove as we only support 3.4+

if sys.hexversion < 0x03000000:
    def _b(x):
        return x
else:
    def _b(x):
        return x.encode('latin-1')

if sys.hexversion < 0x02070800:
    def _str(x):
        return buffer(x)
else:
    def _str(x):
        return x


def u2i(uint32):
    """
    Converts a 32 bit unsigned number to signed.

    uint32:= an unsigned 32 bit number

    ...
    print(u2i(4294967272))
    -24
    print(u2i(37))
    37
    ...
    """
    mask = (2 ** 32) - 1
    if uint32 & (1 << 31):
        v = uint32 | ~mask
    else:
        v = uint32 & mask
    return v


def _u2i(uint32):
    """
    Converts a 32 bit unsigned number to signed.  If the number
    is negative it indicates an error.  On error a pigpio
    exception will be raised if exceptions is True.
    """
    v = u2i(uint32)
    if v < 0:
        if exceptions:
            raise ApigpioError(error_text(v))
    return v


class _callback_ADT:
    """An ADT class to hold callback information."""

    def __init__(self, gpio, edge, func):
        """
        Initialises a callback ADT.

        gpio:= Broadcom gpio number.
        edge:= EITHER_EDGE, RISING_EDGE, or FALLING_EDGE.
        func:= a user function taking three arguments (gpio, level, tick).
        """
        self.gpio = gpio
        self.edge = edge
        self._func = func
        self.bit = 1 << gpio

    @property
    def func(self):
        def _f(*args, **kwargs):
            # protect our-self from faulty callbacks
            try:
                self._func(*args, **kwargs)
            except Exception as e:
                print('Exception raised when running callback {}'.format(e))
        return _f


class _callback_handler(object):
    """
    A class to handle callbacks.
    Each instance of this class open it's own connection to gpiod, which is
    only used to listen for notifications.
    """

    def __init__(self, pi):
        self._loop = pi._loop
        self.pi = pi
        self.handle = None
        self.monitor = 0
        self.callbacks = []
        self.f_stop = asyncio.Future(loop=self._loop)
        self.f_stopped = asyncio.Future(loop=self._loop)

    @asyncio.coroutine
    def _connect(self, address):

        # FIXME: duplication with pi.connect
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Disable the Nagle algorithm.
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.s.setblocking(False)

        # TODO: handle connection errors !
        yield from self._loop.sock_connect(self.s, address)
        self.handle = yield from self._pigpio_aio_command(_PI_CMD_NOIB, 0, 0)
        asyncio.ensure_future(self._wait_for_notif(), loop=self._loop)

    @asyncio.coroutine
    def close(self):
        if not self.f_stop.done():
            self.handle = yield from self._pigpio_aio_command(_PI_CMD_NC,
                                                              self.handle, 0)
            self.f_stop.set_result(True)
            yield from self.f_stopped

    @asyncio.coroutine
    def _wait_for_notif(self):

        last_level = 0

        while True:
            MSG_SIZ = 12
            f_recv = self._loop.sock_recv(self.s, MSG_SIZ)
            tup = yield from asyncio.\
                wait([f_recv, self.f_stop],
                     return_when=asyncio.FIRST_COMPLETED)
            done, pending = tup
            if self.f_stop in done:
                break
            else:
                buf = done.pop().result()
            # buf = yield from self._loop.sock_recv(self.s, MSG_SIZ)

            while len(buf) < MSG_SIZ:
                yield from self._loop.sock_recv(self.s, MSG_SIZ-len(buf))

            seq, flags, tick, level = (struct.unpack('HHII', buf))
            if flags == 0:
                changed = level ^ last_level
                last_level = level
                for cb in self.callbacks:
                    if cb.bit & changed:
                        new_level = 0
                        if cb.bit & level:
                            new_level = 1
                        if cb.edge ^ new_level:
                            cb.func(cb.gpio, new_level, tick)
            else:
                if flags & NTFY_FLAGS_WDOG:
                    print('watchdog signal')
                    gpio = flags & NTFY_FLAGS_GPIO
                    for cb in self.callbacks:
                        if cb.gpio == gpio:
                            cb.func(cb.gpio, TIMEOUT, tick)
                if flags & NTFY_FLAGS_ALIVE:
                    print('keep alive signal')
                # no event for now
                # elif flags & NTFY_FLAGS_EVENT:
                #    event = flags & NTFY_FLAGS_GPIO
                #    for cb in self.events:
                #        if cb.event == event:
                #            cb.func(event, tick)
        self.s.close()
        self.f_stopped.set_result(True)

    @asyncio.coroutine
    def append(self, cb):
        """Adds a callback."""
        self.callbacks.append(cb.callb)
        self.monitor = self.monitor | cb.callb.bit

        yield from self.pi._pigpio_aio_command(_PI_CMD_NB, self.handle,
                                               self.monitor)

    @asyncio.coroutine
    def remove(self, cb):
        """Removes a callback."""
        if cb in self.callbacks:
            self.callbacks.remove(cb)
            new_monitor = 0
            for c in self.callbacks:
                new_monitor |= c.bit
            if new_monitor != self.monitor:
                self.monitor = new_monitor
                yield from self.pi._pigpio_aio_command(
                    _PI_CMD_NB, self.handle, self.monitor)

    @asyncio.coroutine
    def _pigpio_aio_command(self, cmd,  p1, p2,):
        # FIXME: duplication with pi._pigpio_aio_command
        data = struct.pack('IIII', cmd, p1, p2, 0)
        yield from self._loop.sock_sendall(self.s, data)
        response = yield from self._loop.sock_recv(self.s, 16)
        _, res = struct.unpack('12sI', response)
        return res


class Callback:
    """A class to provide gpio level change callbacks."""

    def __init__(self, notify, user_gpio, edge=RISING_EDGE, func=None):
        """
        Initialise a callback and adds it to the notification thread.
        """
        self._notify = notify
        self.count = 0
        if func is None:
            func = self._tally
        self.callb = _callback_ADT(user_gpio, edge, func)
        # FIXME yield from self._notify.append(self.callb)

    @asyncio.coroutine
    def cancel(self):
        """Cancels a callback by removing it from the notification thread."""
        yield from self._notify.remove(self.callb)

    def _tally(self, user_gpio, level, tick):
        """Increment the callback called count."""
        self.count += 1

    def tally(self):
        """
        Provides a count of how many times the default tally
        callback has triggered.

        The count will be zero if the user has supplied their own
        callback function.
        """
        return self.count


class Pi(object):

    @asyncio.coroutine
    def _pigpio_aio_command(self, cmd,  p1, p2,):
        """
        Runs a pigpio socket command.

        sl:= command socket and lock.
        cmd:= the command to be executed.
        p1:= command parameter 1 (if applicable).
         p2:=  command parameter 2 (if applicable).
        """
        with (yield from self._lock):
            data = struct.pack('IIII', cmd, p1, p2, 0)
            yield from self._loop.sock_sendall(self.s, data)
            response = yield from self._loop.sock_recv(self.s, 16)
            _, res = struct.unpack('12sI', response)
            return res

    @asyncio.coroutine
    def _pigpio_aio_command_ext(self, cmd, p1, p2, p3, extents):
        """
        Runs an extended pigpio socket command.

            sl:= command socket and lock.
           cmd:= the command to be executed.
            p1:= command parameter 1 (if applicable).
            p2:= command parameter 2 (if applicable).
            p3:= total size in bytes of following extents
        extents:= additional data blocks
        """
        with (yield from self._lock):
            return (yield from self._pigpio_aio_command_ext_unlocked(cmd, p1, p2, p3, extents))

    @asyncio.coroutine
    def _pigpio_aio_command_ext_unlocked(self, cmd, p1, p2, p3, extents):
        """Run extended pigpio socket command without any lock."""
        ext = bytearray(struct.pack('IIII', cmd, p1, p2, p3))
        for x in extents:
            if isinstance(x, str):
                ext.extend(_b(x))
            else:
                ext.extend(x)
        yield from self._loop.sock_sendall(self.s, ext)
        response = yield from self._loop.sock_recv(self.s, 16)
        _, res = struct.unpack('12sI', response)
        return res

    @asyncio.coroutine
    def connect(self, address):
        """
        Connect to a remote or local gpiod daemon.
        :param address: a pair (address, port), the address must be already
        resolved (for example an ip address)
        :return:
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setblocking(False)
        # Disable the Nagle algorithm.
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        yield from self._loop.sock_connect(self.s, address)

        yield from self._notify._connect(address)

    @asyncio.coroutine
    def stop(self):
        """

        :return:
        """
        print('closing notifier')
        yield from self._notify.close()
        print('closing socket')
        self.s.close()

    @asyncio.coroutine
    def get_version(self):
        res = yield from self._pigpio_aio_command(_PI_CMD_PIGPV)
        print('version: {}'.format(res))

    @asyncio.coroutine
    def get_pigpio_version(self):
        """
        Returns the pigpio software version.

        ...
        v = pi.get_pigpio_version()
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_PIGPV, 0, 0)

    @asyncio.coroutine
    def store_script(self, script):
        """
        Store a script for later execution.

        script:= the script text as a series of bytes.

        Returns a >=0 script id if OK.

        ...
        sid = pi.store_script(
         b'tag 0 w 22 1 mils 100 w 22 0 mils 100 dcr p0 jp 0')
        ...
        """
        if len(script):
            res = yield from self._pigpio_aio_command_ext(_PI_CMD_PROC, 0, 0,
                                                          len(script),
                                                          [script])
            return _u2i(res)
        else:
            return 0

    @asyncio.coroutine
    def run_script(self, script_id, params=None):
        """
        Runs a stored script.

        script_id:= id of stored script.
         params:= up to 10 parameters required by the script.

        ...
        s = pi.run_script(sid, [par1, par2])

        s = pi.run_script(sid)

        s = pi.run_script(sid, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        ...
        """
        # I p1 script id
        # I p2 0
        # I p3 params * 4 (0-10 params)
        # (optional) extension
        # I[] params
        if params is not None:
            ext = bytearray()
            for p in params:
                ext.extend(struct.pack("I", p))
            nump = len(params)
            extents = [ext]
        else:
            nump = 0
            extents = []
        res = yield from self._pigpio_aio_command_ext(_PI_CMD_PROCR, script_id,
                                                      0, nump * 4, extents)
        return _u2i(res)

    @asyncio.coroutine
    def script_status(self, script_id):
        """
        Returns the run status of a stored script as well as the
        current values of parameters 0 to 9.

        script_id:= id of stored script.

        The run status may be

        . .
        PI_SCRIPT_INITING
        PI_SCRIPT_HALTED
        PI_SCRIPT_RUNNING
        PI_SCRIPT_WAITING
        PI_SCRIPT_FAILED
        . .

        The return value is a tuple of run status and a list of
        the 10 parameters.  On error the run status will be negative
        and the parameter list will be empty.

        ...
        (s, pars) = pi.script_status(sid)
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_PROCP, script_id, 0)
        bytes = u2i(res)

        if bytes > 0:

            # Fixme : this sould be the same a _rxbuf
            # data = self._rxbuf(bytes)
            data = yield from self._loop.sock_recv(self.s, bytes)
            while len(data) < bytes:
                b = yield from self._loop.sock_recv(self.s, bytes-len(data))
                data.extend(b)

            pars = struct.unpack('11i', _str(data))
            status = pars[0]
            params = pars[1:]
        else:
            status = bytes
            params = ()
        return status, params

    @asyncio.coroutine
    def stop_script(self, script_id):
        """
        Stops a running script.

        script_id:= id of stored script.

        ...
        status = pi.stop_script(sid)
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_PROCS, script_id, 0)
        return _u2i(res)

    @asyncio.coroutine
    def delete_script(self, script_id):
        """
        Deletes a stored script.

        script_id:= id of stored script.

        ...
        status = pi.delete_script(sid)
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_PROCD, script_id, 0)
        return _u2i(res)

    @asyncio.coroutine
    def read_bank_1(self):
        """
        Returns the levels of the bank 1 gpios (gpios 0-31).

        The returned 32 bit integer has a bit set if the corresponding
        gpio is high.  Gpio n has bit value (1<<n).

        ...
        print(bin(pi.read_bank_1()))
        0b10010100000011100100001001111
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_BR1, 0, 0)
        return res

    @asyncio.coroutine
    def clear_bank_1(self, bits):
        """
        Clears gpios 0-31 if the corresponding bit in bits is set.

        bits:= a 32 bit mask with 1 set if the corresponding gpio is
             to be cleared.

        A returned status of PI_SOME_PERMITTED indicates that the user
        is not allowed to write to one or more of the gpios.

        ...
        pi.clear_bank_1(int("111110010000",2))
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_BC1, bits, 0)
        return _u2i(res)

    @asyncio.coroutine
    def set_bank_1(self, bits):
        """
        Sets gpios 0-31 if the corresponding bit in bits is set.

        bits:= a 32 bit mask with 1 set if the corresponding gpio is
             to be set.

        A returned status of PI_SOME_PERMITTED indicates that the user
        is not allowed to write to one or more of the gpios.

        ...
        pi.set_bank_1(int("111110010000",2))
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_BS1, bits, 0)
        return _u2i(res)

    @asyncio.coroutine
    def set_mode(self, gpio, mode):
        """
        Sets the gpio mode.

        gpio:= 0-53.
        mode:= INPUT, OUTPUT, ALT0, ALT1, ALT2, ALT3, ALT4, ALT5.

        ...
        pi.set_mode( 4, apigpio.INPUT)  # gpio  4 as input
        pi.set_mode(17, apigpio.OUTPUT) # gpio 17 as output
        pi.set_mode(24, apigpio.ALT2)   # gpio 24 as ALT2
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_MODES, gpio, mode)
        return _u2i(res)

    @asyncio.coroutine
    def set_pull_up_down(self, gpio, pud):
        """
        Sets or clears the internal GPIO pull-up/down resistor.
        gpio:= 0-53.
         pud:= PUD_UP, PUD_DOWN, PUD_OFF.
        ...
        yield from pi.set_pull_up_down(17, apigpio.PUD_OFF)
        yield from pi.set_pull_up_down(23, apigpio.PUD_UP)
        yield from pi.set_pull_up_down(24, apigpio.PUD_DOWN)
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_PUD, gpio, pud)
        return _u2i(res)

    @asyncio.coroutine
    def get_mode(self, gpio):
        """
        Returns the gpio mode.

        gpio:= 0-53.

        Returns a value as follows

        . .
        0 = INPUT
        1 = OUTPUT
        2 = ALT5
        3 = ALT4
        4 = ALT0
        5 = ALT1
        6 = ALT2
        7 = ALT3
        . .

        ...
        print(pi.get_mode(0))
        4
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_MODEG, gpio, 0)
        return _u2i(res)

    @asyncio.coroutine
    def write(self, gpio, level):
        """
        Sets the gpio level.

        gpio:= 0-53.
        level:= 0, 1.

        If PWM or servo pulses are active on the gpio they are
        switched off.

        ...
        pi.set_mode(17, pigpio.OUTPUT)

        pi.write(17,0)
        print(pi.read(17))
        0

        pi.write(17,1)
        print(pi.read(17))
        1
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_WRITE, gpio, level)
        return _u2i(res)

    @asyncio.coroutine
    def read(self, gpio):
        """
        Returns the GPIO level.
        gpio:= 0-53.
        ...
        yield from pi.set_mode(23, pigpio.INPUT)
        yield from pi.set_pull_up_down(23, pigpio.PUD_DOWN)
        print(yield from pi.read(23))
        0
        yield from pi.set_pull_up_down(23, pigpio.PUD_UP)
        print(yield from pi.read(23))
        1
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_READ, gpio, 0)
        return _u2i(res)

    @asyncio.coroutine
    def gpio_trigger(self, user_gpio, pulse_len=10, level=1):
        """
        Send a trigger pulse to a GPIO.  The GPIO is set to
        level for pulse_len microseconds and then reset to not level.
        user_gpio:= 0-31
        pulse_len:= 1-100
            level:= 0-1
        ...
        pi.gpio_trigger(23, 10, 1)
        ...
        """
        # pigpio message format

        # I p1 user_gpio
        # I p2 pulse_len
        # I p3 4
        ## extension ##
        # I level
        extents = [struct.pack("I", level)]
        res = yield from self._pigpio_aio_command_ext(_PI_CMD_TRIG, user_gpio,
                                                      pulse_len, 4, extents)
        return _u2i(res)

    @asyncio.coroutine
    def set_glitch_filter(self, user_gpio, steady):
        """
        Sets a glitch filter on a GPIO.
        Level changes on the GPIO are not reported unless the level
        has been stable for at least [*steady*] microseconds.  The
        level is then reported.  Level changes of less than [*steady*]
        microseconds are ignored.
        user_gpio:= 0-31
           steady:= 0-300000
        Returns 0 if OK, otherwise PI_BAD_USER_GPIO, or PI_BAD_FILTER.
        This filter affects the GPIO samples returned to callbacks set up
        with [*callback*] and [*wait_for_edge*].
        It does not affect levels read by [*read*],
        [*read_bank_1*], or [*read_bank_2*].
        Each (stable) edge will be timestamped [*steady*]
        microseconds after it was first detected.
        ...
        pi.set_glitch_filter(23, 100)
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_FG, user_gpio, steady)
        return _u2i(res)

    @asyncio.coroutine
    def set_noise_filter(self, user_gpio, steady, active):
        """
        Sets a noise filter on a GPIO.
        Level changes on the GPIO are ignored until a level which has
        been stable for [*steady*] microseconds is detected.  Level
        changes on the GPIO are then reported for [*active*]
        microseconds after which the process repeats.
        user_gpio:= 0-31
           steady:= 0-300000
           active:= 0-1000000
        Returns 0 if OK, otherwise PI_BAD_USER_GPIO, or PI_BAD_FILTER.
        This filter affects the GPIO samples returned to callbacks set up
        with [*callback*] and [*wait_for_edge*].
        It does not affect levels read by [*read*],
        [*read_bank_1*], or [*read_bank_2*].
        Level changes before and after the active period may
        be reported.  Your software must be designed to cope with
        such reports.
        ...
        pi.set_noise_filter(23, 1000, 5000)
        ...
        """
        # pigpio message format

        # I p1 user_gpio
        # I p2 steady
        # I p3 4
        ## extension ##
        # I active
        extents = [struct.pack("I", active)]
        res = yield from self._pigpio_aio_command_ext(_PI_CMD_FN, user_gpio,
                                                      steady, 4, extents)
        return _u2i(res)

    @asyncio.coroutine
    def set_PWM_dutycycle(self, user_gpio, dutycycle):
        """
        Starts (non-zero dutycycle) or stops (0) PWM pulses on the GPIO.
        user_gpio:= 0-31.
        dutycycle:= 0-range (range defaults to 255).
        The [*set_PWM_range*] function can change the default range of 255.
        ...
        pi.set_PWM_dutycycle(4,   0) # PWM off
        pi.set_PWM_dutycycle(4,  64) # PWM 1/4 on
        pi.set_PWM_dutycycle(4, 128) # PWM 1/2 on
        pi.set_PWM_dutycycle(4, 192) # PWM 3/4 on
        pi.set_PWM_dutycycle(4, 255) # PWM full on
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_PWM, user_gpio, int(dutycycle))
        return _u2i(res)

    @asyncio.coroutine
    def add_callback(self, user_gpio, edge=RISING_EDGE, func=None):
        """
        Calls a user supplied function (a callback) whenever the
        specified gpio edge is detected.

        user_gpio:= 0-31.
           edge:= EITHER_EDGE, RISING_EDGE (default), or FALLING_EDGE.
           func:= user supplied callback function.

        The user supplied callback receives three parameters, the gpio,
        the level, and the tick.

        If a user callback is not specified a default tally callback is
        provided which simply counts edges.  The count may be retrieved
        by calling the tally function.

        The callback may be cancelled by calling the cancel function.

        A gpio may have multiple callbacks (although I can't think of
        a reason to do so).

        ...
        def cbf(gpio, level, tick):
         print(gpio, level, tick)

        cb1 = pi.callback(22, pigpio.EITHER_EDGE, cbf)

        cb2 = pi.callback(4, pigpio.EITHER_EDGE)

        cb3 = pi.callback(17)

        print(cb3.tally())

        cb1.cancel() # To cancel callback cb1.
        ...
        """

        cb = Callback(self._notify, user_gpio, edge, func)
        yield from self._notify.append(cb)

        return cb

    @asyncio.coroutine
    def set_servo_pulsewidth(self, user_gpio, pulsewidth):
        """
        Starts (500-2500) or stops (0) servo pulses on the GPIO.
         user_gpio:= 0-31.
        pulsewidth:= 0 (off),
                     500 (most anti-clockwise) - 2500 (most clockwise).
        The selected pulsewidth will continue to be transmitted until
        changed by a subsequent call to set_servo_pulsewidth.
        The pulsewidths supported by servos varies and should probably
        be determined by experiment. A value of 1500 should always be
        safe and represents the mid-point of rotation.
        You can DAMAGE a servo if you command it to move beyond its
        limits.
        ...
        yield from pi.set_servo_pulsewidth(17, 0)    # off
        yield from pi.set_servo_pulsewidth(17, 1000) # safe anti-clockwise
        yield from pi.set_servo_pulsewidth(17, 1500) # centre
        yield from pi.set_servo_pulsewidth(17, 2000) # safe clockwise
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_SERVO, user_gpio, int(pulsewidth))
        return _u2i(res)

    @asyncio.coroutine
    def bb_spi_open(self, cs, miso, mosi, sclk ,b, spf):
        """Open a bspi device on a bus."""
        extents = [struct.pack('IIIII', int(miso), int(mosi), int(sclk), int(b), int(spf))]
        res = yield from self._pigpio_aio_command_ext(_PI_CMD_BSPIO, cs, 0, 20, extents=extents)
        return _u2i(res)

    @asyncio.coroutine
    def bb_spi_close(self, cs):
        """Close a bspi device on a bus."""
        res = yield from self._pigpio_aio_command(_PI_CMD_BSPIC, cs, 0)
        return _u2i(res)

    @asyncio.coroutine
    def bb_spi_xfer(self, cs, data):
        bytes = PI_CMD_INTERRUPTED
        with (yield from self._lock):
            bytes = yield from self._pigpio_aio_command_ext_unlocked(
                _PI_CMD_BSPIX, cs, 0, len(data), [data])
            if bytes > 0:
                data = yield from self._rxbuf(bytes)
            else:
                data = ""
        return bytes, data

    @asyncio.coroutine
    def i2c_open(self, bus, address):
        """Open an i2c device on a bus."""
        res = yield from self._pigpio_aio_command(_PI_CMD_I2CO, int(bus), int(address))
        return _u2i(res)

    @asyncio.coroutine
    def i2c_close(self, handle):
        """Close an i2c handle."""
        res = yield from self._pigpio_aio_command(_PI_CMD_I2CC, handle)
        return _u2i(res)

    @asyncio.coroutine
    def i2c_write_byte_data(self, handle, register, data):
        """Write byte to i2c register on handle."""
        extents = [struct.pack("I", data)]
        res = yield from self._pigpio_aio_command_ext(_PI_CMD_I2CWB, handle, int(register), 1, extents)
        return _u2i(res)

    @asyncio.coroutine
    def _rxbuf(self, count):
        """"Returns count bytes from the command socket."""
        ext = yield from self._loop.sock_recv(self.s, count)
        while len(ext) < count:
            ext.extend((yield from self._loop.sock_recv(self.s, count - len(ext))))
        return ext

    @asyncio.coroutine
    def i2c_read_byte_data(self, handle, register):
        """Write byte to i2c register on handle."""
        res = yield from self._pigpio_aio_command(_PI_CMD_I2CRB, handle, int(register))
        return _u2i(res)

    @asyncio.coroutine
    def i2c_read_i2c_block_data(self, handle, register, count):
        """Read count bytes from an i2c handle."""
        extents = [struct.pack("I", count)]
        with (yield from self._lock):
            bytes = yield from self._pigpio_aio_command_ext_unlocked(_PI_CMD_I2CRI, handle, int(register), 4, extents)
            if bytes > 0:
                data = yield from self._rxbuf(count)
            else:
                data = ""
        return data

    def __init__(self, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self.s = None
        self._notify = _callback_handler(self)
        self._lock = asyncio.Lock()
