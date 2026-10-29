#!/usr/bin/env python3
import json
import re

# 1. Existing cards currently in index.html
existing_cards_data = [
    {"num": "9000000000", "price": 25000, "originalPrice": 40000, "tag": "hexa", "category": "Hexa Numbers", "seconds": 6320},
    {"num": "9880000000", "price": 16000, "originalPrice": 30000, "tag": "hexa", "category": "Hexa Numbers", "seconds": 8110},
    {"num": "7010106666", "price": 11000, "originalPrice": 16000, "tag": "mirror", "category": "Mirror Numbers", "seconds": 16325},
    {"num": "7010107777", "price": 11000, "originalPrice": 16000, "tag": "mirror", "category": "Mirror Numbers", "seconds": 3522},
    {"num": "7010110000", "price": 11000, "originalPrice": 16000, "tag": "0000", "category": "0000 Ending", "seconds": 11367},
    {"num": "7010111100", "price": 11000, "originalPrice": 16000, "tag": "mirror", "category": "Mirror Numbers", "seconds": 19367},
    {"num": "7010111222", "price": 11000, "originalPrice": 16000, "tag": "mirror", "category": "Mirror Numbers", "seconds": 4472},
    {"num": "7010111133", "price": 11000, "originalPrice": 16000, "tag": "mirror", "category": "Mirror Numbers", "seconds": 9918},
    {"num": "7010116666", "price": 11000, "originalPrice": 16000, "tag": "mirror", "category": "Mirror Numbers", "seconds": 12644},
    {"num": "7010117777", "price": 11000, "originalPrice": 16000, "tag": "mirror", "category": "Mirror Numbers", "seconds": 7128},
    {"num": "7010118888", "price": 11000, "originalPrice": 16000, "tag": "mirror", "category": "Mirror Numbers", "seconds": 15495},
    {"num": "7010119999", "price": 11000, "originalPrice": 16000, "tag": "triple9", "category": "Triple 9", "seconds": 2915},
    {"num": "7010120000", "price": 12250, "originalPrice": 18000, "tag": "0000", "category": "0000 Ending", "seconds": 18240},
    {"num": "7010121111", "price": 12250, "originalPrice": 18000, "tag": "mirror", "category": "Mirror Numbers", "seconds": 10332},
    {"num": "7010184444", "price": 12999, "originalPrice": 19000, "tag": "mirror", "category": "Mirror Numbers", "seconds": 5954},
    {"num": "7010185555", "price": 12999, "originalPrice": 19000, "tag": "mirror", "category": "Mirror Numbers", "seconds": 13532}
]

# 2. User Prompt Categories & Numbers
user_groups = [
    {
        "category": "70101 Series — Repeating Numbers",
        "tag": "70101-repeating",
        "price": 12250,
        "originalPrice": 18000,
        "numbers": [
            "7010101111", "7010102222", "7010104444", "7010105555", "7010106666",
            "7010107777", "7010110000", "7010112222", "7010113333", "7010114444",
            "7010115555", "7010116666", "7010117777", "7010118888", "7010119999",
            "7010120000", "7010121111", "7010123333", "7010124444", "7010125555",
            "7010126666", "7010127777", "7010128888", "7010129999", "7010130000",
            "7010131111", "7010132222", "7010134444", "7010135555", "7010136666",
            "7010137777", "7010138888", "7010139999", "7010140000", "7010141111",
            "7010142222", "7010143333", "7010145555", "7010146666", "7010147777",
            "7010148888", "7010149999", "7010150000", "7010151111", "7010152222",
            "7010153333", "7010154444", "7010156666", "7010157777", "7010158888",
            "7010159999", "7010160000", "7010161111", "7010162222", "7010163333",
            "7010164444", "7010165555", "7010167777", "7010168888", "7010169999",
            "7010170000", "7010171111", "7010172222", "7010173333", "7010174444",
            "7010175555", "7010176666", "7010178888", "7010179999", "7010180000",
            "7010181111", "7010182222", "7010183333", "7010184444", "7010185555"
        ]
    },
    {
        "category": "70101 Series — Mixed Repeating Numbers",
        "tag": "70101-mixed",
        "price": 8800,
        "originalPrice": 13500,
        "numbers": [
            "7010111100", "7010111122", "7010111133", "7010111144", "7010111155",
            "7010111166", "7010111177", "7010111188", "7010111199"
        ]
    },
    {
        "category": "9 Series Numbers",
        "tag": "9-series",
        "price": 11500,
        "originalPrice": 18000,
        "numbers": ["9999999995", "9999999996", "9999999997", "9999999998"]
    },
    {
        "category": "9 Series VIP Numbers",
        "tag": "9-series-vip",
        "items": [
            {"num": "9123000002", "price": 8300, "originalPrice": 12500},
            {"num": "9123000007", "price": 8300, "originalPrice": 12500},
            {"num": "9123000008", "price": 8300, "originalPrice": 12500},
            {"num": "9512395123", "price": 6000, "originalPrice": 9500},
            {"num": "9292879292", "price": 5500, "originalPrice": 8500}
        ]
    },
    {
        "category": "9 Series Penta Numbers",
        "tag": "9-series-penta",
        "price": 11500,
        "originalPrice": 18000,
        "numbers": ["9999966666", "9999977777"]
    },
    {
        "category": "8 Series Numbers",
        "tag": "8-series",
        "items": [
            {"num": "8808888088", "price": 11500, "originalPrice": 18000},
            {"num": "8888588885", "price": 11500, "originalPrice": 18000},
            {"num": "8988889888", "price": 11000, "originalPrice": 17000},
            {"num": "8888878888", "price": 11000, "originalPrice": 17000}
        ]
    },
    {
        "category": "Penta Series",
        "tag": "penta-series",
        "price": 8800,
        "originalPrice": 14000,
        "numbers": ["7777755555", "6666655555"]
    },
    {
        "category": "VIP 5 Series 5",
        "tag": "vip-5-series",
        "items": [
            {"num": "7805555555", "price": 7500, "originalPrice": 12000},
            {"num": "7085555555", "price": 7500, "originalPrice": 12000},
            {"num": "7205555555", "price": 7500, "originalPrice": 12000},
            {"num": "6222555555", "price": 6000, "originalPrice": 9500}
        ]
    },
    {
        "category": "VIP Number",
        "tag": "vip-numbers",
        "items": [
            {"num": "9797889999", "price": 5500, "originalPrice": 9000},
            {"num": "7999999143", "price": 4500, "originalPrice": 7500},
            {"num": "6262108108", "price": 3500, "originalPrice": 5500}
        ]
    },
    {
        "category": "Mirror Numbers",
        "tag": "mirror-numbers",
        "price": 8800,
        "originalPrice": 14000,
        "numbers": ["7070370703", "7222272222", "7333373333"]
    },
    {
        "category": "7 Series Numbers",
        "tag": "7-series",
        "price": 12500,
        "originalPrice": 19000,
        "numbers": ["7100000000", "7200000000", "7600000000"]
    },
    {
        "category": "7 Series VIP Numbers",
        "tag": "7-series-vip",
        "price": 7000,
        "originalPrice": 11000,
        "numbers": ["7444474444", "7000006789", "7000007100"]
    },
    {
        "category": "786 Series Numbers",
        "tag": "786-series",
        "price": 8800,
        "originalPrice": 14000,
        "numbers": ["7867867861", "7867867862"]
    },
    {
        "category": "6 Series Numbers",
        "tag": "6-series",
        "items": [
            {"num": "6600000007", "price": 6000, "originalPrice": 9500},
            {"num": "6600000008", "price": 6000, "originalPrice": 9500},
            {"num": "6289898989", "price": 5000, "originalPrice": 8500}
        ]
    }
]

