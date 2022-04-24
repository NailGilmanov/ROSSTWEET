# файл отвечает за подключение к базе данных и создание сессии
# содержит одинаковый код для всех проектов
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

# абстрактная декларативная база, в которую позднее будем наследовать все наши модели
SqlAlchemyBase = dec.declarative_base()

# для получения сессий подключения к нашей базе данных
__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    # engine - движок для работы с БД
    # если echo=True, то в консоль будут выводится все запросы

    __factory = orm.sessionmaker(bind=engine)

    # импорт всех моделей
    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)
    # создание всех несозданных объектов


# получение сессии подключения к БД
def create_session() -> Session:
    global __factory
    return __factory()
