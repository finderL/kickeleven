# -*- coding: utf-8 -*-
'''
Created on 2014-1-23

@author: nttdocomo
'''
import web
from soccer.controllers import hello, RegisterPage, validate_password
from api.urls import app_api
from soccer.models import SQLAStore, Session, DB_Session, RegistrationProfile, User

web.config.smtp_server = 'smtp.gmail.com'
web.config.smtp_port = 587
web.config.smtp_username = 'adam.au@guohead.com'
web.config.smtp_password = 'ouyi709394'
web.config.smtp_starttls = True

urls = (
    '/api', app_api,
    '/register/', 'RegisterPage',
    '/activate/(\w+)/','Activate',
    '/admin/', 'Admin',
    '/admin/login/', 'Login',
    '/(.*)', 'hello'
)
app = web.application(urls, locals())

# session
global session
if web.config.get('session') is None:
    web.config.session = session = Session(app, SQLAStore())
else:
    session = web.config.session

class AuthBase:
    def __init__(self):
        if (not hasattr(session, 'login')) or session.login == 0:
            raise web.seeother('/admin/login/',absolute=True)

class Admin(AuthBase):
    def GET(self):
        render = web.template.render('templates')
        return render.admin(session.login)
        
class Login:
    def GET(self):
        render = web.template.render('templates')
        return render.login()
    def POST(self):
        input = web.input()
        email, password = input.email, input.password
        db = DB_Session()
        query = db.query(User)
        user = query.filter(User.email == email).one()
        if user and validate_password(user.password, password):  
            session.login=1  
            session.privilege=user.privilege
            raise web.seeother('/admin/')
        else:
            raise web.seeother('/admin/login/')

if __name__ == "__main__":
    app.run()