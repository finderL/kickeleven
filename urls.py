# -*- coding: utf-8 -*-
'''
Created on 2014-1-23

@author: nttdocomo
'''
import web
from auth.controllers import *
from api.urls import app_api
from sessions.models import Session, SQLAStore

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

global session
if web.config.get('session') is None:
    web.config.session = session = Session(app, SQLAStore())
else:
    session = web.config.session

if __name__ == "__main__":
    app.run()