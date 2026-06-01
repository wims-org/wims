import enum
import uuid

from pydantic import BaseModel, Field

MESSAGE_STREAM_DELAY: float = 0.3  # second
MESSAGE_STREAM_RETRY_TIMEOUT: int = 15000  # millisecond


class Qualifier(enum.Enum):
    IN = "in"
    NOT_IN = "not_in"
    EQUALS = "eq"
    NOT_EQUALS = "not_eq"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"


class FilterReq(BaseModel):
    field: str
    qualifier: Qualifier = Qualifier.EQUALS
    value: str | int | list[str | int]


class Filter(FilterReq):
    # since pydantic does not allow for nullable defaults, this wrapper is used
    qualifier: Qualifier | None = Field(default=None, description="If null, defaults to 'eq'.")


class QueryReq(BaseModel):
    term: str | None = None
    filters: list[Filter] = []
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1)
    sort_by: str | None = None
    sort_desc: bool = False


class Query(QueryReq):
    # since pydantic does not allow for nullable defaults, this wrapper is used
    filters: list[Filter] | None = Field(default=None, description="If null, defaults to empty list.")
    offset: int | None = Field(default=None, ge=0, description="If null, defaults to 0.")
    limit: int | None = Field(default=None, ge=1, description="If null, defaults to 10.")
    sort_desc: bool | None = Field(default=None, description="If null, defaults to False.")


class Event(enum.Enum):
    SCAN = "SCAN"
    SCAN_NEW = "SCAN_NEW"
    IDENTIFICATION = "IDENTIFICATION"
    ALIVE = "ALIVE"
    ERROR = "ERROR"
    ELEMENT_UPDATE = "ELEMENT_UPDATE"
    ALL = "ALL"


class ElementUpdate(enum.Enum):
    READERS = "READERS"
    ITEM = "ITEM"
    CONTAINER = "CONTAINER"


class CodeFormat(enum.Enum):
    # All bar code formats supported by the frontend library
    # https://www.npmjs.com/package/vue-qrcode-reader
    # https://en.wikipedia.org/wiki/Barcode#Types_of_barcodes
    DATA_MATRIX = "data_matrix"  # https://en.wikipedia.org/wiki/Data_Matrix
    AZTEC = "aztec"  # https://en.wikipedia.org/wiki/Aztec_Code
    CODE_128 = "code_128"  # https://en.wikipedia.org/wiki/Code_128
    CODE_39 = "code_39"  # https://en.wikipedia.org/wiki/Code_39
    CODE_93 = "code_93"  # https://en.wikipedia.org/wiki/Code_93
    CODABAR = "codabar"  # https://en.wikipedia.org/wiki/Codabar
    DATABAR = "databar"  # https://en.wikipedia.org/wiki/GS1_DataBar
    # https://en.wikipedia.org/wiki/GS1_DataBar -> Expanded
    DATABAR_EXPANDED = "databar_expanded"
    # https://en.wikipedia.org/wiki/Barcode#Film_edge_barcode
    DX_FILM_EDGE = "dx_film_edge"
    # https://en.wikipedia.org/wiki/International_Article_Number_(EAN)
    EAN_13 = "ean_13"
    EAN_8 = "ean_8"  # https://en.wikipedia.org/wiki/EAN-8
    ITF = "itf"  # https://en.wikipedia.org/wiki/Interleaved_2_of_5
    MAXI_CODE = "maxi_code"  # https://en.wikipedia.org/wiki/MaxiCode
    MICRO_QR_CODE = "micro_qr_code"  # https://en.wikipedia.org/wiki/QR_code#micro
    PDF417 = "pdf417"  # https://en.wikipedia.org/wiki/PDF417
    QR_CODE = "qr_code"  # https://en.wikipedia.org/wiki/QR_code
    RM_QR_CODE = "rm_qr_code"  # https://en.wikipedia.org/wiki/RMQR_Code
    UPC_A = "upc_a"  # https://en.wikipedia.org/wiki/Universal_Product_Code#UPC-A
    UPC_E = "upc_e"  # https://en.wikipedia.org/wiki/Universal_Product_Code#UPC-E
    LINEAR_CODES = "linear_codes"  # https://en.wikipedia.org/wiki/Linear_barcode
    MATRIX_CODES = "matrix_codes"  # https://en.wikipedia.org/wiki/Matrix_barcode
    UNKNOWN = "unknown"
    # All other formats:
    UUID = "uuid"  # for nfc tags


class SseEventData(BaseModel):
    reader_id: str | None = None
    id: str | int | None = None
    code_value: str | None = None
    code_format: CodeFormat | None = None
    data: dict | None = None
    stream_id: str | None = None


class ElementUpdateData(BaseModel):
    element: ElementUpdate
    id: int | None = None
    code: str | None = None


class SseEvent(BaseModel):
    event: Event
    data: SseEventData | ElementUpdateData
    id: str = str(uuid.uuid4())
    retry: int = MESSAGE_STREAM_RETRY_TIMEOUT


class WebhookEvent(enum.Enum):
    ITEM_UPDATE = "ITEM_UPDATE"
    ITEM_CREATE = "ITEM_CREATE"
    ITEM_DELETE = "ITEM_DELETE"
    CATEGORY_UPDATE = "CATEGORY_UPDATE"
    CATEGORY_CREATE = "CATEGORY_CREATE"
    CATEGORY_DELETE = "CATEGORY_DELETE"
    USER_UPDATE = "USER_UPDATE"
    USER_CREATE = "USER_CREATE"
    USER_DELETE = "USER_DELETE"
    READER_UPDATE = "READER_UPDATE"
    READER_CREATE = "READER_CREATE"
    READER_DELETE = "READER_DELETE"
    FILE_UPDATE = "FILE_UPDATE"
    FILE_CREATE = "FILE_CREATE"
    FILE_DELETE = "FILE_DELETE"
    CONTAINER_ADD = "CONTAINER_ADD"
    CONTAINER_REMOVE = "CONTAINER_REMOVE"
    CODE_SCAN = "CODE_SCAN"
    CODE_SCAN_NEW = "CODE_SCAN_NEW"
