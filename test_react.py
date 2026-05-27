from dataloader import load_products
from dataloader import load_orders
from dataloader import load_policy

from react_agent import ReActAgent


products=load_products()
orders=load_orders()
policy=load_policy()

agent=ReActAgent(
    products,
    orders,
    policy
)


while True:

    q=input("用户：")

    if q=="exit":
        break

    print(
        agent.run(q)
    )