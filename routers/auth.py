import json
from typing import Optional, Dict
from fastapi import APIRouter, Depends, Form
from dependencies import ClientStorage, get_clients
from instagrapi.exceptions import (
    ChallengeRequired,
    SelectContactPointRecoveryForm, RecaptchaChallengeForm,
)
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}}
)

def challenge_code_handler(username, choice, code):
    return 1234

def handle_exception(client, e):
    if isinstance(e, ChallengeRequired):
        client.challenge_resolve(client.last_json)

    return True

@router.post("/login")
async def auth_login(username: str = Form(...),
                     password: str = Form(...),
                     verification_code: Optional[str] = Form(""),
                     proxy: Optional[str] = Form(""),
                     locale: Optional[str] = Form(""),
                     timezone: Optional[str] = Form(""),
                     clients: ClientStorage = Depends(get_clients)) -> str:
    """Login by username and password with 2FA
    """
    cl = clients.client()
    cl.challenge_code_handler = challenge_code_handler
    if proxy != "":
        cl.set_proxy(proxy)

    if locale != "":
        cl.set_locale(locale)

    if timezone != "":
        cl.set_timezone_offset(timezone)

    result = cl.login(
        username,
        password,
        verification_code=verification_code
    )
    if result:
        clients.set(cl)
        return cl.sessionid
    return result

@router.post("/loginwithcode")
async def auth_login(username: str = Form(...),
                     password: str = Form(...),
                     code: str = Form(...),
                     verification_code: Optional[str] = Form(""),
                     proxy: Optional[str] = Form(""),
                     locale: Optional[str] = Form(""),
                     timezone: Optional[str] = Form(""),
                     clients: ClientStorage = Depends(get_clients)) -> str:
    """Login by username and password with 2FA
    """
    cl = clients.client()
    cl.handle_exception = handle_exception
    if proxy != "":
        cl.set_proxy(proxy)

    if locale != "":
        cl.set_locale(locale)

    if timezone != "":
        cl.set_timezone_offset(timezone)

    result = cl.login(
        username,
        password,
        verification_code=verification_code,
        code=code
    )
    if result:
        clients.set(cl)
        return cl.sessionid
    return result

@router.post("/relogin")
async def auth_relogin(sessionid: str = Form(...),
                       clients: ClientStorage = Depends(get_clients)) -> str:
    """Relogin by username and password (with clean cookies)
    """
    cl = clients.get(sessionid)
    result = cl.relogin()
    return result


@router.get("/settings/get")
async def settings_get(sessionid: str,
                   clients: ClientStorage = Depends(get_clients)) -> Dict:
    """Get client's settings
    """
    cl = clients.get(sessionid)
    return cl.get_settings()


@router.post("/settings/set")
async def settings_set(settings: str = Form(...),
                       sessionid: Optional[str] = Form(""),
                       clients: ClientStorage = Depends(get_clients)) -> str:
    """Set client's settings
    """
    if sessionid != "":
        cl = clients.get(sessionid)
    else:
        cl = clients.client()
    cl.set_settings(json.loads(settings))
    cl.expose()
    clients.set(cl)
    return cl.sessionid

@router.get("/timeline_feed")
async def timeline_feed(sessionid: str,
                   clients: ClientStorage = Depends(get_clients)) -> Dict:
    """Get your timeline feed
    """
    cl = clients.get(sessionid)
    return cl.get_timeline_feed()