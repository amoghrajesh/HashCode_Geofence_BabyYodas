from sqlalchemy import create_engine

db_uri = 'sqlite:///geofence.db' 
engine = create_engine(db_uri)

result1 = engine.execute('SELECT * FROM "device"')
#print(result.fetchall())

for r1 in result1:
  print(r1)

result2 = engine.execute('SELECT * FROM "geofence"')
#print(result.fetchall())

for r2 in result2:
   print(r2)

result3 = engine.execute('SELECT * FROM "admin"')
#print(result.fetchall())

for r3 in result3:
   print(r3)
