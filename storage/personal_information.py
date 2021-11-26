from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class PersonalInformationEntry(Base):
    """ Blood Sugar """

    __tablename__ = "personal_information"

    id = Column(Integer, primary_key=True)
    member_id = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    address = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, member_id, name, address, age):
        """ Initializes a blood sugar reading """
        self.member_id = member_id
        self.name = name
        self.age = age
        self.address = address
        self.date_created = datetime.datetime.now() # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of a blood sugar reading """
        dict = {}
        dict['id'] = self.id
        dict['member_id'] = self.member_id
        dict['name'] = self.name
        dict['age'] = self.age
        dict['address'] = self.address
        dict['date_created'] = self.date_created

        return dict