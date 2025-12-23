from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db

router = APIRouter(prefix="/reports", tags=["CRUD SQL"])


@router.get("/active")
def active_rentals(db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT * FROM v_active_rentals")).mappings().fetchall()
    return [dict(row) for row in result]


@router.get("/overdue")
def overdue_rentals(db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT * FROM v_overdue_rentals")).mappings().fetchall()
    return [dict(row) for row in result]


@router.get("/clients")
def client_stats(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM v_client_stats")
                        ).mappings().fetchall()
    return [dict(row) for row in result]


@router.get("/monthly")
def monthly_revenue(db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT * FROM v_monthly_revenue")).mappings().fetchall()
    return [dict(row) for row in result]


@router.get("/ending_soon")
def ending_soon(days: int = 2, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT * FROM get_rentals_ending_soon(:days)").bindparams(days=days)).mappings().fetchall()
    return [dict(row) for row in result]


@router.get("/period")
def period_report(start_date: str, end_date: str, db: Session = Depends(get_db)):
    result = db.execute(text(
        "SELECT * FROM get_rentals_period_report(:start_date, :end_date)").bindparams(start_date=start_date, end_date=end_date)).mappings().fetchall()
    return [dict(row) for row in result]
