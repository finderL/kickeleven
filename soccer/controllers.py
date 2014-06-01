'''
Created on 2014-1-23

@author: nttdocomo
'''
import web
from forms import RegistrationForm
from models import RegistrationProfile
import hashlib,random
from django.utils.hashcompat import md5_constructor, sha_constructor
from django.utils.encoding import smart_str
from string import ascii_letters, digits

def get_hexdigest(algorithm, salt, raw_password):
    """
    Returns a string of the hexdigest of the given plaintext password and salt
    using the given algorithm ('md5', 'sha1' or 'crypt').
    """
    raw_password, salt = smart_str(raw_password), smart_str(salt)
    if algorithm == 'crypt':
        try:
            import crypt
        except ImportError:
            raise ValueError('"crypt" password algorithm not supported in this environment')
        return crypt.crypt(raw_password, salt)

    if algorithm == 'md5':
        return md5_constructor(salt + raw_password).hexdigest()
    elif algorithm == 'sha1':
        return sha_constructor(salt + raw_password).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")

def gen_hash(password, salt=None, algorithm='sha512'):
    hash = hashlib.new(algorithm)
    hash.update(smart_str(password))
    if salt is None:
        salt = ''.join([random.choice(ascii_letters + digits) for _ in range(8)])
    hash.update(salt)
    return (algorithm, salt, hash.hexdigest())

def validate_password(raw_password,password):
    algo, salt, hsh = raw_password.split('$')
    return hsh == get_hexdigest(algo, salt, password)

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