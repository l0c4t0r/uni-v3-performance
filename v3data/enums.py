from enum import Enum


class Chain(str, Enum):
    ARBITRUM = "arbitrum"
    CELO = "celo"
    MAINNET = "mainnet"
    OPTIMISM = "optimism"
    POLYGON = "polygon"
    BSC = "bsc"
    POLYGON_ZKEVM = "polygon_zkevm"


class PositionType(str, Enum):
    BASE = "base"
    LIMIT = "limit"


class Protocol(str, Enum):
    QUICKSWAP = "quickswap"
    UNISWAP = "uniswap"
    ZYBERSWAP = "zyberswap"
    THENA = "thena"


class QueryType(str, Enum):
    DATABASE = "database"
    SUBGRAPH = "subgraph"


class YieldType(str, Enum):
    TOTAL = "total"
    LP = "lp"
