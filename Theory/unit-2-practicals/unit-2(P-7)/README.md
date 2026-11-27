# Unit 2 (P-7): Authentication with JWT (Lecture 20)

## Lab exercise
1. Implement JWT authentication for the Student Management API.
2. Add a password field to the Student model (stored as a hashed password).
3. Create `/login` and `/register` endpoints.
4. Secure `DELETE /students/{id}` so only admins or the student themselves can use it.
5. Test the flow in Postman: register, login (get JWT), access a protected route, access it without a token (401).
6. Implement token expiration and test what happens when the token expires.

This builds on P-6. New or changed files: `auth.py` (hashing and JWT), `models.py` (`hashed_password`, `role`), `schemas.py`, `main.py`, `create_admin.py`.

## Run
```bash
cd "unit-2(P-7)"
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload
pytest -q                      # automated version of the Postman steps (about 10 s: bcrypt is slow on purpose, plus a 2 s expiry wait)
```
Swagger UI: http://127.0.0.1:8000/docs (use the **Authorize** button: username = email, password).

Create an admin (needed to test "admin may delete anyone"):
```bash
python create_admin.py admin@upes.ac.in "Admin@12345" "Admin User"
```
Self-registration can only create students, so nobody can make themselves admin.

## Postman steps
| # | Request | Expected |
|---|---|---|
| 1 | `POST /register`, Body raw JSON `{"name":"Aarav","email":"aarav@upes.ac.in","branch":"CSE","password":"Str0ngPass!"}` | 201, no password in the response |
| 2 | `POST /login`, Body **x-www-form-urlencoded**: `username=aarav@upes.ac.in`, `password=Str0ngPass!` | 200, `access_token` |
| 3 | `GET /me`, Authorization tab, Type **Bearer Token**, paste the token | 200 |
| 4 | `GET /me` with **No Auth** | 401 `Not authenticated` |
| 5 | `DELETE /students/{another id}` with Aarav's token | 403 |
| 6 | `DELETE /students/{Aarav's id}` with Aarav's token | 204 |
| 7 | Log in as admin, `DELETE /students/{any id}` | 204 |

Login uses form data (not JSON) because that is the OAuth2 password-flow standard and it makes the Swagger Authorize button work.

## Testing token expiry in Postman
Default lifetime is 30 minutes. For a quick test start the server with a 30-second lifetime:
```bash
# Windows PowerShell
$env:ACCESS_TOKEN_EXPIRE_MINUTES="0.5"; uvicorn main:app --reload
# Mac / Linux
ACCESS_TOKEN_EXPIRE_MINUTES=0.5 uvicorn main:app --reload
```
Log in, call `GET /me` (200), wait 30 seconds, call it again: **401 "Token has expired, please log in again"**. The client must log in again to get a new token.

## Security notes
- Passwords are hashed with **bcrypt** (salted). The plain password is never stored or returned.
- The JWT contains `sub` (user id), `role` and `exp`. It is signed (HS256), not encrypted, so never put secrets inside it.
- Set a real secret in production: `SECRET_KEY=<long random string>` (generate one with `python -c "import secrets; print(secrets.token_hex(32))"`). The default in `auth.py` is for local development only.
- Wrong email and wrong password return the identical 401 message, so attackers cannot discover which emails exist.
- I also restricted `PUT`, `PATCH` and enrollment changes to admin-or-self. Without this any logged-in student could edit anyone's record.
- The slides use `python-jose` and `passlib`. This project uses `PyJWT` and `bcrypt` directly because they are actively maintained and avoid known compatibility problems between passlib and newer bcrypt versions. The concepts are identical.
