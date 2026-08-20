# Sample API responses

Every response below was captured from a local run seeded with
`python manage.py seed_demo_data`, so the ids line up with what you get after
following the README.

Grab a token first:

```bash
export TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ops@hmlet.com","password":"Sup3rSecret!"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['tokens']['access'])")
```

Access tokens in the samples are truncated for readability.

---

### Login

Returns an access/refresh pair. Send the access token as `Authorization: Bearer <token>` on every other call.

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "ops@hmlet.com", "password": "Sup3rSecret!"}'
```

`200`

```json
{
  "user": {
    "id": 1,
    "email": "ops@hmlet.com",
    "full_name": "Ops Staff",
    "is_staff": true,
    "created_at": "2026-08-20T16:10:58.605239+08:00"
  },
  "tokens": {
    "access": "eyJhbGciOiJI...<truncated>",
    "refresh": "eyJhbGciOiJI...<truncated>"
  }
}
```

---

### Register a staff user

Tokens come back with the created user, so a freshly registered user is already logged in.

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "jamie.ong@hmlet.com", "full_name": "Jamie Ong", "password": "Sup3rSecret!"}'
```

`201`

```json
{
  "user": {
    "id": 2,
    "email": "jamie.ong@hmlet.com",
    "full_name": "Jamie Ong",
    "is_staff": true,
    "created_at": "2026-08-20T16:11:22.815973+08:00"
  },
  "tokens": {
    "access": "eyJhbGciOiJI...<truncated>",
    "refresh": "eyJhbGciOiJI...<truncated>"
  }
}
```

---

### Create a property

```bash
curl -X POST http://localhost:8000/api/properties \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Hmlet Cantonment", "address": "80 Cantonment Road, Singapore 089908"}'
```

`201`

```json
{
  "id": 3,
  "name": "Hmlet Cantonment",
  "address": "80 Cantonment Road, Singapore 089908",
  "created_at": "2026-08-20T16:11:22.855197+08:00",
  "updated_at": "2026-08-20T16:11:22.855268+08:00"
}
```

---

### List properties

Paginated, newest first, each row carrying its unit count.

```bash
curl -X GET http://localhost:8000/api/properties \
  -H "Authorization: Bearer $TOKEN"
```

`200`

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Cove Somerset",
      "address": "12 Somerset Road, Singapore 238164",
      "units_count": 3,
      "created_at": "2026-08-20T16:11:02.384378+08:00",
      "updated_at": "2026-08-20T16:11:02.384452+08:00"
    },
    {
      "id": 2,
      "name": "Hmlet Tiong Bahru",
      "address": "5 Kim Pong Road, Singapore 169178",
      "units_count": 2,
      "created_at": "2026-08-20T16:11:02.387959+08:00",
      "updated_at": "2026-08-20T16:11:02.388019+08:00"
    },
    {
      "id": 3,
      "name": "Hmlet Cantonment",
      "address": "80 Cantonment Road, Singapore 089908",
      "units_count": 0,
      "created_at": "2026-08-20T16:11:22.855197+08:00",
      "updated_at": "2026-08-20T16:11:22.855268+08:00"
    }
  ]
}
```

---

### Add a unit to a property

A unit always starts `available` - status is derived from its contracts, never set by the client.

```bash
curl -X POST http://localhost:8000/api/properties/3/units \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"unit_number": "07-04", "monthly_rent": "2900.00"}'
```

`201`

```json
{
  "id": 6,
  "property_id": 3,
  "property_name": "Hmlet Cantonment",
  "unit_number": "07-04",
  "monthly_rent": "2900.00",
  "status": "available",
  "created_at": "2026-08-20T16:11:22.916016+08:00",
  "updated_at": "2026-08-20T16:11:22.916097+08:00"
}
```

---

### Get a property with its units

```bash
curl -X GET http://localhost:8000/api/properties/3 \
  -H "Authorization: Bearer $TOKEN"
```

`200`

```json
{
  "id": 3,
  "name": "Hmlet Cantonment",
  "address": "80 Cantonment Road, Singapore 089908",
  "units_count": 1,
  "created_at": "2026-08-20T16:11:22.855197+08:00",
  "updated_at": "2026-08-20T16:11:22.855268+08:00",
  "units": [
    {
      "id": 6,
      "property_id": 3,
      "property_name": "Hmlet Cantonment",
      "unit_number": "07-04",
      "monthly_rent": "2900.00",
      "status": "available",
      "created_at": "2026-08-20T16:11:22.916016+08:00",
      "updated_at": "2026-08-20T16:11:22.916097+08:00"
    }
  ]
}
```

---

### List units filtered by status

```bash
curl -X GET http://localhost:8000/api/units?status=available \
  -H "Authorization: Bearer $TOKEN"
