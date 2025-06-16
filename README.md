# mini-oauth2

mini-oauth2 is a simple OAuth 2.0 server implementation. mini-oauth2 is a JWT certification issuer(authorization center). user can authorize client by local username/password or social account(google, github, apple).

## How to use
1. Install, config(.env file) & run mini-oauth2
2. Add client with API on http://localhost:3000/docs
3. User OAuth2 service like this:
 - Google login: `http://localhost:3000/signin/google?response_type=code&redirect_uri={to}&client_id={client_id}&state={state}`
 - Local login: `http://localhost:3000/signin?response_type=code&redirect_uri={to}&client_id={client_id}&state={state}`

## Features
- [x] Simple
- [x] Seamless social account authorization(google, github, apple)
- [x] Simplest JWT access token with EdDSA

## Social login flow
1. Write url: `https://mini-oauth/signin/google?response_type=code&redirect_uri=https://host/callback&client_id=id&state=state`
2. mini-oauth will save the state and redirect_uri, and then redirect to google login page
3. mini-oauth will create or update user info from google
4. mini-oauth will redirect to redirect_uri with code
5. client can use code to get access token


## Supported social login
- [x] Google /signin/google
- [x] Github /signin/github
- [x] Apple /signin/apple

## Installation

```bash

# Run the container with docker compose
docker compose up -d

# view API docs
http://localhost:3000/docs

# for development
uv venv
source .venv/bin/activate
uv sync
uv run uvicorn app.main:app --reload

sudo docker run --name postgres1 -e POSTGRES_PASSWORD='postgres' -d -p 5432:5432 postgres
sudo docker run --name redis1 -d -p 6379:6379 redis


# Build the image
docker build -t daqiancode/mini-oauth2:0.0.1 .

# Run the container
docker run -p 3000:3000 --rm --env-file .env daqiancode/mini-oauth2:0.0.1
docker push daqiancode/mini-oauth2:0.0.1

# rebuild
docker-compose down
docker volume rm mini-oauth2_postgres_data
docker-compose up --build


# create JWT key pair
python app/utils/jwts.py

# create apple login jwt
python app/utils/apple_utils.py -t team_id -c client_id -k key_id -p ./AuthKey_key_id.p8


## alembic
alembic init -t async alembic
alembic revision --autogenerate -m "first migration"
alembic upgrade head
```

