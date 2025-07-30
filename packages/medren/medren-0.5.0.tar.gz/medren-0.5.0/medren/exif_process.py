import datetime
import logging
from dataclasses import dataclass
from enum import IntEnum
from typing import Any

from medren.timezone_offset import get_timezone_offset


class ExifStat(IntEnum):
    UnknownErr = 0
    FileNotFound = 1
    Unsupported = 2
    NoExif = 3
    NoDateTime = 4
    InvalidDateTime = 5
    ValidExif = 6


ExifRaw = dict
TOffset = float | int | None

logger = logging.getLogger()

@dataclass
class ExifClass:
    # class MyExif(NamedTuple):
    # File Type                       : JPEG
    # Date/Time Original              : 2020:04:24 12:07:46
    # Create Date                     : 2020:04:24 12:07:46
    # Make                            : samsung
    # Camera Model Name               : SM-G975F
    # Image Size                      : 2944x2208
    # GPS Latitude                    : 32 deg 34' 13.22" N
    # GPS Longitude                   : 34 deg 56' 29.58" E
    ext: str
    backend: str
    dt: datetime.datetime | None = None
    is_utc: bool | None = None
    t_org: str | None = None
    t_dig: str | None = None
    t_img: str | None = None
    t_fn: str | None = None

    t_offset: TOffset = None
    t_offset_dig: TOffset = None
    t_offset_img: TOffset = None
    t_offset_ll: TOffset = None

    make: str | None = None
    model: str | None = None
    w: int | None = None
    h: int | None = None
    iw: int | None = None
    ih: int | None = None
    lat: float | None = None
    lon: float | None = None
    alt: float | None = None

    # all: dict | None = None

    # @classmethod
    # def is_supported(cls, filename: Path):
    #     return filename.suffix.lower() in ['.jpg', '.jpeg', '.tif', '.tiff']
    def get_exif_kwargs(self, none_value=None):
        return dict(
            make=self.make or none_value,
            model=self.model or none_value,
            w=self.w or none_value,
            h=self.h or none_value,
            lat=self.lat or none_value,
            lon=self.lon or none_value,
        )

    def __post_init__(self):
        self.t_offset_form_loc(logger)

    def t_offset_form_loc(self, logger: logging.Logger):
        try:
            if self.is_utc and self.t_offset is not None:
                self.is_utc = False
                self.dt = self.dt + datetime.timedelta(hours=self.t_offset)
            if self.lat and self.lon and self.dt:
                self.t_offset_ll = get_timezone_offset(lat=self.lat, lon=self.lon, date=self.dt)
                if self.t_offset_ll:
                    if self.is_utc:
                        self.is_utc = False
                        self.dt = self.dt + datetime.timedelta(hours=self.t_offset_ll)
                    if not self.t_offset:
                        self.t_offset = self.t_offset_ll
                        # pass
                    elif self.t_offset == self.t_offset_ll:
                        pass
                    else:
                        logger.warning(f"time offset mismatch {self.t_offset} != {self.t_offset_ll} {self}")
        except Exception as e:
            logger.warning(f"Failed to fetch time offset {self} ({e})")


makers = {
    'Hewlett-Packard': 'HP',
    'Samsung': 'Samsung',
    'FUJIFILM': 'Fujifilm',
    'FUJI': 'Fujifilm',
    'NIKON': 'Nikon',
    'OLYMPUS': 'Olympus',
}
makers = {str(k).lower(): v for k, v in makers.items()}


# def nice_model(model: str) -> str:
#     spam_words = ('SAMSUNG-',)
#     for spam in spam_words:
#         model = model.replace(spam, '')
#     return model


def make_by_model(model: str | None) -> str | None:
    if not model:
        return None
    parts = model.replace('_', ' ').replace('-', ' ').split(' ')
    model_prefix = parts[0].lower()
    model_prefix_to_make = {
        "dmc": 'Panasonic',
        "samsung": 'Samsung',
    }
    return model_prefix_to_make.get(model_prefix)


def clean_make_or_model(name: str | None) -> str | None:
    # makes = ['Canon', 'HP', 'NIKON CORPORATION', 'OLYMPUS OPTICAL CO.,LTD', 'Google', 'FUJIFILM', 'SONY',
    # 'Panasonic', 'SAMSUNG', 'samsung', 'MOTOROLA', 'Hewlett-Packard', 'EASTMAN KODAK COMPANY', 'Apple',
    # 'NIKON', 'SANYO Electric Co.,Ltd',
    # 'OLYMPUS_IMAGING_CORP.', 'KONICA MINOLTA', 'LGE', 'PENTAX Corporation', 'OLYMPUS IMAGING CORP.', 'DSCimg',
    # 'CASIO COMPUTER CO.,LTD.', 'Research In Motion', 'Minolta Co., Ltd.', 'Samsung Techwin', 'OLYMPUS CORPORATION',
    # 'Toshiba', 'LG Electronics', 'Nokia', 'Microtek', 'DIGITAL', 'AgfaPhoto GmbH', 'Xiaomi',
    # 'Hewlett-Packard Company', 'Sony Ericsson', 'Zoran Corporation', 'FUJI PHOTO FILM CO., LTD.']
    if not name:
        return None
    name = fix_make_model_base(name)
    spam_words = (
        'CORP', 'CORPORATION', 'CO.,LTD', 'LTD', 'EASTMAN', 'COMPANY', 'Electric', 'IMAGING', 'Electronics',
        'COMPUTER', 'PHOTO', 'FILM', 'OPTICAL')
    def normalize_spam(s: str) -> str:
        return s.upper().replace('.', '').replace(',', '').replace('-', '').replace('_', '')
    spam_words = [normalize_spam(s) for s in spam_words]

    parts = name.split(sep=' ')
    maker_parts = []
    for part in parts:
        if normalize_spam(part) not in spam_words:
            nice_part = makers.get(part.lower(), part)
            maker_parts.append(nice_part)
    name = ' '.join(maker_parts)
    return name