```

`200`

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "property_id": 1,
      "property_name": "Cove Somerset",
      "unit_number": "04-13",
      "monthly_rent": "2650.00",
      "status": "available",
      "created_at": "2026-08-20T16:11:02.399006+08:00",
      "updated_at": "2026-08-20T16:11:02.399033+08:00"
    },
    {
      "id": 3,
      "property_id": 1,
      "property_name": "Cove Somerset",
      "unit_number": "10-01",
      "monthly_rent": "3800.00",
      "status": "available",
      "created_at": "2026-08-20T16:11:02.401143+08:00",
      "updated_at": "2026-08-20T16:11:02.401206+08:00"
    },
    {
      "id": 4,
      "property_id": 2,
      "property_name": "Hmlet Tiong Bahru",
      "unit_number": "02-05",
      "monthly_rent": "2100.00",
      "status": "available",
      "created_at": "2026-08-20T16:11:02.403113+08:00",
      "updated_at": "2026-08-20T16:11:02.403138+08:00"
    },
    {
      "id": 5,
      "property_id": 2,
      "property_name": "Hmlet Tiong Bahru",
      "unit_number": "02-06",
      "monthly_rent": "2100.00",
      "status": "available",
      "created_at": "2026-08-20T16:11:02.406489+08:00",
      "updated_at": "2026-08-20T16:11:02.406553+08:00"
    },
    {
      "id": 6,
      "property_id": 3,
      "property_name": "Hmlet Cantonment",
      "unit_number": "07-04",
      "monthly_rent": "2900.00",
      "status": "available",
      "created_at": "2026-08-20T16:11:22.916016+08:00",
      "updated_at": "2026-08-20T16:11:22.916097+08:00"
    }
  ]
}
```

---

### Create a member (tenant)

```bash
curl -X POST http://localhost:8000/api/members \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Priya Nair", "email": "priya.nair@example.com", "phone": "+65 8123 4567"}'
```

`201`

```json
{
  "id": 4,
  "full_name": "Priya Nair",
  "email": "priya.nair@example.com",
  "phone": "+65 8123 4567",
  "created_at": "2026-08-20T16:11:22.997909+08:00",
  "updated_at": "2026-08-20T16:11:22.997957+08:00"
}
```

---

### List members

```bash
curl -X GET http://localhost:8000/api/members \
  -H "Authorization: Bearer $TOKEN"
```

`200`

```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "full_name": "Aditi Rao",
      "email": "aditi.rao@example.com",
      "phone": "",
      "created_at": "2026-08-20T16:11:02.409559+08:00",
      "updated_at": "2026-08-20T16:11:02.409616+08:00"
    },
    {
      "id": 3,
      "full_name": "Lena Fischer",
      "email": "lena.fischer@example.com",
      "phone": "",
      "created_at": "2026-08-20T16:11:02.414071+08:00",
      "updated_at": "2026-08-20T16:11:02.414089+08:00"
    },
    {
      "id": 2,
      "full_name": "Marcus Tan",
      "email": "marcus.tan@example.com",
      "phone": "",
      "created_at": "2026-08-20T16:11:02.412458+08:00",
      "updated_at": "2026-08-20T16:11:02.412512+08:00"
    },
    {
      "id": 4,
      "full_name": "Priya Nair",
      "email": "priya.nair@example.com",
      "phone": "+65 8123 4567",
      "created_at": "2026-08-20T16:11:22.997909+08:00",
      "updated_at": "2026-08-20T16:11:22.997957+08:00"
    }
  ]
}
```

---

### Create a contract

`monthly_rent` is optional and falls back to the unit's rent. `total_value` is always computed server side: 12 months x 2900.

```bash
curl -X POST http://localhost:8000/api/contracts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"member_id": 4, "unit_id": 6, "start_date": "2026-09-01", "end_date": "2027-08-31"}'
```

`201`

```json
{
  "id": 4,
  "member": {
    "id": 4,
    "full_name": "Priya Nair",
    "email": "priya.nair@example.com"
  },
  "unit": {
    "id": 6,
    "unit_number": "07-04",
    "status": "available",
    "property_id": 3,
    "property_name": "Hmlet Cantonment"
  },
  "start_date": "2026-09-01",
  "end_date": "2027-08-31",
  "monthly_rent": "2900.00",
  "total_value": "34800.00",
  "is_active": false,
  "created_at": "2026-08-20T16:11:23.083765+08:00",
  "updated_at": "2026-08-20T16:11:23.083811+08:00"
}
```

---

### Double booking is rejected

The requested period overlaps the existing contract by a single day, which is enough to refuse it.

```bash
curl -X POST http://localhost:8000/api/contracts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"member_id": 4, "unit_id": 6, "start_date": "2027-08-31", "end_date": "2028-02-29"}'
```

`400`

```json
{
  "detail": "Unit 07-04 is already booked from 2026-09-01 to 2027-08-31."
}
```

---

### Back-to-back booking is allowed

Starting the day after the previous contract ends is fine. 1 Sep 2027 to 29 Feb 2028 is six whole calendar months, so the total is a clean 6 x 2900.

```bash
curl -X POST http://localhost:8000/api/contracts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"member_id": 4, "unit_id": 6, "start_date": "2027-09-01", "end_date": "2028-02-29"}'
```

`201`

