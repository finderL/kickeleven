# -*- coding: utf-8 -*-
'''
Created on 2014-1-23

@author: nttdocomo
'''
import web
import datetime
import utils
import random
import sha
import re
import settings
from django.utils.hashcompat import md5_constructor, sha_constructor
from django.utils.encoding import smart_str
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.orm import sessionmaker, class_mapper
from sqlalchemy.types import CHAR, String, Date, DateTime, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base

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

def parseAcceptLanguage(acceptLanguage):
    languages = acceptLanguage.split(",")
    return languages[0].lower()

DB_CONNECT_STRING = 'mysql+mysqldb://root@localhost/kickeleven?charset=utf8'
engine = create_engine(DB_CONNECT_STRING, echo=True)
DB_Session = sessionmaker(bind=engine,expire_on_commit=False)

# db = web.database(dbn='mysql', user='root', pw='', db='kickeleven')
# db.supports_multiple_insert = True

BaseModel = declarative_base()

def _to_api(v):
#    if hasattr(v, 'to_api'):
#        v = v.to_api()
    if isinstance(v, type([])):
        v = [_to_api(x) for x in v]
#    elif isinstance(v, datetime.datetime):
#        v = str(v)
    elif isinstance(v, datetime.date):
        # Convert date/datetime to ms-since-epoch ("new Date()").
        if isinstance(v, datetime.datetime):
            epoch = datetime.datetime(1970, 1, 1)
            # ms = time.mktime(value.utctimetuple())*1000
        else:
            epoch = datetime.date(1970, 1, 1)
            # ms = time.mktime(value.timetuple())*1000
        diff = v - epoch
        ms = (diff.days * 24 * 3600 + diff.seconds) * 1000
        ms += getattr(v, 'microseconds', 0)
        v = int(ms)
    elif isinstance(v, type({})):
        v = dict([(key, _to_api(value)) for (key, value) in v.iteritems()])
    return v

class ApiModel(BaseModel):
    __abstract__ = True
    __table_args__ = { # 可以省掉子类的 __table_args__ 了
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    
    def to_api(self):
        o = {}
        columns = [c.key for c in class_mapper(self.__class__).columns]
        for prop in columns:
            value = getattr(self, prop)
            o[prop] = _to_api(value)
        return o

class Translation(ApiModel):
    __abstract__ = True
    language_code = Column(CHAR(6))
    #version = db.IntegerProperty(verbose_name="版本", default=1)
#     active = db.BooleanProperty(verbose_name="是否激活", default=True)

    def to_api(self):
        o = super(Translation, self).to_api()
        #del o['id']
        #del o['language_code']
        return o

class TranslationModel(ApiModel):
    __abstract__ = True  

    def to_api(self, admin):
        o = super(TranslationModel, self).to_api()
        if admin is None:
            translation = self.get_tranlation()
            if translation is not None:
                id = o['id']
                o.update(translation.to_api())
                o['id'] = id
        return o
    
    def get_language(self):
        return parseAcceptLanguage(web.ctx.env['HTTP_ACCEPT_LANGUAGE'])
    
    def get_tranlation(self,translation):
        session = DB_Session()
        if translation is not None:
            try:
                translation = translation.one()
            except Exception:
                translation = None
        session.close()
        return translation

class Session(BaseModel):
    '''webpy的session表'''
    __tablename__ = 'sessions'
    
    session_id = Column(String(128), primary_key=True)
    atime = Column(DateTime, nullable=False, default=datetime.datetime.now)
    data = Column(Text, nullable=True)

class SQLAStore(web.session.Store):
    '''webpy的session存储在sqlalchemy中的接口'''
    def __init__(self):
        self.table = Session.__table__
    
    def __contains__(self, key):
        db = DB_Session()
        session = db.execute(self.table.select(self.table.c.session_id==key)).fetchone()
        db.close()
        return bool(session)
    
    def __getitem__(self, key):
        db = DB_Session()
        s = db.execute(
            self.table.select(self.table.c.session_id==key)).fetchone()
        if s is None:
            raise KeyError
        else:
            db.execute(self.table.update().values(
                atime=datetime.datetime.now()).where(self.table.c.session_id==key))
            db.close()
            return self.decode(s[self.table.c.data])
    
    def __setitem__(self, key, value):
        db = DB_Session()
        pickled = self.encode(value)
        if key in self:
            db.execute(self.table.update().values(
                data=pickled).where(self.table.c.session_id==key))
        else:
            db.execute(self.table.insert().values(
                session_id=key, data=pickled))
        db.close()
    
    def __delitem__(self, key):
        db = DB_Session()
        db.execute(self.table.delete(self.table.c.session_id==key))
        db.close()
    
    def cleanup(self, timeout):
        db = DB_Session()
        timeout = datetime.timedelta(timeout / (24. * 60 * 60))
        last_allowed_time = datetime.datetime.now() - timeout
        db.execute(self.table.delete(self.table.c.atime<last_allowed_time))
        db.close()

UNUSABLE_PASSWORD = '!' # This will never be a valid hash
SHA1_RE = re.compile('^[a-f0-9]{40}$')

class User(ApiModel):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_joined = Column(DateTime, nullable=False, default=datetime.datetime.now)
    username = Column(String(60), unique=True) # or Column(String(30))
    email = Column(String(60))
    password = Column(CHAR(60),default=UNUSABLE_PASSWORD)
    is_active = Column(Boolean, default=True)

    def set_password(self, raw_password):
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)

