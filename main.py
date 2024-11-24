from sqlalchemy.exc import IntegrityError

from fastapi import FastAPI, status, HTTPException, Request
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from backend.db_depends import get_db
from typing import Annotated
from fastapi.templating import Jinja2Templates
from routers import profile
from link_log_st import link_st, log_st
from models import User, Product
from schemas import CreateProduct
from sqlalchemy import insert, select


app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def main_page(request: Request) -> HTMLResponse:
    link_st.__init__()
    link_st.home = 'active'
    context = {
        'request': request,
        'title': 'Главная',
        'pagename': 'Булочная - Теплый Хлеб',
        'logged': log_st.is_logged_in,
        'LinkStatus': link_st,
    }
    return templates.TemplateResponse("home.html", context)


@app.get("/products")
async def get_products(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
    link_st.__init__()
    link_st.products = 'active'
    products = db.scalars(select(Product)).all()

    context = {
        'request': request,
        'title': 'Продукты',
        'pagename': 'Продукты',
        'logged': log_st.is_logged_in,
        'LinkStatus': link_st,
        'products': products,
        'is_logged_in': log_st.is_logged_in,
        'search': ''
    }
    return templates.TemplateResponse("products.html", context)


@app.get("/products/search")
async def get_products_search(request: Request, db: Annotated[Session, Depends(get_db)], search) -> HTMLResponse:
    link_st.__init__()
    link_st.products = 'active'
    if search is None:
        await get_products(request,db)
    else:
        products = db.scalars(select(Product).where(Product.name.icontains(search.lower()))).all()
        context = {
            'request': request,
            'title': 'Продукты',
            'pagename': 'Продукты',
            'logged': log_st.is_logged_in,
            'LinkStatus': link_st,
            'products': products,
            'is_logged_in': log_st.is_logged_in,
            'search': search,
        }
        return templates.TemplateResponse("products.html", context)


@app.post("/products")
async def create_product(db: Annotated[Session, Depends(get_db)], create_product: CreateProduct):
    product = db.scalar(select(Product).where(Product.name == create_product.name))
    if product is None:
        db.execute(insert(Product).values(name=create_product.name,
                                          weight=create_product.weight,
                                          price=create_product.price,
                                          image_url=create_product.image_url,
                                          ))
        db.commit()
        return {'status_code': status.HTTP_201_CREATED,
                'add_product': 'Successful'}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Product already exists')


@app.post("/products/add_to_cart")
async def add_product_to_cart(request: Request, db: Annotated[Session, Depends(get_db)]):
    form = await request.form()
    try:
        product = db.query(Product).filter(Product.name == form.get('card_button')).first()
        user = db.query(User).filter(User.email == log_st.email).first()

        product.user.append(user)
        user.product.append(product)
        db.commit()
    except Exception as e:
        print(e)

    finally:
        products = db.scalars(select(Product)).all()
        context = {
            'request': request,
            'title': 'Продукты',
            'pagename': 'Продукты',
            'logged': log_st.is_logged_in,
            'LinkStatus': link_st,
            'products': products,
            'is_logged_in': log_st.is_logged_in,
        }
        return templates.TemplateResponse("products.html", context)
    


@app.get("/about")
async def get_about(request: Request) -> HTMLResponse:
    link_st.__init__()
    link_st.about = 'active'
    context = {
        'request': request,
        'title': 'Информация',
        'pagename': 'Информация',
        'logged': log_st.is_logged_in,
        'LinkStatus': link_st,
    }
    return templates.TemplateResponse("about.html", context)


@app.get("/log_in")
async def get_log_in(request: Request) -> HTMLResponse:
    link_st.__init__()
    link_st.log_in = 'active'
    context = {
        'request': request,
        'title': 'Войти',
        'pagename': 'Войти',
        'logged': False,
        'LinkStatus': link_st,
        'error': '',
    }
    return templates.TemplateResponse("log_in.html", context)


@app.post("/log_in")
async def log_in(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
    form = await request.form()
    email = form.get('email')
    password = form.get('password')
    if db.scalar(select(User).where(User.email == email)) and password == db.scalar(select(User).where(User.email == email)).password:
        link_st.__init__()
        link_st.home = 'active'
        log_st.log_in(email)
        context = {
            'request': request,
            'title': 'Главная',
            'pagename': 'Булочная - Теплый Хлеб',
            'logged': log_st.is_logged_in,
            'LinkStatus': link_st,
        }
        return templates.TemplateResponse("home.html", context)

    else:
        link_st.__init__()
        link_st.log_in = 'active'
        context = {
            'request': request,
            'title': 'Войти',
            'pagename': 'Войти',
            'logged': False,
            'LinkStatus': link_st,
            'error': 'Неверный логин или пароль',
        }
        return templates.TemplateResponse("log_in.html", context)
        



@app.get("/sign_up")
async def get_sign_up(request: Request) -> HTMLResponse:
    link_st.__init__()
    link_st.sign_up = 'active'
    context = {
        'request': request,
        'title': 'Регистрация',
        'pagename': 'Регистрация',
        'logged': False,
        'LinkStatus': link_st,
        'error': ''
    }
    return templates.TemplateResponse("sign_up.html", context)


@app.post("/sign_up")
async def sign_up(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
    form = await request.form()
    email = form.get('email')
    first_name = form.get('first_name')
    last_name = form.get('last_name')
    password = form.get('password')
    password_repeat = form.get('password_repeat')
    def fill_inputs(eml, firstname, lastname, psw, psw_repeat):
        context['email'] = eml
        context['first_name'] = firstname
        context['last_name'] = lastname
        context['password'] = psw
        context['repeat_password'] = psw_repeat

    context = {
        'request': request,
        'title': 'Регистрация',
        'pagename': 'Регистрация',
        'logged': False,
        'LinkStatus': link_st
    }

    if password != password_repeat:
        context['error'] = 'Пароли не совпадают'
        fill_inputs(email, first_name, last_name, password, password_repeat)
    else:
        try:
            db.execute(insert(User).values(email=email, first_name=first_name, last_name=last_name, password=password))
            db.commit()
            link_st.__init__()
            link_st.home = 'active'
            log_st.log_in()
            context = {
                'request': request,
                'title': 'Главная',
                'pagename': 'Булочная - Теплый Хлеб',
                'logged': log_st.is_logged_in,
                'LinkStatus': link_st,
            }
            return templates.TemplateResponse("home.html", context)
        except IntegrityError:
            context['error'] = 'Пользователь с таким email уже существует'
            fill_inputs(email, first_name, last_name, password, password_repeat)

    return templates.TemplateResponse("sign_up.html", context)


app.include_router(profile.router)
