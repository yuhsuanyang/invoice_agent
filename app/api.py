import numpy as np
import pandas as pd
import re
from fastapi import FastAPI
from rapidfuzz import fuzz  # package that serve for fuzzy matching
from pydantic import BaseModel
from typing import List

db = pd.read_excel("客戶訂單資料.xlsx")
db["product_and_unit"] = db["品名"] + "_" + db["單位"]


class Item(BaseModel):
    product_id: str
    product_name: str
    unit: str
    amount: int


app = FastAPI()


def fuzzy_match(product_id: str, product_name: str, unit: str, amount: int):
    # if product_id is in the database, use it to find the product (assume product_id is correct)
    if product_id in db["品號"]:
        match_item = db[db["品號"] == product_id]
        match_name = match_item["品名"].values[0]
        match_unit = match_item["單位"].values[0]
        match_score = 100
    else:
        candidates = []
        # because same product name may have different units, we need to match the unit as well
        product_to_match = product_name + "_" + unit
        # candidates are select if they contain any character in product_name
        for char in product_name:
            candidates.extend(
                db[db["品名"].str.contains(re.escape(char), regex=True)][
                    "product_and_unit"
                ].values.tolist()
            )
        candidates = list(set(candidates))
        if candidates:
            similarities = [fuzz.ratio(product_to_match, name) for name in candidates]
            # get the index of the max similarity
            max_index = np.argmax(similarities)
            match_item = db[db["product_and_unit"] == candidates[max_index]]
            product_id = match_item["品號"].values[0]
            match_name = match_item["品名"].values[0]
            match_unit = match_item["單位"].values[0]
            match_score = round(similarities[max_index], 2)
        else:  # if no candidates found, return empty result
            product_id = ""
            match_name = ""
            match_unit = ""
            match_score = 0

    return {
        "product_id": product_id,
        "match_name": match_name,
        "original_input_name": product_name,
        "original_input_unit": unit,
        "unit": match_unit,
        "quantity": amount,
        "match_score": match_score,
    }


@app.post("/fuzzy_match")
def wrapper(data: List[Item]):
    results = []
    for item in data:
        result = fuzzy_match(item.product_id, item.product_name, item.unit, item.amount)
        results.append(result)
    return {"items": results}
