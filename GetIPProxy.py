from sqlalchemy import create_engine, Column, Integer, VARCHAR, DateTime, Numeric
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime

BaseModel = declarative_base()
DEFAULT_SCORE = 10
class Proxy(BaseModel):
    __tablename__ = 'proxys'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(VARCHAR(16), nullable=False)
    port = Column(Integer, nullable=False)
    types = Column(Integer, nullable=False)
    protocol = Column(Integer, nullable=False, default=0)
    country = Column(VARCHAR(100), nullable=False)
    area = Column(VARCHAR(100), nullable=False)
    updatetime = Column(DateTime(), default=datetime.datetime.utcnow)
    speed = Column(Numeric(5, 2), nullable=False)
    score = Column(Integer, nullable=False, default=DEFAULT_SCORE)


def get_proxy_ip():
    try:
        connect_args = {'check_same_thread': False}
        engine = create_engine('sqlite:///C:/Users/李闻卓/Desktop/爬虫/IPProxyPool-master/data/proxy.db', echo=False,connect_args=connect_args)
        DB_Session = sessionmaker(bind=engine)  # sessionmaker() 会生成一个数据库会话类。这个类的实例可以当成一个数据库连接，它同时还记录了一些查询的数据，并决定什么时候执行 SQL 语句
        session = DB_Session()  # 创建session对象
    except Exception as e:
        print("connecting failed...")
        return 0
    query = session.query(Proxy.ip, Proxy.port, Proxy.protocol, Proxy.score)  # 创建Query查询
    session.close()
    return query.order_by(Proxy.score.desc(), Proxy.speed).all()




