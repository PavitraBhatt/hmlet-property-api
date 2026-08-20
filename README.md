# Property Management API

REST API for a property management system: staff log in, register properties and
their units, keep a list of members (tenants), and place members into units under
a contract. Built with Django + Django REST Framework and JWT auth.

The interesting parts live in the contract domain — a unit cannot be double-booked,
the contract value is derived rather than supplied, and a unit's status follows from
its contracts instead of being toggled by hand.

## Stack

- Python 3.12+ / Django 6.1 / Django REST Framework
- PostgreSQL (SQLite supported for a zero-setup run)
- JWT via `djangorestframework-simplejwt`
- pytest + pytest-django

## Running it locally

```bash
git clone <this-repo>
cd hmlet-property-api

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then edit the DB credentials
python manage.py migrate
python manage.py seed_demo_data  # optional, gives you data to poke at
python manage.py runserver
```

The API is then on `http://localhost:8000/api/`.

`seed_demo_data` creates a staff login (`ops@hmlet.com` / `Sup3rSecret!`), two
properties with five units between them, three members and a few contracts,
including one that is running today and one that has already ended, so the
`?active=true` filter shows something meaningful straight away.

### Without Postgres

Set `DB_ENGINE=sqlite` in `.env` (or in the environment) and the same commands
work against a local SQLite file, which is handy if you just want to read the code and
run the suite.

```bash
DB_ENGINE=sqlite python manage.py migrate
DB_ENGINE=sqlite python manage.py runserver
```

### Tests

```bash
pytest
```

28 tests, covering auth, unit creation and filtering, the overlap rules and the
contract value maths. They run on an in-memory SQLite database by default so a
fresh clone needs nothing set up; `DB_ENGINE=postgres pytest` runs the same suite
against Postgres.

## Endpoints

All routes except register and login require `Authorization: Bearer <access token>`.

| Method | Path | Notes |
| --- | --- | --- |
| POST | `/api/auth/register` | Creates a staff user, returns the user and a token pair |
| POST | `/api/auth/login` | Email + password, returns a token pair |
| POST | `/api/auth/refresh` | Exchanges a refresh token for a new access token |
| GET | `/api/auth/me` | The authenticated user |
| POST | `/api/properties` | Create a property |
| GET | `/api/properties` | List properties, `?search=` on name |
| GET | `/api/properties/:property_id` | One property, with its units inline |
| POST | `/api/properties/:property_id/units` | Add a unit to a property |
| GET | `/api/properties/:property_id/units` | Units of one property |
| GET | `/api/units` | All units, `?status=available\|occupied`, `?property_id=` |
| POST | `/api/members` | Create a member |
| GET | `/api/members` | List members, `?search=` on name |
| GET | `/api/members/:member_id` | One member |
| POST | `/api/contracts` | Create a contract |
| GET | `/api/contracts` | List contracts, `?active=true`, `?unit_id=`, `?member_id=`, `?property_id=` |
| GET | `/api/contracts/:contract_id` | One contract |

Real request/response pairs for every one of these, error cases included, are
in [docs/API_EXAMPLES.md](docs/API_EXAMPLES.md).

List endpoints are paginated (`?page=`, 20 per page) and return the usual DRF
`count / next / previous / results` envelope.

## Layout

```
config/           settings, urls, shared exception handler
apps/
  common/         timestamp base model, seed command
  accounts/       staff user, register/login
  properties/     Property
  units/          Unit + status logic
  members/        Member (tenant)
  contracts/      Contract + the booking rules
```

One app per domain concept rather than one big `api` app. Each owns its models,
serializers, views and urls, so a change to how contracts work stays inside
`apps/contracts/`.

Business rules that decide *whether something may happen* sit in `services.py`,
not in serializers or views. `apps/contracts/services.py` is the one place that
knows how a contract is priced and when it is allowed to exist, and the API,
management commands and tests all go through it.

## Decisions worth calling out

**Preventing double-booking.** Two closed date ranges overlap when each starts
before the other ends, so the check is
`start_date <= new_end AND end_date >= new_start` against the unit's existing
contracts. A contract starting the day the previous one ends is fine; one that
shares even a single day is refused with a 400 naming the conflicting period.
The unit row is locked with `select_for_update()` for the length of the
transaction, so two requests racing for the same unit and period cannot both pass
the check. On Postgres this could also be pushed into the database with an
`ExclusionConstraint` over a `daterange`; I kept the rule in the service layer so
the same behaviour holds on SQLite, and the lock closes the race either way.

**Contract value.** Whole calendar months are charged at the full monthly rent and
any leftover tail is pro-rated over the length of the month it falls in. So
1 Jan → 31 Dec is exactly 12x rent, 15 Mar → 14 Apr is one month, and
1 Jan → 15 Feb is one month plus 15/28 of another. The period is inclusive of both
dates — a one-day contract costs one day's rent, not zero. `total_value` is stored
on the row (contracts get reported on and their historical value should not shift
if the pricing rule is ever changed) but is only ever written by the service; a
client that posts `total_value` is ignored.

**Unit status.** `status` is derived: a unit is occupied when a contract covers
today, and available otherwise. It is recomputed whenever a contract is created,
and `python manage.py sync_unit_statuses` re-derives every unit. That one is meant to run
once a day from cron, since a contract ending overnight changes a unit's status
without anyone touching the API. Treating the column as a cache of the contracts
rather than an independent flag is what keeps the two from drifting apart.

**Members are not users.** Tenants do not log into this system, so `Member` is its
own model rather than a role on `User`. Staff users use a custom user model with
email as the login field; the assignment only has staff, so `is_staff` defaults to
true.

**Errors** all come back in one shape via a single exception handler:
`{"detail": "..."}` for a plain failure, plus an `"errors"` object with the
per-field messages when validation fails.

## If I were taking this further

- Contract termination (ending a contract early) and amendments, which is where a
  `status` field on the contract would start earning its keep.
- The Postgres `ExclusionConstraint` mentioned above, as a second line of defence
  behind the service-layer check.
- OpenAPI schema via `drf-spectacular`.
- Rate limiting on the auth endpoints.
