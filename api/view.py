#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2011-9-12

@author: nttdocomo
'''
import datetime, json, web, urlparse, StringIO, hashlib
from PIL import Image
from sqlalchemy.orm import class_mapper
from soccer.models import DB_Session, Continent, _to_api, Player, PlayerTranslation, Nation, NationTranslation, Team, TeamPlayer, Position, PlayerPosition, Club, ClubTranslation, City, Match
from settings import TEMP_DIR
from sqlalchemy.types import String

PAGE_ARGS = ('limit','p')

def paging(query, limit=None, p=None):
    if limit is not None:
        limit = int(limit)
        offset = (int(p) - 1)*limit
        return query.offset(offset).limit(limit)
    return query

class Base:
    def render_api_response(self, rv, format="json", servertime=None):
        o = {"status": "ok"}
        # TODO make this into something real
        rv = {"rv": rv.to_api()}
        o.update(rv)

        web.header('Content-Type', 'application/json')
        return json.dumps(o)

class Players(Base):
    def GET(self):
        db = DB_Session()
        query = db.query(Player)
        player = query
        count = player.count()
        n = ResultWrapper(player, player=[v.to_api(1) for v in player],count=count)
        db.close()
        return self.render_api_response(n)        

class ExtendedEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.date):   
            # Convert date/datetime to ms-since-epoch ("new Date()").
            if isinstance(o, datetime.datetime):
                epoch = datetime.datetime(1970, 1, 1)
                # ms = time.mktime(value.utctimetuple())*1000
            else:
                epoch = datetime.date(1970, 1, 1)
                # ms = time.mktime(value.timetuple())*1000
            diff = o - epoch
            ms = (diff.days * 24 * 3600 + diff.seconds) * 1000
            ms += getattr(o, 'microseconds', 0)
            o = int(ms)

        # Defer to the superclass method
        return o
#         return json.JSONEncoder(self, o)

class ResultWrapper(object):
    def __init__(self, raw, **kw):
        self.__dict__['raw'] = raw
        self.__dict__['kw'] = kw

    def __getattr__(self, attr):
        return getattr(self.raw, attr)
    
    def __setattr__(self, attr, value):
        return setattr(self.raw, attr, value)
    
    def __nonzero__(self):
        return bool(self.raw)
    
    def __len__(self):
        return len(self.raw)
    
    def to_api(self):
        o = {}
        for k, v in self.kw.iteritems():
            if v is None:
                o[k] = {}
            else:
                o[k] = _to_api(v)
        return o

class Upload():
    def POST(self):
        i = web.input()
        filedir = TEMP_DIR # change this to the directory you want to store the file in.
        if 'qqfile' in i: # to check if the file-object is created
            myhash = hashlib.md5()
            myhash.update(i.qqfile)
            image = Image.open(StringIO.StringIO(i.qqfile))
            filename=myhash.hexdigest() + '.' + image.format.lower() # splits the and chooses the last part (the filename with extension)
#             fout = open(filedir +'/'+ filename,'w') # creates the file where the uploaded file should be stored
#             fout.write(data) # writes the uploaded file to the newly created file.
#             fout.close() # closes the file, upload complete.
            image.save(filedir +'/'+ filename)
        web.header('Content-Type', 'application/json')
        return json.dumps({
            'success': True,
            'filename':filename
        })

def nation(id=None, p=None, limit=None, admin=None):
    db = DB_Session()
    query = db.query(Nation)
    if web.ctx.method in ('POST','PUT','PATCH'):
        i=json.loads(web.data())
        if web.ctx.method in ('PUT','PATCH'):
            nation = query.get(int(id))
            for name,value in i.items():
                setattr(nation, name, value)
        else:
            nation = Nation(**i)
            db.add(nation)
            db.flush()
            db.refresh(nation)
        db.commit()
        n = ResultWrapper(nation, nation=nation.to_api(admin))
    else:
        if id:
            nation = query.get(int(id))
            n = ResultWrapper(nation, nation=nation.to_api(admin))
        else:
            nation = paging(query, limit, p)
            n = ResultWrapper(nation, nation=[v.to_api(admin) for v in nation],count=query.count())
    db.close()
    return n

def nationtranslation(id=None, p=0, limit=20):
    db = DB_Session()
    query = db.query(NationTranslation)
    method = web.ctx.method
    if method in ('POST','PUT','PATCH'):
        i=json.loads(web.data())
        if method in ('PUT','PATCH'):
            nationtranslation = query.get(int(id))
            for name,value in i.items():
                setattr(nationtranslation, name, value)
        else:
            nationtranslation = NationTranslation(**i)
            db.add(nationtranslation)
            db.flush()
            db.refresh(nationtranslation)
        db.commit()
        n = ResultWrapper(nationtranslation, nationtranslation=nationtranslation.to_api())
    else:
        if id:
            nationtranslation = query.get(int(id))
            n = ResultWrapper(nationtranslation, nationtranslation=nationtranslation.to_api())
        else:
            offset = (int(p) - 1)*int(limit)
            nationtranslation = query.offset(offset).limit(limit).all()
            n = ResultWrapper(nationtranslation, nationtranslation=[v.to_api() for v in nationtranslation],count=query.count())
    db.close()
    return n

def continent(id=None, p=0, limit=20):
    db = DB_Session()
    query = db.query(Continent)
    method = web.ctx.method
    if method in ('POST','PUT','PATCH'):
        i=web.data()
        i=json.loads(i)
        if method == 'PATCH':
            continent = query.get(int(id))
            continent.update(i)
            n = ResultWrapper(continent, continent=continent.to_api())
        else:
            continent = Continent(**i)
            db.add(continent)
            db.flush()
            db.refresh(continent)
            db.commit()
            n = ResultWrapper(continent, continent=continent.to_api())
    if method == 'DELETE':
        continent = query.get(int(id))
        db.delete(continent)
        db.commit()
        n = ResultWrapper(continent, continent=continent.to_api())
    if method == 'GET':
        if id:
            continent = query.get(int(id))
            n = ResultWrapper(continent, continent=continent.to_api())
        else:
            limit = int(limit)
            offset = (int(p) - 1)*limit
            continent = query.offset(offset).limit(limit).all()
            n = ResultWrapper(continent, continent=[v.to_api() for v in continent],count=query.count())
    db.close()
    return n

def city(id=None, p=None, limit=None, admin=None):
    db = DB_Session()
    query = db.query(City)
    if web.ctx.method in ('POST','PUT','PATCH'):
        i=json.loads(web.data())
        if web.ctx.method in ('PUT','PATCH'):
            city = query.get(int(id))
            for name,value in i.items():
                setattr(city, name, value)
        else:
            city = City(**i)
            db.add(city)
            db.flush()
            db.refresh(city)
        db.commit()
        n = ResultWrapper(city, city=city.to_api(admin))
    else:
        if id:
            city = query.get(int(id))
            n = ResultWrapper(city, city=city.to_api(admin))
        else:
            city = paging(query, limit, p)
            n = ResultWrapper(city, city=[v.to_api(admin) for v in city],count=query.count())
#             n = {'player' : list,'count':results[0].players}
    db.close()
    return n

def position(id=None, p=None, limit=None, admin=None):
    db = DB_Session()
    query = db.query(Position)
    if web.ctx.method in ('POST','PUT','PATCH'):
        i=json.loads(web.data())
        if web.ctx.method in ('PUT','PATCH'):
            position = query.get(int(id))
            for name,value in i.items():
                setattr(position, name, value)
        else:
            position = Position(**i)
            db.add(position)
            db.flush()
            db.refresh(position)
        db.commit()
        n = ResultWrapper(position, position=position.to_api())
    else:
        if id:
            position = query.get(int(id))
            n = ResultWrapper(position, position=position.to_api())
        else:
            position = paging(query, limit, p)
            n = ResultWrapper(position, position=[v.to_api() for v in position],count=query.count())
    db.close()
    return n

def club(id=None, p=None, limit=None, admin=None):
    db = DB_Session()
    query = db.query(Club)
    if web.ctx.method in ('POST','PUT','PATCH'):
        i=web.data()
        i=json.loads(i)
        if web.ctx.method in ('PUT','PATCH'):
            club = query.get(int(id))
            for name,value in i.items():
                setattr(club, name, value)
        else:
            club = Club(**i)
            db.add(club)
            db.flush()
            db.refresh(club)
        db.commit()
        n = ResultWrapper(club, club=club.to_api(admin))
    else:
        if id:
            club = query.get(int(id))
            n = ResultWrapper(club, club=club.to_api(admin))
        else:
            club = paging(query, limit, p)
            n = ResultWrapper(club, club=[v.to_api(admin) for v in club],count=query.count())
    db.close()
    return n

def clubtranslation(id=None, p=0, limit=20):
    db = DB_Session()
    query = db.query(ClubTranslation)
    method = web.ctx.method
    if web.ctx.method in ('POST','PUT','PATCH'):
        i=web.data()
        i=json.loads(i)
        if web.ctx.method in ('PUT','PATCH'):
            n = db.update('clubtranslation', where="id = " + id, **i)
        else:
            n = db.insert('clubtranslation', **i)
    else:
        if id:
            clubtranslation = query.get(int(id))
            n = ResultWrapper(clubtranslation, clubtranslation=clubtranslation.to_api())
        else:
            offset = (int(p) - 1)*int(limit)
            clubtranslation = query.offset(offset).limit(limit).all()
            n = ResultWrapper(clubtranslation, clubtranslation=[v.to_api() for v in clubtranslation],count=query.count())
    db.close()
    return n

def player(id=None, p=None, limit=None, admin=None, action=None, **kwargs):
    db = DB_Session()
    query = db.query(Player)
    method = web.ctx.method
    if method in ('POST','PUT','PATCH'):
        i=json.loads(web.data())
        position = None
        if i.has_key('position'):
            position = i.pop('position')
        if method in ('PUT','PATCH'):
            player = query.get(int(id))
            for name,value in i.items():
                setattr(player, name, value)
        else:
            player = Player(**i)
            db.add(player)
            db.flush()
            db.refresh(player)
        if position is not None:
            player.player2position[:] = [PlayerPosition(**{'player_id':id,'position_id':p}) for p in position]
        db.commit()
        n = ResultWrapper(player, player=player.to_api(admin))
    else:
        if id:
            player = query.get(int(id))
            position = [v.position_child for v in player.player2position]
            player = player.to_api(admin)
            player['position'] = [v.to_api() for v in position]
            n = ResultWrapper(player, player=player)
        else:
            player = query
            if kwargs.has_key('nation'):
                nation = kwargs['nation']
                player = query.join(TeamPlayer, Player.id == TeamPlayer.player_id).join(Team,Team.id == TeamPlayer.team_id).filter(Team.owner_id == int(nation) and Team.type == 1)
            if action is not None:
                for column in class_mapper(Player).columns:
                    column_name = column.key
                    if kwargs.has_key(column_name):
                        sql_string = ''
                        if isinstance(column.type, String):
                            sql_string = ' like "%'+kwargs[column_name]+'%"'
                        player = query.filter(column_name + sql_string)
            count = player.count()
            player = paging(player, limit, p)
            n = ResultWrapper(player, player=[v.to_api(admin) for v in player],count=count)
#             n = {'player' : list,'count':results[0].players}
    db.close()
    return n

def playertranslation(id=None, p=0, limit=20):
    db = DB_Session()
    query = db.query(PlayerTranslation)
    if web.ctx.method in ('POST','PUT','PATCH'):
        i=json.loads(web.data())
        if web.ctx.method in ('PUT','PATCH'):
            playertranslation = query.get(int(id))
            for name,value in i.items():
                setattr(playertranslation, name, value)
        else:
            playertranslation = PlayerTranslation(**i)
            db.add(playertranslation)
            db.flush()
            db.refresh(playertranslation)
        db.commit()
        n = ResultWrapper(playertranslation, playertranslation=playertranslation.to_api())
    else:
        if id:
            playertranslation = query.get(int(id))
            player = playertranslation.player_ref
            playertranslation = playertranslation.to_api()
            playertranslation['player'] = player.to_api(1)
            n = ResultWrapper(playertranslation, playertranslation=playertranslation)
        else:
            limit = int(limit)
            offset = (int(p) - 1)*limit
            playertranslation = query.offset(offset).limit(limit).all()
            n = ResultWrapper(playertranslation, playertranslation=[v.to_api() for v in playertranslation],count=query.count())
    db.close()
    return n

def clubsquad(club=None, p=0, limit=20):
    if club:
#         db = DB_Session()
#         query = db.query(Club)
#         club = query.get(int(club))
#         team = club.team.one()
#         player = [v.player for v in team.team2player]
        db = DB_Session()
        player = db.query(Player).join(TeamPlayer, Player.id == TeamPlayer.player_id).join(Team,Team.id == TeamPlayer.team_id).filter(Team.owner_id == int(club) and Team.type == 2)
        n = ResultWrapper(player, player=[v.to_api(None) for v in player],count=player.count())
        db.close()
    return n

def nationsquad(nation=None, p=None, limit=None):
    if nation:
#         db = DB_Session()
#         query = db.query(Nation)
#         nation = query.get(int(nation))
#         team = nation.team.one()
#         player = [v.player for v in team.team2player]
        db = DB_Session()
        query = db.query(Player)
        player = query.join(TeamPlayer, Player.id == TeamPlayer.player_id).join(Team,Team.id == TeamPlayer.team_id).filter(Team.owner_id == int(nation) and Team.type == 1)
        n = ResultWrapper(player, player=[v.to_api(None) for v in player],count=player.count())
        db.close()
    return n

def team(id=None, p=None, limit=None,admin=None):
    db = DB_Session()
    query = db.query(Team)
    if web.ctx.method in ('POST','PUT','PATCH'):
        i=json.loads(web.data())
        player = None
        if i.has_key('player'):
            player = i.pop('player')
        if web.ctx.method in ('PUT','PATCH'):
            team = query.get(int(id))
            for name,value in i.items():
                setattr(team, name, value)
        else:
            team = Team(**i)
            db.add(team)
            db.flush()
            db.refresh(team)
        if player is not None:
            team.teamplayer[:] = [TeamPlayer(**{'team_id':id, 'player_id':p}) for p in player]
        db.commit()
        n = ResultWrapper(team, team=team.to_api(admin))
    else:
        if id:
            team = query.get(int(id))
            player = [v.player for v in team.teamplayer]
            team = team.to_api(admin)
            team['player'] = [v.to_api(admin) for v in player]
            n = ResultWrapper(team, team=team)
        else:
            team = paging(query, limit, p)
            n = ResultWrapper(team, team=[v.to_api(admin) for v in team],count=query.count())
    db.close()
    return n

def match(id=None, p=None, limit=None,admin=None):
    db = DB_Session()
    query = db.query(Match)
    if web.ctx.method in ('POST','PUT','PATCH'):
        i=json.loads(web.data())
        if web.ctx.method in ('PUT','PATCH'):
            match = query.get(int(id))
            for name,value in i.items():
                setattr(match, name, value)
        else:
            match = Match(**i)
            db.add(match)
            db.flush()
            db.refresh(match)
        db.commit()
        n = ResultWrapper(match, match=match.to_api(admin))
    else:
        if id:
            match = query.get(int(id))
            match = match.to_api(admin)
            n = ResultWrapper(match, match=match)
        else:
            match = paging(query, limit, p)
            n = ResultWrapper(match, match=[v.to_api(admin) for v in match],count=query.count())
    db.close()
    return n

def teamplayer(id=None, p=0, limit=20):
    if web.ctx.method in ('POST','PUT','PATCH'):
        i=web.data()
        i=json.loads(i)
        if web.ctx.method in ('PUT','PATCH'):
            n = db.update('team2player', where="id = " + id, **i)
        else:
            id = n = db.insert('team2player', **i)
    else:
        if id:
#             n = db.select('player', where="id = " + id)
            n = db.query('SELECT * FROM team2player WHERE team2player.id='+id)
            team2player = n.list()[0]
            n = {'team2player' : team2player}
        else:
            offset = (int(p) - 1)*int(limit)
            #n = db.select('player', limit=int(limit), offset=offset)
            n = db.query('SELECT * FROM team2player LIMIT '+limit+' OFFSET ' + str(offset) + '')
            list = []
            for team2player in n.list():
                team2player.team = db.query('SELECT * FROM team WHERE team.id=' + str(team2player.team)).list()[0]
                team2player.player = db.query('SELECT * FROM player WHERE player.id=' + str(team2player.player)).list()[0]
                list.append(team2player)
            #n = db.query('SELECT *,GROUP_CONCAT(position_name) AS position FROM player LEFT JOIN player2position ON player.id = player2position.player LEFT JOIN position ON player2position.position = position.id')
            results = db.query("SELECT COUNT(*) AS teams FROM team2player")
            n = {'team2player' : list,'count':results[0].teams}
    return n

class PublicApi:
    methods = {"continent":continent,
               "nationtranslation":nationtranslation,
               "nation":nation,
               "city":city,
               "position":position,
               "player":player,
               "playertranslation":playertranslation,
               "club":club,
               "clubtranslation":clubtranslation,
               "team":team,
               "match":match,
               "clubsquad":clubsquad,
               "nationsquad":nationsquad,
               'teamplayer':teamplayer}
    # Private methods are externally accessible but whose design has not been
    # finalized yet and may change in the future.
    private_methods = ("entry_add_comment_with_entry_uuid","entry_get_comments_with_entry_uuid","keyvalue_put",
                       "keyvalue_get","keyvalue_prefix_list","presence_get","presence_set","presence_get_contacts")
    
    root_methods = ("user_authenticate","task_process_actor")

    def GET(self, name):
        return self.api_call(name)

    def POST(self, name):
        return self.api_call(name)

    def PUT(self, name):
        return self.api_call(name)
    
    def PATCH(self, name):
        return self.api_call(name)
    
    def DELETE(self, name):
        return self.api_call(name)
    
    def call_method(self, name, api_user=None):
        if api_user and name in self.root_methods and name in self.root_methods:
            return self.root_methods[name]
        if name in self.methods:
            return self.methods[name]
        if name in self.private_methods:
            return self.private_methods[name]
        return None

    def api_call(self, name, format="json"):
        """ the public api
        
        attempts to validate a request as a valid oauth request then
        builds the appropriate api_user object and tries to dispatch
        to the provided method
        """
        try:
            if web.ctx.method in ('POST','PUT','PATCH'):
                kwargs = dict(urlparse.parse_qsl(web.ctx.query.replace('?', '')))
                method = name or kwargs.pop('method', '').replace('.', '_')
            else:
                kwargs = urlparse.parse_qsl(web.ctx.query.replace('?', ''))
                kwargs = dict(kwargs)
                method = name or kwargs.pop('method', '').replace('.', '_')
            method_ref = self.call_method(method)
            rv = method_ref(**kwargs)
            return self.render_api_response(rv, format)
        except Exception,e:
            return self.render_api_response(e, format)
        # some error happened
        return self.render_api_response(e, format)
    
    def render_api_response(self, rv, format="json", servertime=None):
        o = {"status": "ok"}
        # TODO make this into something real
        rv = {"rv": rv.to_api()}
        o.update(rv)

        web.header('Content-Type', 'application/json')
        return json.dumps(o)
#         o = {"status": "ok"}
#         rv = {"rv": rv}
#         o.update(rv)
#         if servertime:
#             o['servertime'] = str(servertime)
#         web.header('Content-Type', 'application/json')
#         return json.dumps(o)