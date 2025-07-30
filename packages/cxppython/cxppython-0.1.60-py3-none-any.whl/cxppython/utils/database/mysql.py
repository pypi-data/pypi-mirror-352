from urllib.parse import urlparse, parse_qs

from sqlalchemy import create_engine, insert, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from typing import List, Iterable, Type, Optional
import time
import cxppython as cc # 假设 cc.logging 是你的日志模块
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MysqlDB:
    def __init__(self, mysql_config):
        """
        初始化 MysqlDB 实例，基于提供的 mysql_config 创建数据库引擎和会话工厂。
        :param mysql_config: 数据库配置字典，包含 user, password, host, port, database 等字段
        """
        self.engine = self._create_engine(mysql_config)
        self.session_factory = sessionmaker(bind=self.engine)

    def _create_engine(self, mysql_config):
        """
        创建 SQLAlchemy 引擎。
        """
        echo = False
        config_dict = {}
        if isinstance(mysql_config, str):
            # 解析连接字符串格式，例如：k8stake_tao:cYn7W4DuJMZqQT0o2yLFJqkZQ@172.27.22.133:3306/k8stake_tao
            parsed = urlparse(f"mysql://{mysql_config}")
            config_dict = {
                "user": parsed.username,
                "password": parsed.password,
                "host": parsed.hostname,
                "port": parsed.port or 3306,  # 默认端口为3306
                "database": parsed.path.lstrip("/")  # 去除路径前的斜杠
            }
            # 检查是否有查询参数 echo
            query_params = parse_qs(parsed.query)
            if "echo" in query_params:
                echo = query_params["echo"][0].lower() == "true"
        else:
            config_dict = mysql_config
            if "echo" in mysql_config:
                echo = mysql_config["echo"]

        return create_engine(
            'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(**config_dict),
            pool_size=200,
            max_overflow=0,
            echo=echo)

    def get_session(self) -> Session:
        """
        获取一个新的 SQLAlchemy 会话。
        """
        return self.session_factory()

    def get_db_connection(self):
        """
        返回 SQLAlchemy 引擎的连接。
        """
        return self.engine.connect()

    def add(self, value) -> Optional[Exception]:
        """
        添加单个对象到数据库。
        """
        try:
            with self.get_session() as session, session.begin():
                session.add(value)
        except Exception as err:
            return err
        return None

    def bulk_save(self, objects: Iterable[object]) -> Optional[Exception]:
        """
        批量保存对象到数据库。
        """
        try:
            with self.get_session() as session, session.begin():
                session.bulk_save_objects(objects)
        except Exception as err:
            return err
        return None

    def test_db_connection(self) -> bool:
        """
        测试数据库连接。
        """
        try:
            with self.engine.connect() as connection:
                cc.logging.success(f"Database connection successful! : {self.engine.engine.url}")
                return True
        except OperationalError as e:
            cc.logging.error(f"Failed to connect to the database: {e}")
            return False

    def batch_insert_records(
        self,
        model: Type[Base],
        data: List,
        batch_size: int = 50,
        ignore_existing: bool = True,
        commit_per_batch: bool = True,
        retries: int = 3,
        delay: float = 1
    ) -> int:
        """
        批量插入记录，支持忽略已存在记录和死锁重试。
        """
        total_inserted = 0
        with self.get_session() as session:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                stmt = insert(model).values(batch)
                if ignore_existing:
                    stmt = stmt.prefix_with("IGNORE")
                try:
                    for attempt in range(retries):
                        try:
                            result = session.execute(stmt)
                            inserted_count = result.rowcount
                            total_inserted += inserted_count
                            break
                        except OperationalError as e:
                            if "Deadlock found" in str(e) and attempt < retries - 1:
                                cc.logging.warning(f"Deadlock found at attempt {attempt + 1}/{retries}, delay: {delay}")
                                time.sleep(delay)
                                continue
                            raise
                except Exception as e:
                    cc.logging.error(f"Batch insert failed at index {i}: {e}")
                    session.rollback()
                    raise

                if commit_per_batch:
                    session.commit()

        return total_inserted

    def batch_replace_records(
        self,
        model: Type[Base],
        data: List,
        update_fields: List,
        conflict_key: str = 'id',
        batch_size: int = 50,
        commit_per_batch: bool = True
    ):
        """
        批量替换记录（插入或更新）。
        """
        table = model.__table__
        valid_keys = {col.name for col in table.primary_key} | {col.name for col in table.columns if col.unique}
        if conflict_key not in valid_keys:
            raise ValueError(f"'{conflict_key}' must be a primary key or unique column. Available: {valid_keys}")

        with self.get_session() as session:
            for i in range(0, len(data), batch_size):
                try:
                    batch = data[i:i + batch_size]
                    stmt = insert(model).values(batch)
                    set_dict = {field: func.values(table.c[field]) for field in update_fields}
                    stmt = stmt.on_duplicate_key_update(**set_dict)
                    session.execute(stmt)
                except Exception as e:
                    cc.logging.error(f"Batch replace failed at index {i}: {e}")
                    session.rollback()
                    raise

                if commit_per_batch:
                    session.commit()

    def close(self):
        """
        清理资源，关闭引擎。
        """
        self.engine.dispose()