import enum

from numpy.typing import ArrayLike


class FilterMode(enum.Enum):
    NONE = 0

    Linear = 1

    Bilinear = 2

    Box = 3

class FourCC(enum.Enum):
    I420 = 808596553

    I422 = 842150985

    I444 = 875836489

    I400 = 808465481

    NV21 = 825382478

    NV12 = 842094158

    YUY2 = 844715353

    UYVY = 1498831189

    I010 = 808529993

    I210 = 808530505

    M420 = 808596557

    ARGB = 1111970369

    BGRA = 1095911234

    ABGR = 1380401729

    AR30 = 808669761

    AB30 = 808665665

    AR64 = 875975233

    AB64 = 875971137

    24BG = 1195521074

    RAW = 544694642

    RGBA = 1094862674

    RGBP = 1346520914

    RGBO = 1329743698

    R444 = 875836498

    MJPG = 1196444237

    YV12 = 842094169

    YV16 = 909203033

    YV24 = 875714137

    YU12 = 842093913

    J420 = 808596554

    J422 = 842150986

    J444 = 875836490

    J400 = 808465482

    F420 = 808596550

    F422 = 842150982

    F444 = 875836486

    H420 = 808596552

    H422 = 842150984

    H444 = 875836488

    U420 = 808596565

    U422 = 842150997

    U444 = 875836501

    F010 = 808529990

    H010 = 808529992

    U010 = 808530005

    F210 = 808530502

    H210 = 808530504

    U210 = 808530517

    P010 = 808530000

    P210 = 808530512

    IYUV = 1448433993

    YU16 = 909202777

    YU24 = 875713881

    YUYV = 1448695129

    YUVS = 1937143161

    HDYC = 1129923656

    2VUY = 2037741106

    JPEG = 1195724874

    DMB1 = 828534116

    BA81 = 825770306

    RGB3 = 859981650

    BGR3 = 861030210

    CM32 = 536870912

    CM24 = 402653184

    L555 = 892679500

    L565 = 892745036

    5551 = 825570613

    I411 = 825308233

    Q420 = 808596561

    RGGB = 1111967570

    BGGR = 1380403010

    GRBG = 1195528775

    GBRG = 1196573255

    H264 = 875967048

    ANY = -1

I420: FourCC = FourCC.I420

I422: FourCC = FourCC.I422

I444: FourCC = FourCC.I444

I400: FourCC = FourCC.I400

NV21: FourCC = FourCC.NV21

NV12: FourCC = FourCC.NV12

YUY2: FourCC = FourCC.YUY2

UYVY: FourCC = FourCC.UYVY

I010: FourCC = FourCC.I010

I210: FourCC = FourCC.I210

M420: FourCC = FourCC.M420

ARGB: FourCC = FourCC.ARGB

BGRA: FourCC = FourCC.BGRA

ABGR: FourCC = FourCC.ABGR

AR30: FourCC = FourCC.AR30

AB30: FourCC = FourCC.AB30

AR64: FourCC = FourCC.AR64

AB64: FourCC = FourCC.AB64

24BG: FourCC = FourCC.24BG

RAW: FourCC = FourCC.RAW

RGBA: FourCC = FourCC.RGBA

RGBP: FourCC = FourCC.RGBP

RGBO: FourCC = FourCC.RGBO

R444: FourCC = FourCC.R444

MJPG: FourCC = FourCC.MJPG

YV12: FourCC = FourCC.YV12

YV16: FourCC = FourCC.YV16

YV24: FourCC = FourCC.YV24

YU12: FourCC = FourCC.YU12

J420: FourCC = FourCC.J420

J422: FourCC = FourCC.J422

J444: FourCC = FourCC.J444

J400: FourCC = FourCC.J400

F420: FourCC = FourCC.F420

F422: FourCC = FourCC.F422

F444: FourCC = FourCC.F444

H420: FourCC = FourCC.H420

H422: FourCC = FourCC.H422

H444: FourCC = FourCC.H444

U420: FourCC = FourCC.U420

U422: FourCC = FourCC.U422

U444: FourCC = FourCC.U444

F010: FourCC = FourCC.F010

H010: FourCC = FourCC.H010

U010: FourCC = FourCC.U010

