import traceback

from operror.op_error import OpError, new_internal_error
from operror.op_status import Code, Status
from tests.test_op_status import ErrorCase


class Connection:
    def exec_sql(self, sql: str):
        raise RuntimeError("Network error")

class DBClient:
    def __init__(self, conn: Connection):
        self._conn = conn

    def insert(self, data: str):
        try:
            self._conn.exec_sql("insert into ...")
        except RuntimeError as e:
            raise new_internal_error().with_message("DB insert failed").build(OpError) from e

class Service:
    def __init__(self, db: DBClient):
        self._db = db
        
    def save(self, data: str):
        self._db.insert(data)

class API:
    def __init__(self, service: Service):
        self._service = service
        
    def create(self, data: str):
        self._service.save(data)

def test_op_error_print_stack():
    api = API(Service(DBClient(Connection())))
    try:
        api.create("test")
    except OpError:
        # print(f"error info: {e}")
        print(traceback.format_exc())

def test_check_op_error_cause():
    try:
        api = API(Service(DBClient(Connection())))
        api.create("test")
    except OpError as e:
        assert e.__cause__ is not None
        assert isinstance(e.__cause__, RuntimeError)
        assert e.__cause__.args[0] == "Network error"
        assert e.__context__ is not None
        assert isinstance(e.__context__, RuntimeError)
        assert e.__context__.args[0] == "Network error"

def test_build_op_error():
    e = new_internal_error().with_message("internal error").build()
    assert isinstance(e, OpError)
    assert e.status.code == Code.INTERNAL_ERROR
    assert e.status.message == "internal error"  
    
    class MyOpError(OpError):
        pass

    e = new_internal_error().with_message("internal error").build(MyOpError)
    assert isinstance(e, MyOpError)
    assert e.status.code == Code.INTERNAL_ERROR
    assert e.status.message == "internal error"
    
    class MyOpError2(OpError):
        def __init__(self, status: Status, module: str, p_arg: str, kw_arg: str = ""):
            super().__init__(status=status, module=module)
            self.p_arg = p_arg
            self.kw_arg = kw_arg

    e = new_internal_error().with_message("internal error").build(MyOpError2, "p_arg", kw_arg="kw_arg")
    assert isinstance(e, MyOpError2)
    assert e.status.code == Code.INTERNAL_ERROR
    assert e.status.message == "internal error"
    assert e.p_arg == "p_arg"
    assert e.kw_arg == "kw_arg"

def test_op_error_module_property():
    e = new_internal_error().with_module("test_module").build()
    assert isinstance(e, OpError)
    assert e.module == "test_module"
    assert e.status.code == Code.INTERNAL_ERROR

    # 测试空模块名
    e = new_internal_error().with_module("").build()
    assert e.module == "none"

    # 测试空白字符模块名
    e = new_internal_error().with_module("   ").build()
    assert e.module == "none"

def test_op_error_str():
    # 测试基本错误信息
    e = new_internal_error().with_message("internal error").build()
    assert str(e) == "OpError(module=none, status=(code=INTERNAL_ERROR(13), message='internal error'))"
    
    # 测试带模块名的错误信息
    e = new_internal_error().with_module("test_module").with_message("internal error").build()
    assert str(e) == "OpError(module=test_module, status=(code=INTERNAL_ERROR(13), message='internal error'))"
    
    # 测试带 case 的错误信息
    e = new_internal_error().with_case(ErrorCase("1001", Code.INTERNAL_ERROR)).with_message("internal error").build()
    assert str(e) == "OpError(module=none, status=(code=INTERNAL_ERROR(13), case=1001, message='internal error'))"
    
    # 测试带 details 的错误信息
    e = new_internal_error().with_details({"key": "value"}).with_message("internal error").build()
    assert str(e) == "OpError(module=none, status=(code=INTERNAL_ERROR(13), message='internal error', details={'key': 'value'}))"
    
    # 测试完整错误信息
    e = new_internal_error()\
        .with_module("test_module")\
        .with_case(ErrorCase("1001", Code.INTERNAL_ERROR))\
        .with_details({"key": "value"})\
        .with_message("internal error")\
        .build()
    assert str(e) == "OpError(module=test_module, status=(code=INTERNAL_ERROR(13), case=1001, message='internal error', details={'key': 'value'}))"


