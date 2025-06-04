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
log = logging.getLogger(__name__)
router = APIRouter(tags=["Signup"])

@router.get("/signup/verify_code/captcha", description="signup page")
async def signup_verify_code_captcha():
    # generate captcha
    captcha_text = rand_num(6)
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
    # check email is not used
    if await Users().get_user_by_email(form.email):
        raise HTTPException(status_code=400, detail="email is already used")
    # send verify code to email
    try:
        code = rand_num(6)
        await redis_client.set(signup_prefix + 'verify_code/code/' + code, form.email, ex=60*10)
        await send_email(form.email, "Signup verify code", "your verify code is " + code)
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail="send email failed")
    return "OK"

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str
    verify_code: str

@router.post("/signup", description="signup")
async def signup(form: SignupRequest):
    # check verify_code is valid from redis
    if await redis_client.get(signup_prefix + 'verify_code/code/' + form.verify_code) != form.email:
        raise HTTPException(status_code=400, detail="invalid verification code")
    # check email is not used
    if await Users().get_user_by_email(form.email):
        raise HTTPException(status_code=400, detail="email is already used")
    # create user
    return await Users().signup(form.email, form.password, form.name)
    # return access_token

