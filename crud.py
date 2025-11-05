from sqlalchemy.orm import Session
import models, schemas

#all read operations
def get_fest(db: Session, fest_id: int):
    return db.query(models.Fest).filter(models.Fest.fest_id == fest_id).first()


#all write operations
def create_fest(db: Session, fest: schemas.FestCreate):
    # Create an instance of the SQLAlchemy model from the Pydantic schema
    db_item = models.Fest(name = fest.name, year = fest.year)
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item