class RegistrationProfile(BaseModel):
    __tablename__ = 'registrationprofile'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    activation_key = Column(CHAR(41), unique=True)
    
    user = relationship(User)
    
    @classmethod
    def activate_user(cls, activation_key):
        """
        Validate an activation key and activate the corresponding
        ``User`` if valid.
        
        If the key is valid and has not expired, return the ``User``
        after activating.
        
        If the key is not valid or has expired, return ``False``.
        
        If the key is valid but the ``User`` is already active,
        return ``False``.
        
        To prevent reactivation of an account which has been
        deactivated by site administrators, the activation key is
        reset to the string constant ``RegistrationProfile.ACTIVATED``
        after successful activation.

        To execute customized logic when a ``User`` is activated,
        connect a function to the signal
        ``registration.signals.user_activated``; this signal will be
        sent (with the ``User`` as the value of the keyword argument
        ``user``) after a successful activation.
        
        """
        #from registration.signals import user_activated
        
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        db = DB_Session()
        if SHA1_RE.search(activation_key):
            query = db.query(RegistrationProfile)
            profile = query.filter(RegistrationProfile.activation_key == activation_key).one()
            if not profile:
                return False
            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.put()
                profile.activation_key = RegistrationProfile.ACTIVATED
                profile.put()
                #user_activated.send(sender=self.model, user=user)
                return user
        return False
    
    @classmethod
    def create_inactive_user(cls,username, password, email, domain_override="", 
                             send_email=True):
        new_user = User(username=username, email=email, is_active=False)
        new_user.set_password(password)
        db = DB_Session()
        db.add(new_user)
        db.flush()
        db.refresh(new_user)
        db.commit()
        
        registration_profile = cls.create_profile(new_user)
        if send_email:
            current_site = domain_override
#            current_site = Site.objects.get_current()
            
            subject = web.template.render('templates').activation_email_subject({ 'site': current_site,'activation_key': registration_profile.activation_key })
