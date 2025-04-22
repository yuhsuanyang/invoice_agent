FROM python:3.13
COPY requirements.txt .
COPY 客戶訂單資料.xlsx .
RUN pip install -r requirements.txt
COPY api.py .
EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
