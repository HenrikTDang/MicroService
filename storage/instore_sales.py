from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql.sqltypes import Numeric
from base import Base
import datetime

class InstoreSales(Base):
    """CREATE TABLE instore_sales
        (id INTEGER PRIMARY KEY ASC, 
        product_id VARCHAR(250) NOT NULL,
        store_id VARCHAR(4) NOT NULL,
        customer_id VARCHAR(10) NOT NULL,
        sales_date DATETIME NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(6,2) NOT NULL,
        date_created VARCHAR(100) NOT NULL)"""

    __tablename__ = "instore_sales"

    id = Column(Integer, primary_key=True)
    product_id = Column(String(250), primary_key=True)
    store_id = Column(String(4), nullable=False)
    customer_id = Column(String(10), nullable=False)
    sales_date = Column(String(250), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, product_id, store_id, customer_id, sales_date, quantity, unit_price):
        self.product_id = product_id
        self.store_id = store_id
        self.customer_id = customer_id
        self.sales_date = sales_date
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.quantity = quantity
        self.unit_price = unit_price

    def to_dict(self):
        dict = {}
        dict['id'] = self.id
        dict['product_id'] = self.product_id
        dict['store_id'] = self.store_id
        dict['customer_id'] = self.customer_id
        dict['sales_date'] = self.sales_date
        dict['bill_amount'] = {}
        dict['bill_amount']['quantity'] = self.quantity
        dict['bill_amount']['unit_price'] = self.unit_price
        dict['date_created'] = self.date_created

        return dict    
