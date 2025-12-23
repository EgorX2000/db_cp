from sqlalchemy.orm import Session, joinedload
from . import models, schemas
from datetime import date
from typing import List, Optional


def create_rental(db: Session, rental: schemas.RentalCreate):
    db_rental = models.Rentals(
        user_id=rental.user_id,
        employee_id=rental.employee_id,
        start_date=rental.start_date,
        end_date=rental.end_date,
        return_date=rental.return_date,
        status="Активен"
    )
    db.add(db_rental)
    db.flush()

    for item in rental.items:
        db_item = models.RentalItems(
            rental_id=db_rental.id,
            equipment_id=item.equipment_id,
            damage_fee=item.damage_fee
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_rental)
    return db_rental


def get_rental(db: Session, rental_id: int):
    return (
        db.query(models.Rentals)
        .options(
            joinedload(models.Rentals.items)
            .joinedload(models.RentalItems.equipment)
            .joinedload(models.Equipment.model)
        )
        .filter(models.Rentals.id == rental_id)
        .first()
    )


def return_rental(db: Session, rental_id: int, return_date: date):
    rental = db.query(models.Rentals).filter(
        models.Rentals.id == rental_id).first()
    if not rental:
        raise ValueError("Аренда не найдена")
    if rental.status in ("Завершён", "Отменён"):
        raise ValueError("Аренда уже завершена или отменена")
    if return_date < rental.start_date:
        raise ValueError("Дата возврата не может быть раньше даты начала")

    rental.return_date = return_date
    rental.status = "Завершён"

    db.commit()
    db.refresh(rental)
    return rental


def cancel_rental(db: Session, rental_id: int):
    rental = db.query(models.Rentals).filter(
        models.Rentals.id == rental_id).first()
    if not rental:
        raise ValueError("Аренда не найдена")
    if rental.status not in ("Активен", "Просрочен срок аренды"):
        raise ValueError(
            "Можно отменять только активные или просроченные аренды")

    rental.status = "Отменён"
    db.commit()
    db.refresh(rental)
    return rental
