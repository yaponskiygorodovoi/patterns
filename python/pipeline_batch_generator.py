orders= [
    {"order_id":1,"user_id":10,"status":"paid","amount":120},
    {"order_id":2,"user_id":11,"status":"new","amount":80},
    {"order_id":3,"user_id":12,"status":"paid","amount":250},
    {"order_id":4,"user_id":13,"status":"cancelled","amount":90},
    {"order_id":5,"user_id":14,"status":"paid","amount":300},
    {"order_id":6,"user_id":15,"status":"paid","amount":180}
]
batch_size = 3

def paid_orders(orders):
    for order in orders:
        if order["status"]=="paid":
            yield order


def big_orders(orders):
    for order in orders:
        if order["amount"] >= 150:
            yield order

def select_fields(orders):
    for order in orders:
        yield {
            "order_id":order["order_id"],
            "user_id":order["user_id"],
            "amount":order["amount"],
        }

## БАТЧ ГЕНЕРАТОР
def batch_generator(orders,batch_size):

    batch = []   # Принимаем строки
    for order in orders:
        batch.append(order)
        if len(batch) == batch_size:  # Строки достигли размера батча(устанавливается) отправляем дальше
            yield batch
            batch = [] # Формируем новую корзину для следующей партии
    if batch:   # Чтобы не потерять последний батч,если он не достиг размера батча
        yield batch

pipeline = batch_generator(select_fields(big_orders(paid_orders(orders))), batch_size)

for batch in pipeline:
    print(batch)