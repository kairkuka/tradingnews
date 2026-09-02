from sqlalchemy import BigInteger, Integer, Numeric

BigIntPrimaryKey = BigInteger().with_variant(Integer, "sqlite")
MarketNumeric = Numeric(20, 8)

