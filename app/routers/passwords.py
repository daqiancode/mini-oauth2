from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from captcha.image import ImageCaptcha
from app.utils.rands import rand_num
from app.drivers.cache import redis_client
from app.routers.forms import redis_prefix
from app.services.users import Users
from app.drivers.emails import send_email
import logging
from app.utils.rands import rand_str
log = logging.getLogger(__name__)
router = APIRouter(tags=["Password reset"])

password_prefix = redis_prefix + "password/"


@router.get("/captcha" , description="reset password page")
async def reset_password_captcha():
    # generate captcha
    captcha_text = rand_num(6)
    await redis_client.set(password_prefix + 'verify_code/captcha/' + captcha_text, '1', ex=60*10)
    image = ImageCaptcha()
    data = image.generate(captcha_text)
    return StreamingResponse(data, media_type='image/png')

class ResetPasswordVerifyCodeRequest(BaseModel):
    email: str
    captcha: str

@router.post("/verify_code")
async def reset_password_verify_code(form: ResetPasswordVerifyCodeRequest):
    # check verify_code is valid from redis
    if await redis_client.get(password_prefix + 'verify_code/captcha/' + form.captcha) != '1':
        raise HTTPException(status_code=400, detail="Invalid captcha")
    # check email is valid
    if not await Users().get(form.email):
        raise HTTPException(status_code=400, detail="Invalid email")
    # send email
    code = rand_str(6)
    await send_email(form.email, "Reset Password", "Your reset password code is <b>" + code + "</b>. Please use this code to reset your password in 10 minutes.")
    await redis_client.set(password_prefix + 'verify_code/email/' + code, form.email, ex=60*10)
    return {"message": "Email sent"}
    

class ResetPasswordRequest(BaseModel):
    email: str
    captcha: str
    verify_code: str
    password: str
    repassword: str

@router.post("/")
async def reset_password(form: ResetPasswordRequest):
    # check verify_code is valid from redis
    if await redis_client.get(password_prefix + 'verify_code/email/' + form.verify_code) != form.email:
        raise HTTPException(status_code=400, detail="Invalid verify code")
    # check email is valid
    if not await Users().get(form.email):
        raise HTTPException(status_code=400, detail="Invalid email")
    # check password is valid
    if form.password != form.repassword:
        raise HTTPException(status_code=400, detail="repassword not match")
    # update password
    await Users().update_password(form.email, form.password)
    return {"message": "Password updated"}
    


