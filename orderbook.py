from typing import List

class Order():
	def __init__(self, unit_price: float, amount: int, orders: int):
		self.amount: int = amount
		self.unit_price: float = unit_price
		self.orders: int = orders

class OrderBook():
	def __init__(self, item_id: str):
		self.item_id: str = item_id
		self.buy_orders: List[Order] = []
		self.sell_orders: List[Order] = []
		# self.sell_volume: int = 0
		# self.buy_volume: int = 0

	def get_unit_instant_buy_price(self) -> float:
		if self.buy_orders:
			return self.buy_orders[0].unit_price
		return -1

	def get_unit_instant_sell_price(self) -> float:
		if self.sell_orders:
			return self.sell_orders[0].unit_price
		return -1