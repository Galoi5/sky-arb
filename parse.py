#this script parses the input-data json files for the parsed-data folder



# !!!!!!!!!!!!!!!!!!!!!

# HAS NOT PARSED BOOKS

#!!!!!!!!!!!
import ujson


def parse_data1():
    data = ujson.load(open("input-data/items.json"))
    items = []
    for item in data["items"]:
        item_id = item["id"]
        item_name = item["name"]
        if "npc_sell_price" in item:
            item_npc_sell_price = item["npc_sell_price"]
        else: 
            item_npc_sell_price = 0
        
        item_json = {
            "id": item_id,
            "name": item_name,
            "npc_sell_price": item_npc_sell_price
        }
        items.append(item_json)
    ujson.dump(items, open("parsed-data/items.json", "w"))

#parse_data1()

def parse_data2():
    items_data = ujson.load(open("input-data/items.json"))
    recipes_data = ujson.load(open("input-data/InternalNameMappings.json"))
    items = []
    for item in items_data["items"]:
        item_id = item["id"]
        item_name = item["name"]
        if "npc_sell_price" in item:
            item_npc_sell_price = item["npc_sell_price"]
        else: 
            item_npc_sell_price = 0
            
        #recipes and forge time are gotten from recipes_data
        item_recipe = {}
        item_forge_time = 0
        for recipe_id in recipes_data:
            if recipe_id == item_id:
                if "recipe" in recipes_data[recipe_id]:
                    item_recipe = recipes_data[recipe_id]["recipe"]
                else:
                    item_recipe = []
                if "forge" in recipes_data[recipe_id]:
                    item_forge_time = recipes_data[recipe_id]["forge"]
                else:
                    item_forge_time = 0
        
        item_json = {
            "id": item_id,
            "name": item_name,
            "npc_sell_price": item_npc_sell_price,
            "recipe": item_recipe,
            "forge_time": item_forge_time
        }
        items.append(item_json)
    ujson.dump(items, open("parsed-data/items2.json", "w"))
    
#parse_data2()

def parse_data3():
    items_data = ujson.load(open("parsed-data/items2.json"))
    for item in items_data:
        if isinstance(item["recipe"], dict) and item["recipe"]:
            # Transform grid-based recipe to simplified format
            simplified_recipe = {}
            
            for slot, item_slot in item["recipe"].items():
                # Skip empty slots and handle different data types
                if item_slot and item_slot != "" and isinstance(item_slot, str):
                    # Parse item_id:quantity format
                    if ":" in item_slot:
                        item_id, quantity_str = item_slot.split(":", 1)
                        try:
                            quantity = int(quantity_str)
                            
                            # Aggregate quantities for the same item
                            if item_id in simplified_recipe:
                                simplified_recipe[item_id] += quantity
                            else:
                                simplified_recipe[item_id] = quantity
                        except ValueError:
                            # Handle case where quantity is not a valid integer
                            print(f"Warning: Invalid quantity '{quantity_str}' for item '{item_id}' in recipe for '{item['id']}'")
                            continue
                    else:
                        # Handle case where quantity is not specified (default to 1)
                        item_id = item_slot
                        if item_id in simplified_recipe:
                            simplified_recipe[item_id] += 1
                        else:
                            simplified_recipe[item_id] = 1
            
            # Replace the original recipe with simplified version
            item["recipe"] = simplified_recipe
    
    # Save the transformed data
    ujson.dump(items_data, open("parsed-data/items3.json", "w"))
    
#parse_data3()

def parse_bazaar1():
    items_data = ujson.load(open("parsed-data/items3.json"))
    bazaar_data = ujson.load(open("input-data/bazaar.json"))["products"]
    items = []
    bazaar_keys = bazaar_data.keys()
    for item in items_data:
        if item["id"] in bazaar_keys:
            items.append(item)
    ujson.dump(items, open("parsed-data/items4.json", "w"))
                
#parse_bazaar1()

