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

team_rounds = Table('team_rounds', Base.metadata,
        Column('team_id', ForeignKey('teams.id'), primary_key=True),
        Column('round_id', ForeignKey('rounds.id'), primary_key=True))

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

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))
    opponent_id = Column(Integer, ForeignKey('teams.id'))
    win_loss_status = Column(Integer, default=0)

    tournaments = relationship(
        'Tournament',
        back_populates='teams')

    players = relationship(
        'Player',
        secondary=team_players,
        back_populates='teams')

    rounds = relationship(
        'Round',
        secondary=team_rounds,
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
        secondary=team_rounds,
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
    session.add(new_round)
    session.commit()

def get_player_win_loss(this_tournament_id, player_id):
    # get player data
    player = get_by_id(Player, player_id)
    #get rounds this player played
    rounds = session.query(Round).filter(Round.tournament_id==this_tournament_id).filter(Round.players.any(id=player_id)).all()
    wins = 0
    losses = 0
    for this_round in rounds:
        # count this player's score
        for team in this_round.teams:
            if player in team.players:
                if team.win_loss_status == WinLossEnum.Win:
                    wins += 1
                elif team.win_loss_status == WinLossEnum.Lose:
                    losses += 1
                break
    return (wins, losses)

def get_current_round_record_split_players(round_id):
    result_dict = {}
    this_round = session.query(Round).get(round_id)
    for player in this_round.players:
        wins, losses = get_player_win_loss(this_round.tournament_id, player.id)
        score = wins - losses
        if score in result_dict:
            result_dict[score].append(player)
        else:
            result_dict[score] = [player]

    return result_dict

def query_by_round_id(object_type, round_id):
    return session.query(object_type).filter(object_type.rounds.any(Round.id == round_id))


