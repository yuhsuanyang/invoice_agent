# from pypdf import PdfReader
import numpy as np
import pandas as pd
import re
from fastapi import FastAPI  # , UploadFile, File
from rapidfuzz import fuzz
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
    if product_id in db["品號"]:
        match_item = db[db["品號"] == product_id]
        match_name = match_item["品名"].values[0]
        unit = match_item["單位"].values[0]
        match_score = 100
    else:
        candidates = []
        product_to_match = product_name + "_" + unit
        for char in product_name:
            candidates.extend(
                db[db["品名"].str.contains(re.escape(char), regex=True)][
                    "product_and_unit"
                ].values.tolist()
            )
        if candidates:
            similarities = [fuzz.ratio(product_to_match, name) for name in candidates]
            max_index = np.argmax(similarities)
            match_item = db[db["product_and_unit"] == candidates[max_index]]
            product_id = match_item["品號"].values[0]
            match_name = match_item["品名"].values[0]
            unit = match_item["單位"].values[0]
            match_score = round(similarities[max_index], 2)
        else:
            product_id = ""
            match_name = ""
            match_score = 0

    return {
        "product_id": product_id,
        "match_name": match_name,
        "original_input": product_name,
        "quantity": amount,
        "unit": unit,
        "match_score": match_score,
    }


@app.post("/fuzzy_match")
def wrapper(data: List[Item]):
    results = []
    for item in data:
        result = fuzzy_match(item.product_id, item.product_name, item.unit, item.amount)
        results.append(result)
    return {"items": results}


# @app.post("/read_pdf")
# async def load_pdf(file: UploadFile = File(...)):
#     print(file)
#     reader = PdfReader(file.file)
#     text = ""
#     for page in reader.pages:
#         text += page.extract_text()
#     return {
#         "filename": file.filename,
#         "text": text
#     }
