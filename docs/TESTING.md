# Testing

Basic CSV:
```csv
phone,name
+919668367700,Pipeline Test
```

Normalization test:
```csv
phone,customer_name,car_id,brand,model,year
9.16304032644E+11,Reshma,TEST001,Hyundai,Creta,2022
+916304032644,Reshma,TEST002,Honda,City,2021
```

Expected: raw/ → formatted/ + archive/ → Contact API 201 → Broadcast Launcher → Broadcast API 202 when routing matches.

A 202 means accepted/queued, not answered/completed.
