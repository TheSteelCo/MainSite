from sqlalchemy import (Column, Text)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SteelCoSchema(object):
    __table_args__ = {'schema': 'thesteelco'}


class GeneralList(SteelCoSchema, Base):
    __tablename__ = 'general_list'

    code = Column(Text, primary_key=True)
    title = Column(Text)
    genre = Column(Text)
    company = Column(Text)
    status = Column(Text)
    notes = Column(Text)

    def serialize(self):
        return dict(
            code=self.code,
            title=self.title,
            genre=self.genre,
            company=self.company,
            status=self.status,
            notes=self.notes)


class GeneralListRegions(SteelCoSchema, Base):
    __tablename__ = 'general_list_regions'

    code = Column(Text, primary_key=True)
    region = Column(Text, primary_key=True)
    avail = Column(Text)
    notes = Column(Text)
