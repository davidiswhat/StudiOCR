from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase

DATABASE = 'ocr_files.db'

# Should likely change where the database files are stored
db = SqliteExtDatabase(DATABASE, c_extensions=True, pragmas=(
    ('journal_mode', 'wal'),  # Use WAL-mode
    ('foreign_keys', 1)))  # Enforce foreign-key constraints


class BaseModel(Model):
    class Meta:
        database = db


# Table entry for an OCR'ed document
class OcrDocument(BaseModel):
    id = PrimaryKeyField(null=False)
    name = CharField(unique=True)


# Stores an individual page of OCR'ed document
# Also stores the original image file of the page
class OcrPage(BaseModel):
    id = PrimaryKeyField(null=False)
    number = IntegerField()
    image = BlobField()
    document = ForeignKeyField(OcrDocument, backref='pages')


# Stores an individual text block with coordinates
class OcrBlock(BaseModel):
    id = PrimaryKeyField(null=False)
    left = IntegerField()
    top = IntegerField()
    width = IntegerField()
    height = IntegerField()
    # Should we store confidence values?
    conf = IntegerField()
    text = TextField()
    page = ForeignKeyField(OcrPage, backref='pages')


# Helper function to intially create the tables in the database
def create_tables():
    with db:
        db.create_tables([OcrDocument, OcrPage, OcrBlock])


# If the database doesn't exist yet, generate it
create_tables()