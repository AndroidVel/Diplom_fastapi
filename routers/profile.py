from itertools import product

from fastapi import APIRouter, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from link_log_st import link_st, log_st

from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete
from fastapi.params import Depends
from backend.db_depends import get_db
from typing import Annotated

from models import User, Product


templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/info")
async def get_info(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
    link_st.__init__()
    link_st.profile_info = 'active'
    context = {
        'request': request,
        'title': 'Профиль',
        'pagename': 'Профиль',
        'logged': True,
        'LinkStatus': link_st,
        'email': db.scalar(select(User).where(User.email == log_st.email)).email,
        'first_name': db.scalar(select(User).where(User.email == log_st.email)).first_name,
        'last_name': db.scalar(select(User).where(User.email == log_st.email)).last_name,
    }
    return templates.TemplateResponse("profile_info.html", context)


@router.post("/info")
async def profile_info(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
    form = await request.form()
    email = form.get('email')
    first_name = form.get('first_name')
    last_name = form.get('last_name')
    db.execute(update(User).where(User.email == log_st.email).values(email=email, 
                                                              first_name=first_name, 
                                                              last_name=last_name))
    db.commit()

    context = {
        'request': request,
        'title': 'Профиль',
        'pagename': 'Профиль',
        'logged': True,
        'LinkStatus': link_st,
        'email': db.scalar(select(User).where(User.email == log_st.email)).email,
        'first_name': db.scalar(select(User).where(User.email == log_st.email)).first_name,
        'last_name': db.scalar(select(User).where(User.email == log_st.email)).last_name,
    }
    return templates.TemplateResponse("profile_info.html", context)


@router.get("/cart")
async def get_cart(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
    products = db.query(Product).join(Product.user).filter(User.email == log_st.email).all()
    # Another solution: db.query(Product).join(User.product).where(User.email == log_st.email).all()

    link_st.__init__()
    link_st.cart = 'active'
    context = {
        'request': request,
        'title': 'Корзина',
        'pagename': 'Корзина',
        'logged': True,
        'LinkStatus': link_st,
        'total_price': 0,
        'products': '',
    }
    if products:
        context['products'] = products
        for product in products:
            context['total_price'] += product.price

    return templates.TemplateResponse("cart.html", context)


@router.post("/cart/buy")
async def buy_products(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
    user = db.query(User).filter(User.email == log_st.email).first()
    user.product.clear()
    db.commit()
    context = {
        'request': request,
        'title': 'Корзина',
        'pagename': 'Корзина',
        'logged': True,
        'LinkStatus': link_st,
        'total_price': 0,
        'products': '',
    }
    return templates.TemplateResponse("cart.html", context)


@router.post("/cart/remove_product")
async def remove_product(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
    form = await request.form()
    user = db.query(User).filter(User.email == log_st.email).first()
    product_ = db.query(Product).filter(Product.name == form.get('card_button')).first()


    user.product.remove(product_)
    db.add(user)
    db.commit()

    context = {
        'request': request,
        'title': 'Корзина',
        'pagename': 'Корзина',
        'logged': True,
        'LinkStatus': link_st,
        'total_price': 0,
        'products': ''
    }
    products = db.scalars(select(Product).join(User.product).where(User.email == log_st.email)).all()
    if products:
        context['products'] = products
        for product in products:
            context['total_price'] += product.price
    return templates.TemplateResponse("cart.html", context)


@router.get("/log_out")
async def get_log_out(request: Request) -> HTMLResponse:
    link_st.__init__()
    link_st.home = 'active'
    log_st.log_out()
    context = {
        'request': request,
        'title': 'Главная',
        'pagename': 'Булочная',
        'logged': log_st.is_logged_in,
        'LinkStatus': link_st,
    }
    return templates.TemplateResponse("home.html", context)
