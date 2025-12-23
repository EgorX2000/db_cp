from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
from .. import crud, schemas, database

router = APIRouter(prefix="/rentals", tags=["Аренды"])


@router.post("/", response_model=schemas.RentalResponse)
def create_rental(rental: schemas.RentalCreate, db: Session = Depends(database.get_db)):
    try:
        return crud.create_rental(db=db, rental=rental)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{rental_id}", response_model=schemas.RentalResponse)
def read_rental(rental_id: int, db: Session = Depends(database.get_db)):
    try:
        rental = crud.get_rental(db=db, rental_id=rental_id)
        if not rental:
            raise HTTPException(status_code=404, detail="Аренда не найдена")
        return rental
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{rental_id}/return", response_model=schemas.RentalResponse)
def return_rental(rental_id: int, return_date: date, db: Session = Depends(database.get_db)):
    try:
        return crud.return_rental(db=db, rental_id=rental_id, return_date=return_date)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_rental(rental_id: int, db: Session = Depends(database.get_db)):
    try:
        rental = crud.cancel_rental(db=db, rental_id=rental_id)
        return None
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
