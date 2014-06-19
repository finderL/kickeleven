#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2014-1-23

@author: nttdocomo
'''
import web
import datetime
from db.models import BaseModel,DB_Session
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import class_mapper
from sqlalchemy.types import CHAR, String, Date, DateTime, Boolean, Integer
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
    nationality = Column(String(30))
    continent_id = Column(TINYINT(3), ForeignKey('continent.id'))
    normal_flag = Column(CHAR(45))
    small_flag = Column(CHAR(45))
    logo = Column(CHAR(45))
    player = relationship("Player", backref="nationality")
    translation = relationship("NationTranslation", backref="nation", lazy="dynamic")
    club = relationship("Club", backref="nation", lazy="dynamic")
    city = relationship("City", backref="nation", lazy="dynamic")

    def get_tranlation(self):
        translation = self.translation.filter(NationTranslation.nation_id == self.id).filter(NationTranslation.language_code==self.get_language())
        return super(Nation, self).get_tranlation(translation)

class NationTranslation(Translation):
    __tablename__ = 'nationtranslation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(60)) # or Column(String(30))
    short_name = Column(String(30)) # or Column(String(30))
    nationality = Column(String(30))
    nation_id = Column(TINYINT(3), ForeignKey('nation.id'))

class City(TranslationModel):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True, autoincrement=True)
    city_name = Column(String(60))
    nation_id = Column(TINYINT(3), ForeignKey('nation.id'))
    capital = Column(Boolean, default=False)

    def to_api(self,admin=None):
        o = super(TranslationModel, self).to_api()
        o['nation'] = self.nation.to_api(admin)
        #del o['id']
        #del o['language_code']
        return o

    def get_tranlation(self):
        translation = self.translation.filter(CityTranslation.city_id == self.id).filter(CityTranslation.language_code==self.get_language())
        return super(City, self).get_tranlation(translation)

class CityTranslation(Translation):
    __tablename__ = 'citytranslation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    city_name = Column(String(60))
    city_id = Column(Integer, ForeignKey('city.id'))

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
    __tablename__ = 'team'

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer)
    type = Column(TINYINT(1),default=1) # 1 for nation, 2 for club
    team_name = Column(String(15))
    level = Column(TINYINT(2),default=1)
    teamplayer = relationship("TeamPlayer", backref="team", cascade='all, delete-orphan')
    
    def to_api(self,admin):
        db = DB_Session()
        o = super(Team, self).to_api()
        if o['type'] == 1:
            owner = db.query(Nation).get(o['owner_id'])
        else:
            owner = db.query(Club).get(o['owner_id'])
        try:
            o['owner'] = owner.to_api(admin)
        except Exception,e:
            o['owner'] = None
        db.close()
        return o

class TeamPlayer(ApiModel):
    __tablename__ = 'teamplayer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    player_id = Column(Integer, ForeignKey('player.id'))
    player = relationship("Player", backref="teamplayer")
    
    def to_api(self,admin):
        db = DB_Session()
        o = super(TeamPlayer, self).to_api()
        o['player'] = self.player.to_api(admin)
        o['team'] = self.team.to_api(admin)
        db.close()
        return o

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
    nation_id = Column(TINYINT(3), ForeignKey('nation.id'))
    height = Column(TINYINT(3))
    weight = Column(TINYINT(4))
    left_foot = Column(TINYINT(2))
    right_foot = Column(TINYINT(2))
    avatar = Column(CHAR(45))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    translation = relationship('PlayerTranslation', backref="player_ref", lazy="dynamic")
    player2position = relationship("PlayerPosition", backref="player_ref", cascade='all, delete-orphan')
    
    __mapper_args__ = {
        "order_by":"full_name"
    }
    
    def to_api(self, admin):
        o = super(Player, self).to_api(admin)
        nation = self.nationality
        try:
            o['nation'] = nation.to_api(admin)
        except Exception,e:
            o['nation'] = None
        if not o['avatar']:
            del o['avatar']
        del o['created_at']
        del o['updated_at']
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
    
    __mapper_args__ = {
        "order_by":["position_name","side","score"]
    }

class Match(ApiModel):
    __tablename__ = 'match'

    id = Column(Integer, primary_key=True, autoincrement=True)
    home_id = Column(Integer, ForeignKey(Team.id)) # or Column(String(30))
    away_id = Column(Integer, ForeignKey(Team.id)) # or Column(String(30))
    match_date = Column(DateTime)
    city_id = Column(Integer, ForeignKey(City.id))
    home_score = Column(TINYINT(2))
    away_score = Column(TINYINT(2))
    home_team = relationship("Team", foreign_keys="Match.home_id")
    away_team = relationship("Team", foreign_keys="Match.away_id")
    city = relationship("City", foreign_keys="Match.city_id")
    
    __mapper_args__ = {
        "order_by":["match_date"]
    }
    
    def to_api(self, admin):
        o = super(Match, self).to_api()
        o['home_team'] = self.home_team.to_api(admin)
        o['away_team'] = self.away_team.to_api(admin)
        o['city'] = self.city.to_api(admin)
        return o