F210: FourCC = FourCC.F210

H210: FourCC = FourCC.H210

U210: FourCC = FourCC.U210

P010: FourCC = FourCC.P010

P210: FourCC = FourCC.P210

IYUV: FourCC = FourCC.IYUV

YU16: FourCC = FourCC.YU16

YU24: FourCC = FourCC.YU24

YUYV: FourCC = FourCC.YUYV

YUVS: FourCC = FourCC.YUVS

HDYC: FourCC = FourCC.HDYC

2VUY: FourCC = FourCC.2VUY

JPEG: FourCC = FourCC.JPEG

DMB1: FourCC = FourCC.DMB1

BA81: FourCC = FourCC.BA81

RGB3: FourCC = FourCC.RGB3

BGR3: FourCC = FourCC.BGR3

CM32: FourCC = FourCC.CM32

CM24: FourCC = FourCC.CM24

L555: FourCC = FourCC.L555

L565: FourCC = FourCC.L565

5551: FourCC = FourCC.5551

I411: FourCC = FourCC.I411

Q420: FourCC = FourCC.Q420

RGGB: FourCC = FourCC.RGGB

BGGR: FourCC = FourCC.BGGR

GRBG: FourCC = FourCC.GRBG

GBRG: FourCC = FourCC.GBRG

H264: FourCC = FourCC.H264

ANY: FourCC = FourCC.ANY

class RotationMode(enum.Enum):
    Rotate0 = 0

    Rotate90 = 90

    Rotate180 = 180

    Rotate270 = 270

Rotate0: RotationMode = RotationMode.Rotate0

Rotate90: RotationMode = RotationMode.Rotate90

Rotate180: RotationMode = RotationMode.Rotate180

Rotate270: RotationMode = RotationMode.Rotate270

def nv12_scale(src_y: ArrayLike, src_uv: ArrayLike, src_stride_y: int, src_stride_uv: int, src_width: int, src_height: int, dst_y: ArrayLike, dst_uv: ArrayLike, dst_stride_y: int, dst_stride_uv: int, dst_width: int, dst_height: int, filtering: FilterMode) -> int: ...

def i420_scale(src_y: ArrayLike, src_u: ArrayLike, src_v: ArrayLike, src_stride_y: int, src_stride_u: int, src_stride_v: int, src_width: int, src_height: int, dst_y: ArrayLike, dst_u: ArrayLike, dst_v: ArrayLike, dst_stride_y: int, dst_stride_u: int, dst_stride_v: int, dst_width: int, dst_height: int, filtering: FilterMode) -> int: ...

def convert_to_i420(sample: ArrayLike, sample_size: int, dst_y: ArrayLike, dst_stride_y: int, dst_u: ArrayLike, dst_stride_u: int, dst_v: ArrayLike, dst_stride_v: int, crop_x: int, crop_y: int, src_width: int, src_height: int, crop_width: int, crop_height: int, rotation: RotationMode, fourcc: FourCC) -> int: ...

def nv12_to_i420(src_y: ArrayLike, src_uv: ArrayLike, src_stride_y: int, src_stride_uv: int, dst_y: ArrayLike, dst_u: ArrayLike, dst_v: ArrayLike, dst_stride_y: int, dst_stride_u: int, dst_stride_v: int, width: int, height: int) -> int: ...

def i420_to_nv12(src_y: ArrayLike, src_u: ArrayLike, src_v: ArrayLike, src_stride_y: int, src_stride_u: int, src_stride_v: int, dst_y: ArrayLike, dst_uv: ArrayLike, dst_stride_y: int, dst_stride_uv: int, width: int, height: int) -> int: ...

def rgb24_to_i420(src_rgb24: ArrayLike, src_stride_rgb24: int, dst_y: ArrayLike, dst_u: ArrayLike, dst_v: ArrayLike, dst_stride_y: int, dst_stride_u: int, dst_stride_v: int, width: int, height: int) -> int: ...

def i420_to_rgb24(src_y: ArrayLike, src_u: ArrayLike, src_v: ArrayLike, src_stride_y: int, src_stride_u: int, src_stride_v: int, dst_rgb24: ArrayLike, dst_stride_rgb24: int, width: int, height: int) -> int: ...
