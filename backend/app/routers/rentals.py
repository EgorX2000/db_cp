from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database

router = APIRouter(prefix="/rentals", tags=["Аренды"])


@router.post("/", response_model=schemas.RentalResponse)
def create_rental(rental: schemas.RentalCreate, db: Session = Depends(database.get_db)):
    try:
        return crud.create_rental(db=db, rental=rental)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