def tag_friendly(s: str | None) -> str | None:
    if not s:
        return None
    return s.replace(' ', '-').replace('_', '-')

def clean_make_model(make: str | None, model: str | None) -> tuple[str | None, str | None]:
    make = clean_make_or_model(make)
    model = clean_make_or_model(model)
    if make and model:
        model_parts = model.replace('_',' ').replace('-', ' ').split(' ')
        make_parts = make.lower().replace('_',' ').replace('-', ' ').split(' ')
        new_parts = []
        for part in model_parts:
            if part.lower() not in make_parts:
                # remove maker name from model
                new_parts.append(part)
        model = ' '.join(new_parts)
        # model = nice_model(model)
    elif model:
        make = make_by_model(model)
    model = tag_friendly(model)
    make = tag_friendly(make)
    return make, model


def filename_friendly(s: str, keep=(' ','.','_','-')) -> str:
    s = "".join(c for c in s if c.isalnum() or c in keep).rstrip()
    return s


def fix_make_model_base(s: str | None) -> str | None:
    if not s:
        return None
    s = s.strip().strip('\x00').replace('_', ' ')
    s = filename_friendly(s)
    return s


OrgExifDict = dict[dict[str, Any]]


def exif_dict_decode(d: OrgExifDict):
    for tags in d.values():
        for k, tag in tags.items():
            if isinstance(tag, bytes):
                tags[k] = tag.decode("ascii")


# GPS Latitude                    : 32 deg 33' 56.49" N
# GPS Longitude                   : 34 deg 56' 12.15" E
# ((32, 1), (33, 1), (56494080, 1000000))

def parse_gps(p, ref) -> float | None:
    if not p:
        return None
    d = p[0][0] / p[0][1]
    m = p[1][0] / p[1][1]
    s = p[2][0] / p[2][1]
    dms = d + m / 60 + s / 3600
    if ref in [b'S', b'W']:
        return -dms
    return dms

def parse_float(p, ref, digits: int) -> float | None:
    if not p:
        return None
    p = p[0] / p[1]
    if digits:
        p = round(p, digits)
    return p


def parse_offset(t_offset: str | None, logger: logging.Logger) -> float | None:
    if not t_offset:
        return None
    try:
        t_offset_len = 6
        if len(t_offset) >= t_offset_len:
            sign = 1 if t_offset[-6] == '+' else -1
            hours = int(t_offset[-5:-3])
            minutes = int(t_offset[-2:])
            return sign * (hours + minutes/60)
    except Exception as e:
        logger.debug(f"Could not parse offset {t_offset}: {e}")
    return None

def extract_datetime_with_optional_t_offset(date_str: str, logger: logging.Logger) -> tuple[datetime.datetime | None, TOffset]:
    dt, t_offset = None, None
    dt_len = 19
    if len(date_str) >= dt_len:
        if len(date_str) > dt_len:
            t_offset = date_str[dt_len:]
            t_offset = parse_offset(t_offset, logger)
            date_str = date_str[:dt_len]
        dt = parse_datetime_colon(date_str)
    return dt, t_offset

def parse_datetime_colon(date_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")

def parse_datetime_dash(date_str: str, logger: logging.Logger) -> datetime.datetime | None:
    if not date_str:
        return None
    return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def is_timestamp_valid(date_str: str) -> bool:
    try:
        datetime.datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
        return True
    except Exception:
        return False


# def exif_parse_datetime(s: str) -> str:
#     obj = datetime.strptime(s, "%Y:%m:%d %H:%M:%S")
#     s = obj.strftime("%Y.%m.%d-%H.%M.%S")
#     return s


# import piexif
# import pyheif
#
# # from exif import Image
# #
# # with open('grand_canyon.jpg', 'rb') as image_file:
# #     my_image = Image(image_file)
# #     my_image.has_exif
# #     my_image.list_all()
#
# exif_dict = piexif.load("foo1.jpg")
# for ifd in ("0th", "Exif", "GPS", "1st"):
#     for tag in exif_dict[ifd]:
#         print(piexif.TAGS[ifd][tag]["name"], exif_dict[ifd][tag])
#
#
#
# # Using a file path:
# heif_file = pyheif.read("IMG_7424.HEIC")
# # Or using bytes directly:
# heif_file = pyheif.read(open("IMG_7424.HEIC", "rb").read())
