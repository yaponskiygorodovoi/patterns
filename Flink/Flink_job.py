from pyflink.common import Types
from pyflink.datastream import StreamExecutionEnvironment

# Аналог создания среды выполнения в Spark
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(2)

# Для примера источник — небольшой набор данных
events = env.from_collection(
    collection=[
        ("drone_1", 10),
        ("drone_2", 20),
        ("drone_1", 15),
    ],
    type_info=Types.TUPLE([
        Types.STRING(),
        Types.INT(),
    ]),
)

totals = (
    events
    .filter(lambda event: event[1] > 0)
    .key_by(lambda event: event[0], key_type=Types.STRING())
    .sum(1)
)

totals.print()

# Запуск графа обработки
env.execute("Drone totals")