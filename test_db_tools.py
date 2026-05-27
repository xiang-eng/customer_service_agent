from db_tools import find_product_in_db, find_order_in_db


print("=== 商品查询测试 ===")
print(find_product_in_db("小米智能音箱多少钱？"))
print(find_product_in_db("米家摄像头库存多少？"))
print(find_product_in_db("华为门铃还有货吗？"))

print("\n=== 订单查询测试 ===")
print(find_order_in_db("订单 O1001 到哪了？"))
print(find_order_in_db("帮我查一下 O1003 的物流"))