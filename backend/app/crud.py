from sqlalchemy.orm import Session
from . import models, schemas


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
