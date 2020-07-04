# gpio levels

OFF = 0
LOW = 0
CLEAR = 0

ON = 1
HIGH = 1
SET = 1

TIMEOUT = 2

# gpio edges

RISING_EDGE = 0
FALLING_EDGE = 1
EITHER_EDGE = 2

# gpio modes

INPUT = 0
OUTPUT = 1
ALT0 = 4
ALT1 = 5
ALT2 = 6
ALT3 = 7
ALT4 = 3
ALT5 = 2

# gpio Pull Up Down

PUD_OFF = 0
PUD_DOWN = 1
PUD_UP = 2

# script run status

PI_SCRIPT_INITING = 0
PI_SCRIPT_HALTED = 1
PI_SCRIPT_RUNNING = 2
PI_SCRIPT_WAITING = 3
PI_SCRIPT_FAILED = 4

# notification flags

NTFY_FLAGS_ALIVE = (1 << 6)
NTFY_FLAGS_WDOG = (1 << 5)
NTFY_FLAGS_GPIO = 31

# pigpio error numbers

PI_INIT_FAILED = -1
PI_BAD_USER_GPIO = -2
PI_BAD_GPIO = -3
PI_BAD_MODE = -4
PI_BAD_LEVEL = -5
PI_BAD_PUD = -6
PI_BAD_PULSEWIDTH = -7
PI_BAD_DUTYCYCLE = -8
PI_BAD_TIMER = -9
PI_BAD_MS = -10
PI_BAD_TIMETYPE = -11
PI_BAD_SECONDS = -12
PI_BAD_MICROS = -13
PI_TIMER_FAILED = -14
PI_BAD_WDOG_TIMEOUT = -15
PI_NO_ALERT_FUNC = -16
PI_BAD_CLK_PERIPH = -17
PI_BAD_CLK_SOURCE = -18
PI_BAD_CLK_MICROS = -19
PI_BAD_BUF_MILLIS = -20
PI_BAD_DUTYRANGE = -21
PI_BAD_SIGNUM = -22
PI_BAD_PATHNAME = -23
PI_NO_HANDLE = -24
PI_BAD_HANDLE = -25
PI_BAD_IF_FLAGS = -26
PI_BAD_CHANNEL = -27
PI_BAD_PRIM_CHANNEL = -27
PI_BAD_SOCKET_PORT = -28
PI_BAD_FIFO_COMMAND = -29
PI_BAD_SECO_CHANNEL = -30
PI_NOT_INITIALISED = -31
PI_INITIALISED = -32
PI_BAD_WAVE_MODE = -33
PI_BAD_CFG_INTERNAL = -34
PI_BAD_WAVE_BAUD = -35
PI_TOO_MANY_PULSES = -36
PI_TOO_MANY_CHARS = -37
PI_NOT_SERIAL_GPIO = -38
PI_BAD_SERIAL_STRUC = -39
PI_BAD_SERIAL_BUF = -40
PI_NOT_PERMITTED = -41
PI_SOME_PERMITTED = -42
PI_BAD_WVSC_COMMND = -43
PI_BAD_WVSM_COMMND = -44
PI_BAD_WVSP_COMMND = -45
PI_BAD_PULSELEN = -46
PI_BAD_SCRIPT = -47
PI_BAD_SCRIPT_ID = -48
PI_BAD_SER_OFFSET = -49
PI_GPIO_IN_USE = -50
PI_BAD_SERIAL_COUNT = -51
PI_BAD_PARAM_NUM = -52
PI_DUP_TAG = -53
PI_TOO_MANY_TAGS = -54
PI_BAD_SCRIPT_CMD = -55
PI_BAD_VAR_NUM = -56
PI_NO_SCRIPT_ROOM = -57
PI_NO_MEMORY = -58
PI_SOCK_READ_FAILED = -59
PI_SOCK_WRIT_FAILED = -60
PI_TOO_MANY_PARAM = -61
PI_NOT_HALTED = -62
PI_BAD_TAG = -63
PI_BAD_MICS_DELAY = -64
PI_BAD_MILS_DELAY = -65
PI_BAD_WAVE_ID = -66
PI_TOO_MANY_CBS = -67
PI_TOO_MANY_OOL = -68
PI_EMPTY_WAVEFORM = -69
PI_NO_WAVEFORM_ID = -70
PI_I2C_OPEN_FAILED = -71
PI_SER_OPEN_FAILED = -72
PI_SPI_OPEN_FAILED = -73
PI_BAD_I2C_BUS = -74
PI_BAD_I2C_ADDR = -75
PI_BAD_SPI_CHANNEL = -76
PI_BAD_FLAGS = -77
PI_BAD_SPI_SPEED = -78
PI_BAD_SER_DEVICE = -79
PI_BAD_SER_SPEED = -80
PI_BAD_PARAM = -81
PI_I2C_WRITE_FAILED = -82
PI_I2C_READ_FAILED = -83
PI_BAD_SPI_COUNT = -84
PI_SER_WRITE_FAILED = -85
PI_SER_READ_FAILED = -86
PI_SER_READ_NO_DATA = -87
PI_UNKNOWN_COMMAND = -88
PI_SPI_XFER_FAILED = -89
PI_BAD_POINTER = -90
PI_NO_AUX_SPI = -91
PI_NOT_PWM_GPIO = -92
PI_NOT_SERVO_GPIO = -93
PI_NOT_HCLK_GPIO = -94
PI_NOT_HPWM_GPIO = -95
PI_BAD_HPWM_FREQ = -96
PI_BAD_HPWM_DUTY = -97
PI_BAD_HCLK_FREQ = -98
PI_BAD_HCLK_PASS = -99
PI_HPWM_ILLEGAL = -100
PI_BAD_DATABITS = -101
PI_BAD_STOPBITS = -102
PI_MSG_TOOBIG = -103
PI_BAD_MALLOC_MODE = -104
PI_TOO_MANY_SEGS = -105
PI_BAD_I2C_SEG = -106
PI_BAD_SMBUS_CMD = -107
PI_NOT_I2C_GPIO = -108
PI_BAD_I2C_WLEN = -109
PI_BAD_I2C_RLEN = -110
PI_BAD_I2C_CMD = -111
PI_BAD_I2C_BAUD = -112
PI_CHAIN_LOOP_CNT = -113
PI_BAD_CHAIN_LOOP = -114
PI_CHAIN_COUNTER = -115
PI_BAD_CHAIN_CMD = -116
PI_BAD_CHAIN_DELAY = -117
PI_CHAIN_NESTING = -118
PI_CHAIN_TOO_BIG = -119
PI_DEPRECATED = -120
PI_BAD_SER_INVERT = -121
_PI_BAD_EDGE = -122
_PI_BAD_ISR_INIT = -123
PI_BAD_FOREVER = -124
PI_BAD_FILTER = -125
PI_BAD_PAD = -126
PI_BAD_STRENGTH = -127
PI_FIL_OPEN_FAILED = -128
PI_BAD_FILE_MODE = -129
PI_BAD_FILE_FLAG = -130
PI_BAD_FILE_READ = -131
PI_BAD_FILE_WRITE = -132
PI_FILE_NOT_ROPEN = -133
PI_FILE_NOT_WOPEN = -134
PI_BAD_FILE_SEEK = -135
PI_NO_FILE_MATCH = -136
PI_NO_FILE_ACCESS = -137
PI_FILE_IS_A_DIR = -138
PI_BAD_SHELL_STATUS = -139
PI_BAD_SCRIPT_NAME = -140
PI_BAD_SPI_BAUD = -141
PI_NOT_SPI_GPIO = -142
PI_BAD_EVENT_ID = -143
PI_CMD_INTERRUPTED = -144
PI_NOT_ON_BCM2711 = -145
PI_ONLY_ON_BCM2711 = -146
