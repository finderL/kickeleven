#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2014-1-23

@author: nttdocomo
'''
import web
import datetime
from db.models import BaseModel,DB_Session,sql_session
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import class_mapper
from sqlalchemy.types import CHAR, String, Date, DateTime, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT

def parseAcceptLanguage(acceptLanguage):
    languages = acceptLanguage.split(",")
    return languages[0].lower()

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
    club = relationship("Club", backref="nation", lazy="dynamic")
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
    nation_id = Column(TINYINT(3), ForeignKey('nation.id'))
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
        nation = self.nation
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

    team_id = Column(Integer, ForeignKey('clubteam.id'), primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'), primary_key=True)
    player = relationship("Player", backref="clubteam2player")

class NationTeamPlayer(TeamPlayer):
    __tablename__ = 'nationteam2player'

    team_id = Column(Integer, ForeignKey('nationteam.id'), primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'), primary_key=True)
    player = relationship("Player", backref="nationteam2player")

class PlayerPosition(BaseModel):
    __tablename__ = 'player2position'

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('player.id'), primary_key=True)
    position_id = Column(Integer, ForeignKey('position.id'), primary_key=True)
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