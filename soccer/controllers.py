'''
Created on 2014-1-23

@author: nttdocomo
'''
import web
from forms import RegistrationForm
from models import RegistrationProfile

class hello:
    def GET(self, name):
        render = web.template.render('templates')
        if not name:
            name = 'World'
        return render.index(name)

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