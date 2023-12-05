import anvil

air = anvil.Block("minecraft", "air")
stone = anvil.Block("minecraft", "stone")
grass_block = anvil.Block("minecraft", "grass_block")
coarse_dirt = dirt = anvil.Block("minecraft", "dirt")
sand = anvil.Block("minecraft", "sand")
gravel = anvil.Block("minecraft", "gravel")
brick = anvil.Block.from_numeric_id(45)
stone_brick = anvil.Block("minecraft", "stone_bricks")
mossy_stone_brick = anvil.Block("minecraft", "mossy_stone_bricks")
oak_planks = anvil.Block("minecraft", "oak_planks")
black_wool = anvil.Block.from_numeric_id(35, 15)
snow = anvil.Block("minecraft", "snow")
packed_ice = anvil.Block("minecraft", "packed_ice")
terracotta = anvil.Block("minecraft", "gray_glazed_terracotta")
podzol = anvil.Block.from_numeric_id(3, 2)
grass = anvil.Block.from_numeric_id(175, 2)
farmland = anvil.Block("minecraft", "farmland")
water = anvil.Block("minecraft", "water")
wheat = anvil.Block("minecraft", "wheat")
carrots = anvil.Block("minecraft", "carrots")
potatoes = anvil.Block("minecraft", "potatoes")
cobblestone = anvil.Block("minecraft", "cobblestone")
iron_block = anvil.Block("minecraft", "iron_block")
log = anvil.Block.from_numeric_id(17)
leaves = anvil.Block.from_numeric_id(18)
white_stained_glass = anvil.Block("minecraft", "white_stained_glass")
dark_oak_door_lower = anvil.Block(
    "minecraft", "dark_oak_door", properties={"half": "lower"}
)
dark_oak_door_upper = anvil.Block(
    "minecraft", "dark_oak_door", properties={"half": "upper"}
)
cobblestone_wall = anvil.Block("minecraft", "cobblestone_wall")
stone_brick_slab = anvil.Block.from_numeric_id(44, 5)
red_flower = anvil.Block.from_numeric_id(38)
white_concrete = anvil.Block("minecraft", "white_concrete")
black_concrete = anvil.Block("minecraft", "black_concrete")
gray_concrete = anvil.Block("minecraft", "gray_concrete")
red_concrete = anvil.Block("minecraft", "red_concrete")
brown_concrete = anvil.Block("minecraft", "brown_concrete")
yellow_concrete = anvil.Block("minecraft", "yellow_concrete")
light_gray_concrete = anvil.Block("minecraft", "light_gray_concrete")
light_blue_concrete = anvil.Block("minecraft", "light_blue_concrete")
gray_concrete_powder = anvil.Block("minecraft", "concrete_powder")
green_stained_hardened_clay = anvil.Block.from_numeric_id(159, 5)
dirt = anvil.Block("minecraft", "dirt")
glowstone = anvil.Block("minecraft", "glowstone")
sponge = anvil.Block("minecraft", "sponge")


MIN_HEIGHT = 0
MAX_HEIGHT = 100