from typing import List, Tuple
from enum import IntEnum

class ProfitType(IntEnum):
	UNPROFITABLE = 0
	RECIPE = 1
	RAW_RECIPE = 2
	NPC_SELL = 3


class Item():
    #Hypixel Skyblock Item
	def __init__(self, id: str, name: str, is_auction: bool, is_bazaar: bool, npc_sell_price: int, forge_time: int = 0, recipe: List[Tuple[str, int]] = []):
		self.id: str = id
		self.name: str = name
		self.is_auction: bool = is_auction
		self.is_bazaar: bool = is_bazaar
		self.npc_sell_price: int = npc_sell_price
		self.forge_time: int = forge_time #minutes
		self.recipe: List[Tuple[str, int]] = recipe
		self.raw_recipe: List[Tuple[str, int]] = []
		self.profit_type: ProfitType

	def calculate_profit(self) -> float:
		raw_recipe_cost = self.get_raw_recipe_cost()
		recipe_cost = self.get_recipe_cost()
		item_price = self.get_item_price()
		profit_rec = item_price - recipe_cost
		profit_raw = item_price - raw_recipe_cost
		profit_npc = item_price - self.npc_sell_price

		profit = max(profit_rec, profit_raw, profit_npc)
		if profit < 0:
			self.profit_type = ProfitType.UNPROFITABLE
		else:
			if profit == profit_rec:
				self.profit_type = ProfitType.RECIPE
			elif profit == profit_raw:
				self.profit_type = ProfitType.RAW_RECIPE
			else:
				self.profit_type = ProfitType.NPC_SELL
		return profit

	def get_raw_recipe(self):
		if self.recipe:
			for item, amount in self.recipe:
				item.get_raw_recipe()
				self.raw_recipe.append((item, amount))
		return self.raw_recipe

	def get_item_price(self) -> float:
		pass

	def get_recipe_cost(self) -> float:
		cost = 0
		for item, amount in self.recipe:
			cost += item.get_item_price() * amount
		return cost

	def get_raw_recipe_cost(self, item: Item) -> float:
		cost = 0
		for item, amount in self.raw_recipe:
			cost += item.get_item_price() * amount
		return cost