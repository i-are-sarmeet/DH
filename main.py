import cmd
import json
import sys
from typing import List
from typing import Union

from tabulate import tabulate


def load_files():
  """
  Read provided json files
  :return:
  """
  with open('json/ingredients.json') as f:
    _ingredients = json.load(f)
    allergen = []
    ingredients = {}
    for i in _ingredients["ingredients"]:
      ingredients[i["name"]] = i["id"]
      if i["is_allergen"]:
        allergen.append(i["id"])

  with open('json/products.json') as f:
    products = {}
    collection = {}
    _products = json.load(f)
    for p in _products["products"]:
      products[p["id"]] = {"name": p["name"], "ingredients": set(p["ingredient_ids"])}
      collection[p["collection"]] = p["id"]

  return ingredients, products, allergen, collection


# read json files
ingredients, products, allergen, collection = load_files()


def list_all_ingredients(ingredients: dict) -> List[str]:
  """
  :return: List of all available ingredients
  """
  return list(ingredients.keys())


def list_all_products(products: dict) -> List[str]:
  """
  :return: List of all available products
  """
  return [p["name"] for p in products.values()]


def search_ingredients(list_ingredients: List[str], ingredient: str) -> List[str]:
  """
  search ingredients with partial names
  TODO: Maybe use fuzzywuzzy for approximation and spelling mistakes
  :param list_ingredients: List of ingredients to filter
  :param ingredient: partial name of ingredient e.g. gin for ginger
  :return: List of all ingredients that have ingredient as substring.
  """
  return list(filter(lambda x: ingredient.lower() in x.lower(), list_ingredients))


def search_products(list_products: List[str], product: str) -> List[str]:
  """
  Search product with partial name
  TODO: Maybe use fuzzywuzzy for approximation and spelling mistakes
  :param list_products: List of products to filter
  :param product: partial name of product to serach
  :return: List of all products that have product as substring.
  """
  return list(filter(lambda x: product.lower() in x.lower(), list_products))


def search_product_with_ingredients(ingredients: dict, products: dict, ing: Union[str, List[str]]) -> List[str]:
  """
  search products with provided ingredients
  :param products: dictionary of products
  :param ingredients: Dictionary of ingredients
  :param ing: ingredients to search, can be list or string
  :return: List of products with ingredients
  """
  if isinstance(ing, List):
    ing_id = {ingredients[i] for i in ing}
  else:
    ing_id = {ingredients[ing]}
  return [p["name"] for p in products.values() if
          all(i in p["ingredients"] for i in ing_id)]


class Shell(cmd.Cmd):
  intro = """Welcome to the D H shell. Type help or ? to list commands.\nDetailed text for help can be seen by using `help option name` e.g. `help search_ingredients`
  """
  prompt = 'D-H > '
  file = None

  def do_ingredients(self, arg):
    "List all Ingredients"
    ing = list_all_ingredients(ingredients)
    table = [ing[i:i + 5] for i in range(0, len(ing), 5)]
    print("Available Ingredients")
    print(tabulate(table, tablefmt="fancy_grid"))

  def do_products(self, arg):
    "List all products."
    prod = list_all_products(products)
    table = [prod[i:i + 5] for i in range(0, len(prod), 5)]
    print("Available Products")
    print(tabulate(table, tablefmt="fancy_grid"))

  def do_search_ingredients(self, arg):
    "Search all Ingredients\nUsage: `search_ingredients Mushrooms`"
    if not arg:
      print("Need some hints")
      return
    ing = search_ingredients(list_all_ingredients(ingredients), arg)
    table = [ing[i:i + 5] for i in range(0, len(ing), 5)]
    print("Available Ingredients")
    print(tabulate(table, tablefmt="fancy_grid"))

  def do_search_products(self, arg):
    "search all products\nUsage: `search_products Acai + Cherry`"
    if not arg:
      print("Need some hints")
      return
    prod = search_products(list_all_products(products), arg)
    table = [prod[i:i + 5] for i in range(0, len(prod), 5)]
    print("Available Products")
    print(tabulate(table, tablefmt="fancy_grid"))

  def do_search_with_ingredients(self, arg):
    "Filter products with ingredients\nUsage: \n1: `search_with_ingredients Organic Spinach`\n2: `search_with_ingredients Organic Cherry, Organic Blueberry`"
    if not arg:
      print("Need ingredients")
      return
    ing = list(map(str.strip, arg.split(",")))
    for i in ing:
      if i not in ingredients:
        print("Ingredient [%s] Not found. Maybe incorrect ingredient spellings" % i)
        self.do_search_ingredients(i)
        ing.remove(i)
    if not ing:
      print("No product")
      return
    print("Searching ingredients : %s" % str(ing))
    prod = search_product_with_ingredients(ingredients, products, ing)

    table = [prod[i:i + 5] for i in range(0, len(prod), 5)]
    print("Available Products")
    print(tabulate(table, tablefmt="fancy_grid"))

  def do_show_product_ingredients(self, arg):
    "Get all ingredients of products\nUsage: `show_product_ingredients Acai + Cherry`"
    if not arg:
      # no product arguments provided
      print("Need Product")
      return
    p = str.strip(arg)
    if p not in list_all_products(products):
      print("Product not found")
      print("Similar Products: ")
      self.do_search_products(arg)
      return
    for pr in products.values():
      if pr["name"] == p:
        product = pr
        break
    product_display = [[p, "-", "-"]]
    ingredients_rev = dict(map(reversed, ingredients.items()))
    for ing in product["ingredients"]:
      product_display.append(["-", ingredients_rev[ing], "Yes" if ingredients_rev[ing] in allergen else "No"])
    print(tabulate(product_display, tablefmt="fancy_grid", headers=["Product", "Ingredients", "Allergen"]))

  # def complete_show_product_ingredients(self, text, line, begidx, endidx):
  #   if not text:
  #     return list_all_products()
  #   else:
  #     return search_products(list_all_products(), text)

  def do_exit(self, arg):
    "Exit the prompt"
    sys.exit(0)


if __name__ == '__main__':
  Shell().cmdloop()