```json
{
  "id": 5,
  "member": {
    "id": 4,
    "full_name": "Priya Nair",
    "email": "priya.nair@example.com"
  },
  "unit": {
    "id": 6,
    "unit_number": "07-04",
    "status": "available",
    "property_id": 3,
    "property_name": "Hmlet Cantonment"
  },
  "start_date": "2027-09-01",
  "end_date": "2028-02-29",
  "monthly_rent": "2900.00",
  "total_value": "17400.00",
  "is_active": false,
  "created_at": "2026-08-20T16:11:23.163499+08:00",
  "updated_at": "2026-08-20T16:11:23.163572+08:00"
}
```

---

### List contracts

```bash
curl -X GET http://localhost:8000/api/contracts \
  -H "Authorization: Bearer $TOKEN"
```

`200`

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 5,
      "member": {
        "id": 4,
        "full_name": "Priya Nair",
        "email": "priya.nair@example.com"
      },
      "unit": {
        "id": 6,
        "unit_number": "07-04",
        "status": "available",
        "property_id": 3,
        "property_name": "Hmlet Cantonment"
      },
      "start_date": "2027-09-01",
      "end_date": "2028-02-29",
      "monthly_rent": "2900.00",
      "total_value": "17400.00",
      "is_active": false,
      "created_at": "2026-08-20T16:11:23.163499+08:00",
      "updated_at": "2026-08-20T16:11:23.163572+08:00"
    },
    {
      "id": 3,
      "member": {
        "id": 3,
        "full_name": "Lena Fischer",
        "email": "lena.fischer@example.com"
      },
      "unit": {
        "id": 3,
        "unit_number": "10-01",
        "status": "available",
        "property_id": 1,
        "property_name": "Cove Somerset"
      },
      "start_date": "2026-09-04",
      "end_date": "2027-09-04",
      "monthly_rent": "3600.00",
      "total_value": "43320.00",
      "is_active": false,
      "created_at": "2026-08-20T16:11:02.483239+08:00",
      "updated_at": "2026-08-20T16:11:02.483267+08:00"
    },
    {
      "id": 4,
      "member": {
        "id": 4,
        "full_name": "Priya Nair",
        "email": "priya.nair@example.com"
      },
      "unit": {
        "id": 6,
        "unit_number": "07-04",
        "status": "available",
        "property_id": 3,
        "property_name": "Hmlet Cantonment"
      },
      "start_date": "2026-09-01",
      "end_date": "2027-08-31",
      "monthly_rent": "2900.00",
      "total_value": "34800.00",
      "is_active": false,
      "created_at": "2026-08-20T16:11:23.083765+08:00",
      "updated_at": "2026-08-20T16:11:23.083811+08:00"
    },
    {
      "id": 1,
      "member": {
        "id": 1,
        "full_name": "Aditi Rao",
        "email": "aditi.rao@example.com"
      },
      "unit": {
        "id": 1,
        "unit_number": "04-12",
        "status": "occupied",
        "property_id": 1,
        "property_name": "Cove Somerset"
      },
      "start_date": "2026-07-21",
      "end_date": "2027-07-21",
      "monthly_rent": "2500.00",
      "total_value": "30080.65",
      "is_active": true,
      "created_at": "2026-08-20T16:11:02.423095+08:00",
      "updated_at": "2026-08-20T16:11:02.423161+08:00"
    },
    {
      "id": 2,
      "member": {
        "id": 2,
        "full_name": "Marcus Tan",
        "email": "marcus.tan@example.com"
      },
      "unit": {
        "id": 4,
        "unit_number": "02-05",
        "status": "available",
        "property_id": 2,
        "property_name": "Hmlet Tiong Bahru"
      },
      "start_date": "2026-02-01",
      "end_date": "2026-07-31",
      "monthly_rent": "2100.00",
      "total_value": "12600.00",
      "is_active": false,
      "created_at": "2026-08-20T16:11:02.464552+08:00",
      "updated_at": "2026-08-20T16:11:02.464600+08:00"
    }
  ]
}
```

---

### List contracts running today

```bash
curl -X GET http://localhost:8000/api/contracts?active=true \
  -H "Authorization: Bearer $TOKEN"
```

`200`

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "member": {
        "id": 1,
        "full_name": "Aditi Rao",
        "email": "aditi.rao@example.com"
      },
      "unit": {
        "id": 1,
        "unit_number": "04-12",
        "status": "occupied",
        "property_id": 1,
        "property_name": "Cove Somerset"
      },
      "start_date": "2026-07-21",
      "end_date": "2027-07-21",
      "monthly_rent": "2500.00",
      "total_value": "30080.65",
      "is_active": true,
      "created_at": "2026-08-20T16:11:02.423095+08:00",
      "updated_at": "2026-08-20T16:11:02.423161+08:00"
    }
  ]
}
```

---

### Calling without a token

Everything except register and login needs a valid JWT.

```bash
curl -X GET http://localhost:8000/api/contracts
```

`401`

```json
{
  "detail": "Authentication credentials were not provided."
}
```
