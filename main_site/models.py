from sqlalchemy import (Boolean, Column, ForeignKey, Integer, Text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from main_site.utils import decrypt, encrypt

Base = declarative_base()


class SteelCoSchema(object):
    __table_args__ = {'schema': 'thesteelco'}


class Users(SteelCoSchema, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(Text)
    password = Column(Text)
    region = Column(Text)
    admin = Column(Boolean)

    def __init__(self, username='', password='', region='', admin=''):
        self.username = username
        if password != '':
            self.password = encrypt(password)
        else:
            self.password = ''
        self.region = region
        self.admin = admin

    def check_password(self, password):
        return password == decrypt(self.password)

    def set_password(self, newPassword):
        self.password = encrypt(newPassword)

    def serialize(self):
        return dict(
            id=self.id,
            username=self.username,
            password=decrypt(self.password),
            region=self.region,
            admin=self.admin
        )


class GeneralList(SteelCoSchema, Base):
    __tablename__ = 'general_list'

    code = Column(Text, primary_key=True)
    title = Column(Text)
    genre = Column(Text)
    company = Column(Text)
    status = Column(Text)
    notes = Column(Text)

    regions = relationship("GeneralListRegions", backref="general_list")

    def __init__(self, code='', title='', genre='', company='',
                 status='', notes=''):
        self.code = code
        self.title = title
        self.genre = genre
        self.company = company
        self.status = status
        self.notes = notes

    def serialize(self):
        ser_regions = []
        for region in self.regions:
            ser_regions.append(dict(region=region.region, avail=region.avail, notes=region.notes))
        return dict(
            code=self.code,
            title=self.title,
            genre=self.genre,
            company=self.company,
            status=self.status,
            notes=self.notes,
            regions=ser_regions
        )

    def __repr__(self):
        return '<models.GeneralList({})>'.format(self.code)


class GeneralListRegions(SteelCoSchema, Base):
    __tablename__ = 'general_list_regions'

    code = Column(Text, ForeignKey(GeneralList.code), primary_key=True)
    region = Column(Text, primary_key=True)
    avail = Column(Text)
    notes = Column(Text)


class HotList(SteelCoSchema, Base):
    __tablename__ = 'hot_list'

    code = Column(Text, primary_key=True)
    title = Column(Text)
    genre = Column(Text)
    company = Column(Text)
    status = Column(Text)
    notes = Column(Text)

    regions = relationship("HotListRegions", backref="hot_list")

    def __init__(self, code='', title='', genre='', company='',
                 status='', notes=''):
        self.code = code
        self.title = title
        self.genre = genre
        self.company = company
        self.status = status
        self.notes = notes

    def serialize(self):
        ser_regions = []
        for region in self.regions:
            ser_regions.append(dict(region=region.region, avail=region.avail, notes=region.notes))
        return dict(
            code=self.code,
            title=self.title,
            genre=self.genre,
            company=self.company,
            status=self.status,
            notes=self.notes,
            regions=ser_regions
        )

    def __repr__(self):
        return '<models.HotList({})>'.format(self.code)


class HotListRegions(SteelCoSchema, Base):
    __tablename__ = 'hot_list_regions'

    code = Column(Text, ForeignKey(HotList.code), primary_key=True)
    region = Column(Text, primary_key=True)
    avail = Column(Text)
    notes = Column(Text)
