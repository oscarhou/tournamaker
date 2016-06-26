from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, Integer, String, Table, ForeignKey, create_engine

engine = create_engine('sqlite:///testsqllite.db', echo=False)
session_maker = sessionmaker(bind=engine)
session = session_maker()
Base = declarative_base()

tournament_teams = Table('tournament_teams', Base.metadata,
        Column('tournament_id', ForeignKey('tournaments.id'), primary_key=True),
        Column('team_id', ForeignKey('teams.id'), primary_key=True))

tournament_players = Table('tournament_players', Base.metadata,
        Column('tournament_id', ForeignKey('tournaments.id'), primary_key=True),
        Column('player_id', ForeignKey('players.id'), primary_key=True))

team_players = Table('team_players', Base.metadata,
        Column('team_id', ForeignKey('teams.id'), primary_key=True),
        Column('player_id', ForeignKey('players.id'), primary_key=True))

#team_rounds = Table('team_rounds', Base.metadata,
#        Column('team_id', ForeignKey('teams.id'), primary_key=True),
#        Column('round_id', ForeignKey('rounds.id'), primary_key=True),
#        Column('win_loss', Integer))

round_players = Table('round_players', Base.metadata,
        Column('player_id', ForeignKey('players.id'), primary_key=True),
        Column('round_id', ForeignKey('rounds.id'), primary_key=True))

group_players = Table('group_players', Base.metadata,
        Column('player_id', ForeignKey('players.id'), primary_key=True),
        Column('group_id', ForeignKey('groups.id'), primary_key=True))

class WinLossEnum():
    NotPlayed = 0
    Win = 1
    Lose = 2

class GroupPlayerEnum():
    Group = 0
    Player = 1

class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    nickname = Column(String)
    phone = Column(String)

    tournaments = relationship(
        'Tournament',
        secondary=tournament_players,
        back_populates='players')

    teams = relationship(
        'Team',
        secondary=team_players,
        back_populates='players')

    rounds = relationship(
        'Round',
        secondary=round_players,
        back_populates='players')

    groups = relationship(
        'Group',
        secondary=group_players,
        back_populates='players')


    def __eq__(self,other):
        return self.id == other.id

    def __repr__(self):
        return "<User(id='{}, 'first_name='{}', last_name='{}', nickname='{}', phone={})>".format(
        self.id, self.first_name, self.last_name, self.nickname, self.phone)

class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey('rounds.id'))

    players = relationship(
        'Player',
        secondary=group_players,
        back_populates='groups')

    def __repr__(self):
        return "<Group(id='{}', round_id={})>".format(self.id, self.round_id)

class Tournament(Base):
    __tablename__ = 'tournaments'

    id = Column(Integer, primary_key=True)
    name = Column(String)
#$    date = Column(String)

    teams = relationship(
        'Team',
        secondary=tournament_teams,
        back_populates='tournaments')

    players = relationship(
        'Player',
        secondary=tournament_players,
        back_populates='tournaments')


    def __repr__(self):
        #return "<Tournament(name='{}', date='{}')>".format(self.name, self.date)
        return "<Tournament(name='{}')>".format(self.name)

class TeamRounds(Base):
    __tablename__ = 'team_rounds'
    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey('rounds.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    opponent_id = Column(Integer, default=None)
    win_loss = Column(Integer, default=WinLossEnum.NotPlayed)

    def __repr__(self):
        #return "<Tournament(name='{}', date='{}')>".format(self.name, self.date)
        return "<TeamRounds(team='{}', round='{}', win_loss='{}')>".format(self.team_id, self.round_id, self.win_loss)

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))

    tournaments = relationship(
        'Tournament',
        back_populates='teams')

    players = relationship(
        'Player',
        secondary=team_players,
        back_populates='teams')

    rounds = relationship(
        'Round',
        secondary=TeamRounds.__table__,
        back_populates='teams')


    def __repr__(self):
        return "<Team(name='{}')>".format(self.name)

class Round(Base):
    __tablename__ = 'rounds'

    id = Column(Integer, primary_key=True)
    round_count = Column(Integer)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))

    players = relationship(
        'Player',
        secondary=round_players,
        back_populates='rounds')

    teams = relationship(
        'Team',
        secondary=TeamRounds.__table__,
        back_populates='rounds')

    def __repr__(self):
        return "<Round(id = '{}', count='{}', tournament_id='{}')>".format(self.id, self.round_count,self.tournament_id)

Base.metadata.create_all(engine)

def get_by_id(sql_type, sql_id):
    return session.query(sql_type).filter(sql_type.id==sql_id).first()

def sql_query(query_type, expression):
    return session.query(query_type).filter(expression)

def nickname_exists(nickname):
    return session.query(Player.nickname).filter(Player.nickname==nickname).first()

def add_player_to_db(sql_type_player):
    if not nickname_exists(sql_type_player.nickname):
        session.add(sql_type_player)
        return True
    else:
        return False

def add_new_round(round_tournament_id):
    # current number of rounds will not reflect the one we are about to add
    rounds = len(session.query(Round).filter(Round.tournament_id==round_tournament_id).all())
    new_round = Round(round_count=rounds + 1, tournament_id=round_tournament_id)

    if rounds > 0:
        prev_round = session.query(Round) \
            .filter(Round.tournament_id==round_tournament_id) \
            .filter(Round.round_count==rounds).first()

        new_round.players = list(prev_round.players)
        new_round.teams = list(prev_round.teams)

    session.add(new_round)
    session.commit()

def get_teams_by_tournament_id(tournament_id):
    return session.query(Team).filter(Team.tournament_id==tournament_id).all()

def get_rounds_by_tournament_id(tournament_id):
    return session.query(Round).filter(Round.tournament_id==tournament_id).all()

def get_teams_by_round_id(round_id):
    return session.query(Team).filter(Team.round_id==round_id).all()

def get_team_rounds_by_round_id(round_id):
    return session.query(TeamRounds).filter(TeamRounds.round_id==round_id).all()


