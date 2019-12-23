#!/usr/bin/python2.7

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_database import Base, Item, Item_adds, User

engine = create_engine('sqlite:///catalog.db')

DBsession = sessionmaker(bind=engine)
session = DBsession()

# master user right now

User1 = User(name="Evan Schoening",
             email="evan.schoening@gamil.com", picture="none")

session.add(User1)
session.commit()

# User1 for testing
Item1 = Item(user_id=1, item_name="bicycle",
             description="A bicycle for riding, kind of broken")

session.add(Item1)
session.commit()

Item1_add = Item_adds(user_id=1, item_add_name="Wheel",
                      description="Road bike Wheel", item=Item1)
session.add(Item1_add)
session.commit()

Item1_add1 = Item_adds(user_id=1, item_add_name="Lights",
                       description="Lights for seeing", item=Item1)
session.add(Item1_add1)
session.commit()


# Item2
Item2 = Item(user_id=1, item_name="Boat",
             description="This is a boat for floating")
session.add(Item2)
session.commit()

Item2_add = Item_adds(user_id=1, item_add_name="lifejacket",
                      description="For floating", item=Item2)
session.add(Item2_add)
session.commit()

Item2_add1 = Item_adds(user_id=1, item_add_name="Beer",
                       description="For drinking", item=Item2)

session.add(Item2_add1)
session.commit()

# Item3
Item3 = Item(user_id=1, item_name="Car",
             description="A car that runs when it wants to")
session.add(Item3)
session.commit()

Item3_add = Item_adds(user_id=1, item_add_name="half a tire",
                      description="Its jumk", item=Item3)
session.add(Item3_add)
session.commit()

Item3_add1 = Item_adds(user_id=1, item_add_name="steering wheel",
                       description="For turning", item=Item3)

session.add(Item3_add1)
session.commit()

Item3_add2 = Item_adds(user_id=1, item_add_name="car seat",
                       description="For babies to sit in", item=Item3)

session.add(Item3_add2)
session.commit()
print ("added items")
