from gluon.contrib.populate import populate
if db(db.t_taste).isempty():
     populate(db.t_taste, 5)
if db(db.t_category).isempty():
          populate(db.t_category, 5)
          populate(db.t_review, 5)
          populate(db.t_recipe, 5)
          populate(db.t_smoothie, 5)
          populate(db.t_fruit, 5)
          populate(db.t_fruit_category, 5)


