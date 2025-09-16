from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from captcha.image import ImageCaptcha
from app.utils.rands import rand_num
from app.drivers.cache import redis_client
from app.routers.forms import signup_prefix
from app.services.users import Users
from app.drivers.emails import send_email
import logging
from typing import Annotated
from fastapi import Request, Query, Form
from fastapi.templating import Jinja2Templates
from app.utils.urls import encode_url_params
from app.services.clients import Clients
from app.routers.dependencies import templates, check_client
from app.routers.forms import set_code
from fastapi.responses import RedirectResponse
from app.utils.urls import set_url_params
from app.routers.forms import SigninRequest

log = logging.getLogger(__name__)
router = APIRouter(tags=["Signup"])

@router.get("/signup/verify_code/captcha", description="signup page")
async def signup_verify_code_captcha():
    # generate captcha
    captcha_text = rand_num(6)
    log.info("signup verify code captcha: %s", captcha_text)
    await redis_client.set(signup_prefix + 'verify_code/captcha/' + captcha_text, '1', ex=60*10)
    image = ImageCaptcha()
    data = image.generate(captcha_text)
    return StreamingResponse(data, media_type='image/png')

class SignupVerifyCodeRequest(BaseModel):
    email: str
    captcha: str

@router.post("/signup/verify_code", description="verify code")
async def signup_verify_code(form: SignupVerifyCodeRequest):
    # check verify_code is valid from redis
    if await redis_client.exists(signup_prefix + 'verify_code/captcha/' + form.captcha) == 0:
        raise HTTPException(status_code=400, detail="captcha is invalid")

    # don't send too frequently
    if await redis_client.ttl(signup_prefix + 'verify_code/code/' + form.email) > 0:
        raise HTTPException(status_code=400, detail="send verify code too frequently")

    # check email is not used
    if await Users().get_user_by_email(form.email):
        raise HTTPException(status_code=400, detail="email is already used")
    # send verify code to email
    try:
        code = rand_num(6)
        log.info("signup verify code: %s", code)
        await redis_client.set(signup_prefix + 'verify_code/code/' + form.email, code, ex=60*5)
        await send_email(form.email, "Signup verify code", "your verify code is " + code)
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail="send email failed")
    return "OK"

@router.get("/signup/verify_code/email/ttl", description="get email ttl")
async def signup_verify_code_email_ttl(email: str):
    ttl = await redis_client.ttl(signup_prefix + 'verify_code/code/' + email)
    if ttl == -1:
        ttl = 0
    return {"ttl": ttl}

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str
    verify_code: str

@router.post("/signup", description="signup")
async def signup(form: Annotated[SignupRequest, Form()], request: Request, query: Annotated[SigninRequest, Query()]):
    # check verify_code is valid from redis
    code = (await redis_client.get(signup_prefix + 'verify_code/code/' + form.email)).decode()
    if code != form.verify_code:
        raise HTTPException(status_code=400, detail="invalid verification code")
    # check email is not used
    if await Users().get_user_by_email(form.email):
        raise HTTPException(status_code=400, detail="email is already used")

    client = await check_client(query.client_id, query.redirect_uri)
    # create user
    user = await Users().signup(form.email, form.password, form.name, query.client_id)
    # return access_token

    code = await set_code({ **request.query_params }, user.id)
    # redirect to redirect_uri with code with GET
    return RedirectResponse(set_url_params(query.redirect_uri, {"code": code,'state':query.state} , remove_none=False), status_code=302)



class SignupPageRequest(BaseModel):
    client_id: str

@router.get("/signup", description="signup page")
async def signup_page(request: Request,qs: Annotated[SignupPageRequest, Query()]):
    client = await Clients().get(qs.client_id)
    if not client:
        raise HTTPException(status_code=400, detail="client not found")
    if client.disabled:
        raise HTTPException(status_code=400, detail="client disabled")
    return templates.TemplateResponse("signup.html", {'request': request,'query': encode_url_params({**request.query_params}), 'client': client})