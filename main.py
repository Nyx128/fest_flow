from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# Import everything from your other files
import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- API Endpoint to CREATE an Item ---
@app.post("/fests/", response_model=schemas.Fest)
def create_fest_endpoint(fest: schemas.FestCreate, db: Session = Depends(get_db)):
    # Now we just call our clean CRUD function
    return crud.create_fest(db=db, fest = fest)

@app.get("/fests/{fest_id}", response_model=schemas.Fest)
def read_fest(fest_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_fest(db, fest_id=fest_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Fest not found")
    return db_item