# -*- coding: utf-8 -*-
'''
Created on 2011-9-12

@author: nttdocomo
'''
import datetime, json, web, urlparse, Image, StringIO, hashlib
from soccer.models import DB_Session, Continent, _to_api, Player, PlayerTranslation, Nation, NationTeam, NationTeamPlayer, Position, PlayerPosition, Club, ClubTranslation, ClubTeam, ClubTeamPlayer, parseAcceptLanguage
from sessions.models import WebpySession
from settings import TEMP_DIR

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

def nation_all():
    db = DB_Session()
    entries = db.select('nation')
    return {'nations' : entries.list()}
#     return ResultWrapper(entries, entries=entries.list())

def nation(id=None, p=0, limit=20, admin=None):
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
            limit = int(limit)
            offset = (int(p) - 1)*limit
            nation = query.offset(offset).limit(limit).all()
            n = ResultWrapper(nation, nation=[v.to_api(admin) for v in nation],count=query.count())
    db.close()
    return n

def continent_all():
    entries = db.select('continent')
    return {'continents' : entries.list()}
#     return ResultWrapper(entries, entries=entries.list())

def continent(id=None, p=0, limit=20):
    session = DB_Session()
    query = session.query(Continent)
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
            session.add(continent)
            session.flush()
            session.refresh(continent)
            session.commit()
            n = ResultWrapper(continent, continent=continent.to_api())
    if method == 'DELETE':
        continent = query.get(int(id))
        session.delete(continent)
        session.commit()
        n = ResultWrapper(continent, continent=continent.to_api())
    else:
        if id:
            continent = query.get(int(id))
            n = ResultWrapper(continent, continent=continent.to_api())
        else:
            limit = int(limit)
            offset = (int(p) - 1)*limit
            continent = query.offset(offset).limit(limit).all()
            n = ResultWrapper(continent, continent=[v.to_api() for v in continent],count=query.count())
    session.close()
    return n

def position(id=None, p=0, limit=20, admin=None):
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
            limit = int(limit)
            offset = (int(p) - 1)*limit
            position = query.offset(offset).limit(limit).all()
            n = ResultWrapper(position, position=[v.to_api() for v in position],count=query.count())
#             n = {'player' : list,'count':results[0].players}
    db.close()
    return n

def club(id=None, p=0, limit=20, admin=None):
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
            limit = int(limit)
            offset = (int(p) - 1)*limit
            club = query.offset(offset).limit(limit).all()
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

def player(id=None, p=0, limit=20, admin=None):
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
            player.player2position[:] = [PlayerPosition(**{'player':id,'position':p}) for p in position]
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
            limit = int(limit)
            offset = (int(p) - 1)*limit
            count=query.count()
            player = query.offset(offset).limit(limit).all()
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
        player = db.query(Player).join(ClubTeamPlayer, Player.id == ClubTeamPlayer.player_id).join(ClubTeam,ClubTeam.id == ClubTeamPlayer.team_id).filter(ClubTeam.club == int(club))
        n = ResultWrapper(player, player=[v.to_api(None) for v in player],count=player.count())
        db.close()
    return n

def nationsquad(nation=None, p=0, limit=20):
    if nation:
#         db = DB_Session()
#         query = db.query(Nation)
#         nation = query.get(int(nation))
#         team = nation.team.one()
#         player = [v.player for v in team.team2player]
        db = DB_Session()
        player = db.query(Player).join(NationTeamPlayer, Player.id == NationTeamPlayer.player_id).join(NationTeam,NationTeam.id == NationTeamPlayer.team_id).filter(NationTeam.nation == int(nation))
        n = ResultWrapper(player, player=[v.to_api(None) for v in player],count=player.count())
        db.close()
    return n

def clubteam(id=None, p=0, limit=20,admin=None):
    db = DB_Session()
    query = db.query(ClubTeam)
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
            team = ClubTeam(**i)
            db.add(team)
            db.flush()
            db.refresh(team)
        if player is not None:
            team.team2player[:] = [ClubTeamPlayer(**{'team':id, 'player':p}) for p in player]
        db.commit()
        n = ResultWrapper(team, team=team.to_api(admin))
    else:
        if id:
            team = query.get(int(id))
            player = [v.player for v in team.team2player]
            team = team.to_api(admin)
            team['player'] = [v.to_api(admin) for v in player]
            n = ResultWrapper(team, team=team)
        else:
            limit = int(limit)
            offset = (int(p) - 1)*limit
            team = query.offset(offset).limit(limit).all()
            n = ResultWrapper(team, team=[v.to_api(admin) for v in team],count=query.count())
    db.close()
    return n

def nationteam(id=None, p=0, limit=20,admin=None):
    db = DB_Session()
    query = db.query(NationTeam)
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
            team = NationTeam(**i)
            db.add(team)
            db.flush()
            db.refresh(team)
        if player is not None:
            team.team2player[:] = [NationTeamPlayer(**{'team':id, 'player':p}) for p in player]
        db.commit()
        n = ResultWrapper(team, team=team.to_api(admin))
    else:
        if id:
            team = query.get(int(id))
            player = [v.player for v in team.team2player]
            team = team.to_api(admin)
            team['player'] = [v.to_api(admin) for v in player]
            n = ResultWrapper(team, team=team)
        else:
            limit = int(limit)
            offset = (int(p) - 1)*limit
            team = query.offset(offset).limit(limit).all()
            n = ResultWrapper(team, team=[v.to_api(admin) for v in team],count=query.count())
    db.close()
    return n

def clubteam2player(id=None, p=0, limit=20):
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
    methods = {"continent_all":continent_all,
               "continent":continent,
               "nation_all":nation_all,
               "nation":nation,
               "position":position,
               "player":player,
               "playertranslation":playertranslation,
               "club":club,
               "clubtranslation":clubtranslation,
               "clubteam":clubteam,
               "nationteam":nationteam,
               "clubsquad":clubsquad,
               "nationsquad":nationsquad,
               'clubteam2player':clubteam2player}
    # Private methods are externally accessible but whose design has not been
    # finalized yet and may change in the future.
    private_methods = ("entry_add_comment_with_entry_uuid","entry_get_comments_with_entry_uuid","keyvalue_put",
                       "keyvalue_get","keyvalue_prefix_list","presence_get","presence_set","presence_get_contacts")
    
    root_methods = ("user_authenticate","task_process_actor")

    def GET(self):
        return self.api_call()

    def POST(self):
        return self.api_call()

    def PUT(self):
        return self.api_call()
    
    def PATCH(self):
        return self.api_call()
    
    def DELETE(self):
        return self.api_call()
    
    def call_method(self, name, api_user=None):
        if api_user and name in self.root_methods and name in self.root_methods:
            return self.root_methods[name]
        if name in self.methods:
            return self.methods[name]
        if name in self.private_methods:
            return self.private_methods[name]
        return None

    def api_call(self, format="json"):
        """ the public api
        
        attempts to validate a request as a valid oauth request then
        builds the appropriate api_user object and tries to dispatch
        to the provided method
        """
        try:
            if web.ctx.method in ('POST','PUT','PATCH'):
                kwargs = dict(urlparse.parse_qsl(web.ctx.query.replace('?', '')))
                method = kwargs.pop('method', '').replace('.', '_')
            else:
                kwargs = urlparse.parse_qsl(web.ctx.query.replace('?', ''))
                kwargs = dict(kwargs)
                method = kwargs.pop('method', '').replace('.', '_')
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