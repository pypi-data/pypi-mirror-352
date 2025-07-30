import redis
from typing import Union, Dict, Optional, List, Set, Any
from urllib.parse import urlparse, ParseResult
import cxppython as cc

class RedisUtil:
    _instance: Optional['RedisUtil'] = None  # 静态字段存储单例实例

    def __init__(self, connection_params: Union[str, Dict], default: bool = True):
        """
        初始化Redis工具类
        :param connection_params: Redis连接参数，可以是连接字符串或字典
        :param default: 是否设置为默认连接
        """
        self._connections: Dict[str, redis.Redis] = {}
        self._default_connection: Optional[redis.Redis] = None
        self._connection_params: Dict[str, Union[str, Dict]] = {}  # 保存原始连接参数

        # 处理连接参数
        if isinstance(connection_params, str):
            # 解析连接字符串，如 "redis://localhost:6379/0"
            self._add_connection("default", connection_params)
        elif isinstance(connection_params, dict):
            # 字典参数，如 {"host": "localhost", "port": 6379, "db": 0}
            self._add_connection("default", connection_params)
        else:
            raise ValueError("connection_params must be str or dict")

        if default:
            self._default_connection = self._connections["default"]

    @staticmethod
    def create(connection_params: Union[str, Dict], default: bool = True) -> 'RedisUtil':
        """
        静态方法创建RedisUtil实例并赋值给静态字段
        :param connection_params: Redis连接参数
        :param default: 是否设置为默认连接
        :return: RedisUtil实例
        """
        RedisUtil._instance = RedisUtil(connection_params, default)
        return RedisUtil._instance

    @staticmethod
    def get_instance() -> Optional['RedisUtil']:
        """
        获取静态字段中的实例
        :return: RedisUtil实例或None
        """
        if RedisUtil._instance is None:
            raise ValueError("No instance created. Call create first.")
        return RedisUtil._instance

    @staticmethod
    def test_connection(name: Optional[str] = None) -> bool:
        """
        静态方法测试Redis连接是否成功，并在成功时打印连接字符串（账号密码使用***掩码）
        :param name: 连接名称，若为None则测试_instance的默认连接
        :return: 连接是否成功
        """
        try:
            instance = RedisUtil.get_instance()
            connection = instance.get_connection(name)
            # 获取连接参数
            conn_name = name if name else "default"
            params = instance._connection_params.get(conn_name)
            if not params:
                raise ValueError(f"No parameters found for connection {conn_name}")

            # 构造连接字符串
            if isinstance(params, str):
                # 解析URL并掩码账号密码
                parsed = urlparse(params)
                if parsed.username or parsed.password:
                    connection_string = f"{parsed.scheme}://***:***@{parsed.hostname}:{parsed.port}{parsed.path}"
                else:
                    connection_string = params
            else:
                # 从字典构造连接字符串
                host = params.get("host", "localhost")
                port = params.get("port", 6379)
                db = params.get("db", 0)
                username = params.get("username") or params.get("auth")
                password = params.get("password") or (params.get("auth") if params.get("auth") else None)
                if username or password:
                    connection_string = f"redis://***:***@{host}:{port}/{db}"
                else:
                    connection_string = f"redis://{host}:{port}/{db}"

            # 测试连接
            result = connection.ping()
            if result:
                cc.logging.success(f"Redis connection successful! : {connection_string}")
            return result
        except (redis.RedisError, ValueError):
            return False

    def _add_connection(self, name: str, params: Union[str, Dict]) -> None:
        """
        添加Redis连接，并保存原始参数
        :param name: 连接名称
        :param params: 连接参数
        """
        try:
            if isinstance(params, str):
                connection = redis.Redis.from_url(params)
            else:
                # 仅传递redis.Redis支持的参数
                valid_params = {}
                for key in ["host", "port", "db", "username", "password"]:
                    if key in params:
                        valid_params[key] = params[key]
                    elif key == "password" and "auth" in params:
                        valid_params[key] = params["auth"]  # 支持auth作为password
                connection = redis.Redis(**valid_params)
            self._connections[name] = connection
            self._connection_params[name] = params  # 保存原始参数
        except redis.RedisError as e:
            raise ConnectionError(f"Failed to connect to Redis: {str(e)}")

    def add_connection(self, name: str, params: Union[str, Dict], set_default: bool = False) -> None:
        """
        添加新的Redis连接
        :param name: 连接名称
        :param params: 连接参数
        :param set_default: 是否设置为默认连接
        """
        self._add_connection(name, params)
        if set_default:
            self._default_connection = self._connections[name]

    @staticmethod
    def add_connection_static(name: str, params: Union[str, Dict], set_default: bool = False) -> None:
        """
        静态方法添加新的Redis连接
        :param name: 连接名称
        :param params: 连接参数
        :param set_default: 是否设置为默认连接
        """
        RedisUtil.get_instance().add_connection(name, params, set_default)

    def get_connection(self, name: Optional[str] = None) -> redis.Redis:
        """
        获取Redis连接
        :param name: 连接名称，若为None则返回默认连接
        :return: Redis连接对象
        """
        if name is None:
            if self._default_connection is None:
                raise ValueError("No default connection set")
            return self._default_connection
        if name not in self._connections:
            raise ValueError(f"No connection named {name}")
        return self._connections[name]

    def execute(self, command: str, *args: Any, name: Optional[str] = None) -> Any:
        """
        执行Redis原始命令
        :param command: Redis命令（如 "SET", "GET", "HINCRBY" 等）
        :param args: 命令参数
        :param name: 连接名称，若为None则使用默认连接
        :return: 命令执行结果
        """
        try:
            # 转换参数，确保没有NoneType
            converted_args = []
            for arg in args:
                if arg is None:
                    raise ValueError("NoneType arguments are not allowed in Redis commands")
                # 转换为字符串类型（Redis支持bytes/str/int/float）
                if not isinstance(arg, (bytes, str, int, float)):
                    converted_args.append(str(arg))
                else:
                    converted_args.append(arg)

            connection = self.get_connection(name)
            return connection.execute_command(command, *converted_args)
        except redis.RedisError as e:
            raise redis.RedisError(f"Failed to execute command {command}: {str(e)}")
        except ValueError as e:
            raise ValueError(f"Invalid argument for command {command}: {str(e)}")

    @staticmethod
    def execute_static(command: str, *args: Any, name: Optional[str] = None) -> Any:
        """
        静态方法：执行Redis原始命令
        :param command: Redis命令
        :param args: 命令参数（过滤掉None值）
        :param name: 连接名称，若为None则使用默认连接
        :return: 命令执行结果
        """
        # 记录接收到的原始参数
        # 过滤掉args中的None值
        filtered_args = [arg for arg in args if arg is not None]
        if len(filtered_args) < len(args):
            cc.logging.warning(f"Filtered out None values from args. Original: {args}, Filtered: {filtered_args}")
        return RedisUtil.get_instance().execute(command, *filtered_args, name=name)
    # 字符串操作
    def set(self, key: str, value: str, ex: Optional[int] = None, name: Optional[str] = None) -> bool:
        """
        设置键值对
        :param key: 键
        :param value: 值
        :param ex: 过期时间(秒)
        :param name: 连接名称
        :return: 是否成功
        """
        return self.get_connection(name).set(key, value, ex=ex)

    @staticmethod
    def set_static(key: str, value: str, ex: Optional[int] = None, name: Optional[str] = None) -> bool:
        """静态方法：设置键值对"""
        return RedisUtil.get_instance().set(key, value, ex, name)

    def get(self, key: str, name: Optional[str] = None) -> Optional[str]:
        """
        获取键值
        :param key: 键
        :param name: 连接名称
        :return: 值或None
        """
        value = self.get_connection(name).get(key)
        return value.decode() if value else None

    @staticmethod
    def get_static(key: str, name: Optional[str] = None) -> Optional[str]:
        """静态方法：获取键值"""
        return RedisUtil.get_instance().get(key, name)

    def delete(self, key: str, name: Optional[str] = None) -> int:
        """
        删除键
        :param key: 键
        :param name: 连接名称
        :return: 删除的键数量
        """
        return self.get_connection(name).delete(key)

    @staticmethod
    def delete_static(key: str, name: Optional[str] = None) -> int:
        """静态方法：删除键"""
        return RedisUtil.get_instance().delete(key)

    # 哈希操作
    def hset(self, hash_name: str, key: str, value: str, name: Optional[str] = None) -> int:
        """
        设置哈希字段值
        :param hash_name: 哈希名称
        :param key: 字段
        :param value: 值
        :param name: 连接名称
        :return: 新增字段数量
        """
        return self.get_connection(name).hset(hash_name, key, value)

    @staticmethod
    def hset_static(hash_name: str, key: str, value: str, name: Optional[str] = None) -> int:
        """静态方法：设置哈希字段值"""
        return RedisUtil.get_instance().hset(hash_name, key, value, name)

    def hget(self, hash_name: str, key: str, name: Optional[str] = None) -> Optional[str]:
        """
        获取哈希字段值
        :param hash_name: 哈希名称
        :param key: 字段
        :param name: 连接名称
        :return: 值或None
        """
        value = self.get_connection(name).hget(hash_name, key)
        return value.decode() if value else None

    @staticmethod
    def hget_static(hash_name: str, key: str, name: Optional[str] = None) -> Optional[str]:
        """静态方法：获取哈希字段值"""
        return RedisUtil.get_instance().hget(hash_name, key, name)

    def hkeys(self, hash_name: str, name: Optional[str] = None) -> Set[str]:
        """
        获取哈希的所有字段名
        :param hash_name: 哈希名称
        :param name: 连接名称
        :return: 字段名集合
        """
        keys = self.get_connection(name).hkeys(hash_name)
        return {k.decode() for k in keys}

    @staticmethod
    def hkeys_static(hash_name: str, name: Optional[str] = None) -> Set[str]:
        """静态方法：获取哈希的所有字段名"""
        return RedisUtil.get_instance().hkeys(hash_name, name)

    # 列表操作
    def lpush(self, list_name: str, value: str, name: Optional[str] = None) -> int:
        """
        从列表左侧插入值
        :param list_name: 列表名称
        :param value: 值
        :param name: 连接名称
        :return: 列表长度
        """
        return self.get_connection(name).lpush(list_name, value)

    @staticmethod
    def lpush_static(list_name: str, value: str, name: Optional[str] = None) -> int:
        """静态方法：从列表左侧插入值"""
        return RedisUtil.get_instance().lpush(list_name, value, name)

    def rpop(self, list_name: str, name: Optional[str] = None) -> Optional[str]:
        """
        从列表右侧弹出值
        :param list_name: 列表名称
        :param name: 连接名称
        :return: 弹出的值或None
        """
        value = self.get_connection(name).rpop(list_name)
        return value.decode() if value else None

    @staticmethod
    def rpop_static(list_name: str, name: Optional[str] = None) -> Optional[str]:
        """静态方法：从列表右侧弹出值"""
        return RedisUtil.get_instance().rpop(list_name, name)

    # 集合操作
    def sadd(self, set_name: str, value: str, name: Optional[str] = None) -> int:
        """
        向集合添加元素
        :param set_name: 集合名称
        :param value: 值
        :param name: 连接名称
        :return: 新增元素数量
        """
        return self.get_connection(name).sadd(set_name, value)

    @staticmethod
    def sadd_static(set_name: str, value: str, name: Optional[str] = None) -> int:
        """静态方法：向集合添加元素"""
        return RedisUtil.get_instance().sadd(set_name, value, name)

    def smembers(self, set_name: str, name: Optional[str] = None) -> Set[str]:
        """
        获取集合所有元素
        :param set_name: 集合名称
        :param name: 连接名称
        :return: 元素集合
        """
        members = self.get_connection(name).smembers(set_name)
        return {m.decode() for m in members}

    @staticmethod
    def smembers_static(set_name: str, name: Optional[str] = None) -> Set[str]:
        """静态方法：获取集合所有元素"""
        return RedisUtil.get_instance().smembers(set_name, name)

    def close(self) -> None:
        """
        关闭所有连接
        """
        for conn in self._connections.values():
            try:
                conn.close()
            except redis.RedisError:
                pass
        self._connections.clear()
        self._default_connection = None
        self._connection_params.clear()

    @staticmethod
    def close_static() -> None:
        """静态方法：关闭所有连接"""
        RedisUtil.get_instance().close()