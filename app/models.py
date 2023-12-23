from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    session_id = Column(String(50), primary_key=True, unique=True)
    parcels = relationship('Parcel', back_populates='user')


class ParcelType(Base):
    __tablename__ = 'parcel_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)


class Parcel(Base):
    __tablename__ = 'parcel'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    weight = Column(Float)
    parcel_type_id = Column(
        Integer,
        ForeignKey('parcel_types.id'),
        nullable=False
    )
    content_value = Column(Float)
    user_session_id = Column(String(50), ForeignKey('user.session_id'))
    delivery_cost = Column(Float, nullable=True)
    delivery_company_id = Column(Integer, ForeignKey('companies.id'))

    company = relationship('Company', back_populates='parcels')
    user = relationship('User', back_populates='parcels')
    parcel_type = relationship('ParcelType', backref='parcels')


class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    parcels = relationship('Parcel', back_populates='company')
