from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class OnlineSales(Base):
    """ 
        CREATE TABLE online_sales
        (id INTEGER PRIMARY KEY ASC, 
        product_id VARCHAR(10) NOT NULL,
        customer_id VARCHAR(10) NOT NULL,
        delivery_info VARCHAR(250) NOT NULL,
        sales_date DATETIME NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(6,2) NOT NULL,
        date_created VARCHAR(100) NOT NULL)
    """
    __tablename__ = "online_sales"

    id = Column(Integer, primary_key=True)
    product_id = Column(String(250), nullable=False)
    customer_id = Column(String(10), nullable=False)
    delivery_info = Column(String(4), nullable=False)
    sales_date = Column(String(250), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, product_id, customer_id,delivery_info, sales_date, quantity, unit_price):
        self.product_id = product_id
        self.customer_id = customer_id
        self.delivery_info = delivery_info
        self.sales_date = sales_date
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.quantity = quantity
        self.unit_price = unit_price

    def to_dict(self):
        """ Dictionary Representation of a blood pressure reading """
        dict = {}
        dict['id'] = self.id
        dict['product_id'] = self.product_id
        dict['customer_id'] = self.customer_id
        dict['delivery_info'] = self.delivery_info
        dict['sales_date'] = self.sales_date
        dict['bill_amount'] = {}
        dict['bill_amount']['quantity'] = self.quantity
        dict['bill_amount']['unit_price'] = self.unit_price
        dict['date_created'] = self.date_created

        return dict    
