#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2014-1-23

@author: nttdocomo
'''
import web
from auth.models import User,RegistrationProfile
from db.models import DB_Session
from auth.forms import RegistrationForm

class AuthBase(object):
    def __init__(self):
        session = web.config.session
        if (not hasattr(session, 'login')) or session.login == 0:
            raise web.seeother('/login/')

class Admin(AuthBase):
    def GET(self):
        session = web.config.session
        render = web.template.render('templates')
        return render.admin(session.login)
        
class Login:
    def GET(self):
        render = web.template.render('templates')
        return render.login()
    def POST(self):
        session = web.config.session
        input = web.input()
        email, password = input.email, input.password
        db = DB_Session()
        query = db.query(User)
        user = query.filter(User.email == email).one()
        if user and user.validate_password(password):  
            session.login=1  
            session.privilege=user.privilege
            raise web.seeother('/admin/')
        else:
            raise web.seeother('/login/')

class Logout:
    def GET(self):
        web.seeother('/')

    def POST(self):
        session = web.config.session
        session.login = 0
        session.kill()
        raise web.seeother('/admin/')

class RegisterPage:
    def GET(self):
        f = RegistrationForm()
        render = web.template.render('templates')
        return render.register(f)
    def POST(self):
        f = RegistrationForm()
        if not f.validates():
            render = web.template.render('templates')
            return render.register(f)
        else:
            domain_override = web.ctx.host
            new_user = f.save(domain_override)
            render = web.template.render('templates')
            return render.register_success(new_user)

class Activate:
    def GET(self,activation_key):
        activation_key = activation_key.lower() # Normalize before trying anything with it.
        account = RegistrationProfile.activate_user(activation_key)