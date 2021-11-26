from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class MembershipValidity(Base):
    """ Cortisol Level """

    __tablename__ = "membership_validity"

    id = Column(Integer, primary_key=True)
    member_id = Column(String(250), nullable=False)
    location_id = Column(String(250), nullable=False)
    start_date = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    duration_months = Column(Integer, nullable=False)

    def __init__(self, member_id, location_id, start_date, duration_months):
        """ Initializes a cortisol level reading """
        self.member_id = member_id
        self.location_id = location_id
        self.start_date = start_date
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.duration_months = duration_months

    def to_dict(self):
        """ Dictionary Representation of a cortisol level reading """
        dict = {}
        dict['id'] = self.id
        dict['member_id'] = self.member_id
        dict['location_id'] = self.location_id
        dict['duration_months'] = self.duration_months
        dict['start_date'] = self.start_date
        dict['date_created'] = self.date_created

        return dict