# Track database records by 10-digit number string
database = {}

# Seed initial existing cards
existing_count = len(existing_cards_data)
for item in existing_cards_data:
    database[item["num"]] = {
        "number": str(item["num"]),
        "price": item["price"],
        "originalPrice": item.get("originalPrice", int(item["price"] * 1.5)),
        "category": item["category"],
        "tag": item["tag"],
        "seconds": item.get("seconds", 7200)
    }

# Process upsert from user prompt
already_present_count = 0
added_count = 0

import random
random.seed(42)

for grp in user_groups:
    cat = grp["category"]
    tag = grp["tag"]
    items = []
    if "numbers" in grp:
        for n in grp["numbers"]:
            items.append({"num": n, "price": grp["price"], "originalPrice": grp.get("originalPrice", int(grp["price"] * 1.5))})
    elif "items" in grp:
        items = grp["items"]
    
    for item in items:
        num_str = str(item["num"]).strip()
        price = item["price"]
        orig_price = item["originalPrice"]
        
        if num_str in database:
            already_present_count += 1
            # Update to latest prompt price & category
            database[num_str]["price"] = price
            database[num_str]["originalPrice"] = orig_price
            database[num_str]["category"] = cat
            database[num_str]["tag"] = tag
        else:
            added_count += 1
            sec = random.randint(2800, 19200)
            database[num_str] = {
                "number": num_str,
                "price": price,
                "originalPrice": orig_price,
                "category": cat,
                "tag": tag,
                "seconds": sec
            }

total_records = len(database)

# Assign tags list for rich filtering
for num_str, record in database.items():
    tags = ["all", record["tag"]]
    if "786" in num_str:
        tags.extend(["786", "786-series"])
    if "999" in num_str:
        tags.extend(["triple9", "9-series"])
    if "0000" in num_str:
        tags.extend(["0000", "0000-ending"])
    if num_str.startswith("9"):
        tags.append("9-series")
    if num_str.startswith("8"):
        tags.append("8-series")
    if num_str.startswith("7"):
        tags.append("7-series")
    if num_str.startswith("6"):
        tags.append("6-series")
    if "penta" in record["tag"] or "55555" in num_str or "66666" in num_str or "77777" in num_str:
        tags.append("penta")
    if "mirror" in record["tag"] or "Mirror" in record["category"]:
        tags.append("mirror")
    if "70101" in num_str:
        tags.append("70101")
        if "Mixed" in record["category"]:
            tags.append("70101-mixed")
        else:
            tags.append("70101-repeating")
    if "vip" in record["tag"] or "VIP" in record["category"]:
        tags.append("vip")
    if record["tag"] == "hexa" or len(set(num_str[-6:])) == 1:
        tags.append("hexa")
    record["tags"] = list(set(tags))

print(f"Report: Initially present: {existing_count}")
print(f"Report: Overlapping / Already present in user prompt: {already_present_count}")
print(f"Report: Newly added from prompt: {added_count}")
print(f"Report: Total records in database: {total_records}")

# Save JSON database
data_path = "/Users/manishshaw/Downloads/stitch_cip_number_marketplace/data/numbers.json"
with open(data_path, "w") as f:
    json.dump(list(database.values()), f, indent=2)

print(f"Saved database to {data_path}")