def parse_recursive_recipe():
    items_data = ujson.load(open("parsed-data/items4.json"))
    
    # Create a lookup dictionary for faster item finding
    items_lookup = {item["id"]: item for item in items_data}
    
    def calculate_raw_recipe(item_id, visited=None):
        """Recursively calculate raw materials needed for an item"""
        if visited is None:
            visited = set()
        
        # Prevent infinite recursion
        if item_id in visited:
            return {}
        
        visited.add(item_id)
        
        # Get the item
        item = items_lookup.get(item_id)
        if not item or not item.get("recipe"):
            # Base case: no recipe, return empty dict
            return {}
        
        raw_recipe = {}
        
        # Process each ingredient in the recipe
        for ingredient_id, quantity in item["recipe"].items():
            ingredient_item = items_lookup.get(ingredient_id)
            
            if ingredient_item and ingredient_item.get("recipe"):
                # This ingredient has a recipe, recursively calculate its raw materials
                ingredient_raw = calculate_raw_recipe(ingredient_id, visited.copy())
                
                # Multiply the raw materials by the quantity needed
                for raw_id, raw_quantity in ingredient_raw.items():
                    if raw_id in raw_recipe:
                        raw_recipe[raw_id] += raw_quantity * quantity
                    else:
                        raw_recipe[raw_id] = raw_quantity * quantity
            else:
                # This ingredient has no recipe, it's a raw material
                if ingredient_id in raw_recipe:
                    raw_recipe[ingredient_id] += quantity
                else:
                    raw_recipe[ingredient_id] = quantity
        
        return raw_recipe
    
    # Calculate raw recipes for all items and reorder fields
    for item in items_data:
        raw_recipe = calculate_raw_recipe(item["id"])
        
        # Create new item with reordered fields
        new_item = {
            "id": item["id"],
            "name": item["name"],
            "npc_sell_price": item["npc_sell_price"],
            "forge_time": item["forge_time"],
            "recipe": item["recipe"],
            "raw_recipe": raw_recipe
        }
        
        # Replace the original item
        item.clear()
        item.update(new_item)
    
    ujson.dump(items_data, open("parsed-data/items5.json", "w"))

#parse_recursive_recipe()

def parse_recursive_recipe_2():
    #creates a list of all infinitely recursive recipes
    items_data = ujson.load(open("parsed-data/items5.json"))
    
    # Create a lookup dictionary for faster item finding
    items_lookup = {item["id"]: item for item in items_data}
    
    def find_circular_dependencies():
        """Find all circular recipe dependencies"""
        circular_items = []
        
        for item in items_data:
            if not item.get("recipe"):
                continue
                
            # Check if this item's recipe creates a circular dependency
            visited = set()
            path = []
            
            def has_circular_dependency(item_id, target_id, depth=0):
                """Check if there's a circular dependency from item_id to target_id"""
                if depth > 10:  # Prevent infinite recursion in case of bugs
                    return False
                    
                if item_id == target_id and depth > 0:
                    return True
                    
                if item_id in visited:
                    return False
                    
                visited.add(item_id)
                path.append(item_id)
                
                item_recipe = items_lookup.get(item_id, {}).get("recipe", {})
                
                # Handle both dict and list recipe formats
                if isinstance(item_recipe, dict):
                    ingredient_ids = item_recipe.keys()
                elif isinstance(item_recipe, list):
                    ingredient_ids = item_recipe
                else:
                    ingredient_ids = []
                
                for ingredient_id in ingredient_ids:
                    if has_circular_dependency(ingredient_id, target_id, depth + 1):
                        return True
                        
                path.pop()
                visited.remove(item_id)
                return False
            
            # Check if this item creates a circular dependency with any of its ingredients
            recipe = item["recipe"]
            if isinstance(recipe, dict):
                ingredient_ids = recipe.keys()
            elif isinstance(recipe, list):
                ingredient_ids = recipe
            else:
                ingredient_ids = []
                
            for ingredient_id in ingredient_ids:
                if has_circular_dependency(ingredient_id, item["id"]):
                    # Found a circular dependency
                    circular_info = {
                        "item_id": item["id"],
                        "item_name": item["name"],
                        "circular_with": ingredient_id,
                        "circular_with_name": items_lookup.get(ingredient_id, {}).get("name", "Unknown"),
                        "recipe": item["recipe"],
                        "circular_recipe": items_lookup.get(ingredient_id, {}).get("recipe", {})
                    }
                    circular_items.append(circular_info)
                    break  # Only need to find one circular dependency per item
        
        return circular_items
    
    # Find all circular dependencies
    circular_dependencies = find_circular_dependencies()
    
    # Save to JSON file
    ujson.dump(circular_dependencies, open("parsed-data/circular_dependencies.json", "w"), indent=2)
    
    print(f"Found {len(circular_dependencies)} items with circular recipe dependencies:")
    for item in circular_dependencies:
        print(f"- {item['item_name']} ({item['item_id']}) ↔ {item['circular_with_name']} ({item['circular_with']})")
    
    return circular_dependencies

#parse_recursive_recipe_2()