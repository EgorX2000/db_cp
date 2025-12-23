from fastapi import FastAPI
from .routers import rentals, reports, batch

app = FastAPI(
    title="Система управления арендой инструментов и оборудования",
    version="1.0"
)

app.include_router(rentals.router)
app.include_router(reports.router)
app.include_router(batch.router)


@app.get("/")
def root():
    return {"message": "API системы аренды оборудования работает!"}
