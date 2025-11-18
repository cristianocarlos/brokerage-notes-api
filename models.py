from database import Base
from sqlalchemy import Column, Integer, String, Numeric, Date

class Trade(Base):
    __tablename__ = 'trade_auto'
    __table_args__ = {'schema': 'main'}
    trad_code = Column(Integer, primary_key=True)
    trad_date = Column(String)
    trad_tick = Column(String)
    trad_oper = Column(String)
    trad_qtty = Column(Numeric)
    trad_valu = Column(Numeric)
    trad_type = Column(String)
    trad_mark = Column(String)
    trad_opti_exer = Column(String)
    trad_brok = Column(String)

class BrokerageNote(Base):
    __tablename__ = 'brokerage_note_auto'
    __table_args__ = {'schema': 'main'}
    brno_date = Column(Date, primary_key=True)
    brno_valu = Column(Numeric)
    brno_taxl = Column(Numeric, server_default='0')
    brno_taxr = Column(Numeric, server_default='0')
    brno_emol = Column(Numeric, server_default='0')
    brno_trat = Column(Numeric, server_default='0')
    brno_clea = Column(Numeric, server_default='0')
    brno_iss = Column(Numeric, server_default='0')
    brno_irrf = Column(Numeric, server_default='0')
    brno_seda = Column(Date)
    brno_brok = Column(String, primary_key=True)
