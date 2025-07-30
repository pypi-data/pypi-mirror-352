import time
from typing import Iterable, List, Type
from urllib.parse import urlparse, parse_qs
from sqlalchemy import text, insert, create_engine, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import insert
import cxppython as cc


@as_declarative()
class Base:
    pass


class MysqlDBSingleton:
    __instance = None

    def __init__(self, mysql_config):
        if MysqlDBSingleton.__instance is not None:
            raise Exception("This class is a singleton, use DB.create()")
        else:
            MysqlDBSingleton.__instance = self
        self.engine = self._create_engine(mysql_config)
        self.session = sessionmaker(bind=self.engine)

    @staticmethod
    def create(mysql_config):
        if MysqlDBSingleton.__instance is None:
            MysqlDBSingleton.__instance = MysqlDBSingleton(mysql_config)

    @staticmethod
    def instance():
        return MysqlDBSingleton.__instance

    @staticmethod
    def session() -> Session:
        session = MysqlDBSingleton.__instance.session
        return session()

    @staticmethod
    def get_db_connection():
        # 返回 SQLAlchemy 引擎的连接
        return MysqlDBSingleton.__instance.engine.connect()

    @staticmethod
    def add(value) -> Exception | None:
        try:
            session = MysqlDBSingleton.session()
            session.add(value)
            session.commit()
            session.close()
        except Exception as err:
            return err

        return None

    @staticmethod
    def bulk_save(objects: Iterable[object]) -> Exception | None:
        try:
            with MysqlDBSingleton.session() as session, session.begin():
                session.bulk_save_objects(objects)
        except Exception as err:
            return err

        return None

    @staticmethod
    def test_db_connection():
        try:
            # 尝试建立连接
            with MysqlDBSingleton.instance().engine.connect() as connection:
                cc.logging.success(f"Database connection successful! : {MysqlDBSingleton.instance().engine.url}")
                connection.commit()
                return True
        except OperationalError as e:
            cc.logging.error(f"Failed to connect to the database: {e}")
            return False

    @staticmethod
    def test_connection():
        MysqlDBSingleton.test_db_connection()

    def _create_engine(self, mysql_config):
        echo = False
        config_dict={}
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

    @staticmethod
    def batch_insert_records(session: Session,
                             model: Type[Base],
                             data: List,
                             batch_size: int = 50,
                             ignore_existing: bool = True,
                             commit_per_batch: bool = True,
                             retries=3,
                             delay=1):
        total_inserted = 0
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
                            cc.logging.warning(f"Deadlock found at attempt {attempt + 1}/{retries},delay:{delay}")
                            time.sleep(delay)  # 等待一段时间后重试
                            continue
                        else:
                            raise  # 重试次数用尽，抛出异常
                # cc.logging.debug(f"Batch_insert_reals_rows: {inserted_count}")

            except Exception as e:
                cc.logging.error(f"Batch insert failed at index {i}: {e}")
                session.rollback()
                raise

            if commit_per_batch:
                session.commit()

        return total_inserted

    @staticmethod
    def batch_replace_records(session: Session, model: Type[Base], data: List, update_fields: List, conflict_key='id', batch_size: int = 50,
                              commit_per_batch: bool = True,retries_count=3,lock_table: bool = False):
        """
        :param model: SQLAlchemy Table 对象
        :param data: 批量插入的数据（字典列表）
        :param update_fields: 需要更新的字段列表（例如 ['name', 'email']）
        :param conflict_key: 冲突检测的键（默认 'id'）
        """
        table = model.__table__
        valid_keys = {col.name for col in table.primary_key} | {col.name for col in table.columns if col.unique}
        if conflict_key not in valid_keys:
            raise ValueError(f"'{conflict_key}' must be a primary key or unique column. Available: {valid_keys}")

        total_changed = 0
        # 显式加表级锁
        if lock_table:
            session.execute(text(f"LOCK TABLES {table.name} WRITE"))
        try:
            for i in range(0, len(data), batch_size):
                retries = retries_count
                while retries > 0:
                    try:
                        batch = data[i:i + batch_size]
                        stmt = insert(model).values(batch)
                        set_dict = {field: func.values(table.c[field]) for field in update_fields}
                        stmt = stmt.on_duplicate_key_update(**set_dict)
                        result = session.execute(stmt)
                        inserted_count = result.rowcount
                        total_changed += inserted_count
                        if commit_per_batch:
                            session.commit()
                        break
                    except OperationalError as e:
                        if e.orig.args[0] == 1213:  # MySQL 死锁错误码
                            retries -= 1
                            cc.logging.warning(f"Deadlock detected at index {i}, retries left: {retries}")
                            time.sleep(0.1 * (3 - retries))  # 指数退避
                            session.rollback()
                            continue
                        cc.logging.error(f"Batch replace failed at index {i}: {e}")
                        session.rollback()
                        raise
                    except Exception as e:
                        cc.logging.error(f"Batch replace failed at index {i}: {e}")
                        session.rollback()
                        raise
                else:
                    cc.logging.error(f"Batch replace failed at index {i} after {retries} retries")
                    raise RuntimeError("Max retries reached due to persistent deadlock")
        finally:
            # 释放锁
            if lock_table:
                session.execute(text("UNLOCK TABLES"))

        return total_changed
    @staticmethod
    def close():
        """
        清理资源，关闭引擎。
        """
        if MysqlDBSingleton.__instance:
            MysqlDBSingleton.__instance.engine.dispose()