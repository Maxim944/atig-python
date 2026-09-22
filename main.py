import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SITE_URL = os.getenv("SITE_URL", "http://localhost:8000")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️  WARNING: SUPABASE_URL and SUPABASE_KEY not set. Auth will not work.")

app = FastAPI(
    title="ATIG — Guardian Trusted Autonomous Intelligence",
    description="Автономная ИИ-экосистема для защиты жизни, управления активами и цифрового наследия",
)

# Templates & static
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def get_current_user(request: Request) -> Optional[dict]:
    """Get user from access_token cookie (simplified session)."""
    access_token = request.cookies.get("sb-access-token")
    refresh_token = request.cookies.get("sb-refresh-token")
    if not access_token:
        return None
    try:
        supabase = get_supabase()
        # Set session
        supabase.auth.set_session(access_token, refresh_token or "")
        user = supabase.auth.get_user()
        if user and user.user:
            return {
                "id": user.user.id,
                "email": user.user.email,
                "created_at": user.user.created_at,
            }
    except Exception:
        pass
    return None


def require_user(request: Request) -> dict:
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )
    return user


# ========== ROUTES ==========

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user, "page": "home"},
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "user": None, "page": "login", "sent": False, "error": None},
    )


@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, email: str = Form(...)):
    try:
        supabase = get_supabase()
        # Magic Link
        supabase.auth.sign_in_with_otp({
            "email": email,
            "options": {
                "email_redirect_to": f"{SITE_URL}/auth/callback",
            },
        })
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "user": None,
                "page": "login",
                "sent": True,
                "email": email,
                "error": None,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "user": None,
                "page": "login",
                "sent": False,
                "error": str(e) or "Ошибка отправки письма",
            },
        )


@app.get("/auth/callback")
async def auth_callback(request: Request, code: Optional[str] = None):
    """Handle magic link redirect. Supabase sends tokens in hash or code."""
    # For PKCE / code flow
    if code:
        try:
            supabase = get_supabase()
            session = supabase.auth.exchange_code_for_session({"auth_code": code})
            if session and session.session:
                response = RedirectResponse(url="/dashboard", status_code=303)
                response.set_cookie(
                    key="sb-access-token",
                    value=session.session.access_token,
                    httponly=True,
                    max_age=60 * 60 * 24 * 7,  # 7 days
                    samesite="lax",
                )
                if session.session.refresh_token:
                    response.set_cookie(
                        key="sb-refresh-token",
                        value=session.session.refresh_token,
                        httponly=True,
                        max_age=60 * 60 * 24 * 30,
                        samesite="lax",
                    )
                return response
        except Exception as e:
            print(f"Auth callback error: {e}")

    # Fallback: tokens may come in URL fragment (handled client-side)
    return templates.TemplateResponse(
        "callback.html",
        {"request": request, "user": None, "page": "callback"},
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "page": "dashboard"},
    )


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user, "page": "profile"},
    )


@app.get("/vault", response_class=HTMLResponse)
async def vault(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        "vault.html",
        {"request": request, "user": user, "page": "vault"},
    )


@app.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        "settings.html",
        {"request": request, "user": user, "page": "settings"},
    )


@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse(
        "privacy.html",
        {"request": request, "user": user, "page": "privacy"},
    )


@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse(
        "terms.html",
        {"request": request, "user": user, "page": "terms"},
    )


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("sb-access-token")
    response.delete_cookie("sb-refresh-token")
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