#             render_to_string('registration/activation_email_subject.txt',
#                                        { 'site': current_site,'activation_key': registration_profile.activation_key })
            # Email subject *must not* contain newlines
            subject = ''.join(subject.__str__().splitlines())
            
            message = web.template.render('templates').activation_email({ 'activation_key': registration_profile.activation_key,
                                         'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                         'site': current_site })
#             render_to_string('registration/activation_email.txt',
#                                        { 'activation_key': registration_profile.activation_key,
#                                          'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
#                                          'site': current_site })
            
            web.sendmail(settings.DEFAULT_FROM_EMAIL, new_user.email,subject, message)
        db.close()
        return new_user
    
    @classmethod
    def create_profile(self, user):
        """
        Create a ``RegistrationProfile`` for a given
        ``User``, and return the ``RegistrationProfile``.
        
        The activation key for the ``RegistrationProfile`` will be a
        SHA1 hash, generated from a combination of the ``User``'s
        username and a random salt.
        
        """
        salt = sha.new(str(random.random())).hexdigest()[:5]
        activation_key = sha.new(salt+user.username).hexdigest()
#        prepend "key_" to the key_name, because key_names can't start with numbers
        registrationprofile = RegistrationProfile(user=user, activation_key=activation_key)
        db = DB_Session()
        db.add(registrationprofile)
        db.flush()
        db.refresh(registrationprofile)
        db.commit()
        db.close()
        return registrationprofile
    
    def activation_key_expired(self):
        """
        Determine whether this ``RegistrationProfile``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired.
        
        Key expiration is determined by a two-step process:
        
        1. If the user has already activated, the key will have been
           reset to the string constant ``ACTIVATED``. Re-activating
           is not permitted, and so this method returns ``True`` in
           this case.

        2. Otherwise, the date the user signed up is incremented by
           the number of days specified in the setting
           ``ACCOUNT_ACTIVATION_DAYS`` (which should be the number of
           days after signup during which a user is allowed to
           activate their account); if the result is less than or
           equal to the current date, the key has expired and this
           method returns ``True``.
        
        """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == RegistrationProfile.ACTIVATED or \
               (self.user.date_joined + expiration_date <= datetime.datetime.now())

    activation_key_expired.boolean = True

class Continent(ApiModel):
    __tablename__ = 'continent'

    id = Column(TINYINT(1), primary_key=True, autoincrement=True)
    name = Column(String(14)) # or Column(String(30))
    nation = relationship("Nation")

class Nation(TranslationModel):
    __tablename__ = 'nation'

    id = Column(TINYINT(1), primary_key=True, autoincrement=True)
    full_name = Column(String(60)) # or Column(String(30))
    short_name = Column(String(30)) # or Column(String(30))
    capital_city = Column(String(60))
    nationality = Column(String(30))
    continent = Column(TINYINT(3), ForeignKey('continent.id'))
    normal_flag = Column(CHAR(45))
    small_flag = Column(CHAR(45))
    player = relationship("Player", backref="nationality")
    translation = relationship("NationTranslation", backref="nation_ref", lazy="dynamic")
    club = relationship("Club", backref="nation_ref", lazy="dynamic")
    team = relationship('NationTeam', backref="nation_ref", lazy="dynamic")

    def get_tranlation(self):
        translation = self.translation.filter(NationTranslation.nation == self.id).filter(NationTranslation.language_code==self.get_language())
        return super(Nation, self).get_tranlation(translation)

class NationTranslation(Translation):
    __tablename__ = 'nationtranslation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(60)) # or Column(String(30))
    short_name = Column(String(30)) # or Column(String(30))
    capital_city = Column(String(60))
    nationality = Column(String(30))
    nation = Column(TINYINT(3), ForeignKey('nation.id'))

class Club(TranslationModel):
    __tablename__ = 'club'

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_name = Column(String(60)) # or Column(String(30))
    nickname = Column(String(30)) # or Column(String(30))
    year_founded = Column(Date())
    nation = Column(TINYINT(3), ForeignKey('nation.id'))
    normal_logo = Column(CHAR(45))
    small_logo = Column(CHAR(45))
    home_kit = Column(CHAR(45))
    away_kit = Column(CHAR(45))
    third_kit = Column(CHAR(45))
    team = relationship('ClubTeam', backref="club_ref", lazy="dynamic")
    translation = relationship('ClubTranslation', backref="club_ref", lazy="dynamic")
    
    def to_api(self, admin):
        db = DB_Session()
        o = super(Club, self).to_api(admin)
        nation = self.nation_ref
        try:
            o['nation'] = nation.to_api(admin)
        except Exception,e:
            o['nation'] = None
        db.close()
        return o

    def get_tranlation(self):
        translation = self.translation.filter(ClubTranslation.club == self.id).filter(ClubTranslation.language_code==self.get_language())
        return super(Club, self).get_tranlation(translation)

class ClubTranslation(Translation):
    __tablename__ = 'clubtranslation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_name = Column(String(60)) # or Column(String(30))
    nickname = Column(String(30)) # or Column(String(30))
    club = Column(TINYINT(10), ForeignKey('club.id'))

class Team(ApiModel):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String(15))
    level = Column(TINYINT(2),default=1)

class ClubTeam(Team):
    __tablename__ = 'clubteam'

    club = Column(Integer, ForeignKey('club.id')) # or Column(String(30))
    team2player = relationship("ClubTeamPlayer", backref="team_ref", cascade='all, delete-orphan')
    
    def to_api(self,admin):
        db = DB_Session()
        o = super(ClubTeam, self).to_api()
        club = self.club_ref
        try:
            o['club'] = club.to_api(admin)
        except Exception,e:
            o['club'] = None
        db.close()
        return o

class NationTeam(Team):
    __tablename__ = 'nationteam'

    nation = Column(Integer, ForeignKey('nation.id')) # or Column(String(30))
    team2player = relationship("NationTeamPlayer", backref="team_ref", cascade='all, delete-orphan')
    
    def to_api(self,admin):
        db = DB_Session()
        o = super(NationTeam, self).to_api()
        nation = self.nation_ref
        try:
            o['nation'] = nation.to_api(admin)
        except Exception,e:
            o['nation'] = None
        db.close()
        return o

class TeamPlayer(BaseModel):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

class ClubTeamPlayer(TeamPlayer):
    __tablename__ = 'clubteam2player'

    team = Column(Integer, ForeignKey('clubteam.id'), primary_key=True)
    player = Column(Integer, ForeignKey('player.id'), primary_key=True)
    player_child = relationship("Player", backref="clubteam2player")

class NationTeamPlayer(TeamPlayer):
    __tablename__ = 'nationteam2player'

    team = Column(Integer, ForeignKey('nationteam.id'), primary_key=True)
    player = Column(Integer, ForeignKey('player.id'), primary_key=True)
    player_child = relationship("Player", backref="nationteam2player")

class PlayerPosition(BaseModel):
    __tablename__ = 'player2position'

    player = Column(Integer, ForeignKey('player.id'), primary_key=True)
    position = Column(Integer, ForeignKey('position.id'), primary_key=True)
    position_child = relationship("Position", backref="player2position")

class Player(TranslationModel):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(60)) # or Column(String(30))
    short_name = Column(String(30)) # or Column(String(30))
    date_of_birth = Column(Date())
    nation = Column(TINYINT(3), ForeignKey('nation.id'))
    height = Column(TINYINT(3))
    weight = Column(TINYINT(4))
    left_foot = Column(TINYINT(2))
    right_foot = Column(TINYINT(2))
    avatar = Column(CHAR(45))
    translation = relationship('PlayerTranslation', backref="player_ref", lazy="dynamic")
    player2position = relationship("PlayerPosition", backref="player_ref", cascade='all, delete-orphan')
    
    __mapper_args__ = {
        "order_by":"full_name"
    }
    
    def to_api(self, admin):
        session = DB_Session()
        o = super(Player, self).to_api(admin)
        nation = self.nationality
        try:
            o['nation'] = nation.to_api(admin)
        except Exception,e:
            o['nation'] = None
        session.close()
        return o

    def get_tranlation(self):
        translation = self.translation.filter(PlayerTranslation.player == self.id).filter(PlayerTranslation.language_code==self.get_language())
        return super(Player, self).get_tranlation(translation)

class PlayerTranslation(Translation):
    __tablename__ = 'playertranslation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(60)) # or Column(String(30))
    short_name = Column(String(30)) # or Column(String(30))
    player = Column(TINYINT(3), ForeignKey('player.id'))

class Position(ApiModel):
    __tablename__ = 'position'

    id = Column(Integer, primary_key=True, autoincrement=True)
    position_name = Column(TINYINT(2)) # or Column(String(30))
    side = Column(TINYINT(1)) # or Column(String(30))
    score = Column(TINYINT(2))