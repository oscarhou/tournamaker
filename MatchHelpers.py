import SqlTypes
def get_current_round_record_split_players(round_id):
    result_players_dict = {}
    grouped_players_dict = {}
    # first get round data
    this_round = SqlTypes.session.query(SqlTypes.SqlTypes.Round).get(round_id)
    # for each player see if they are in a group
    for player in this_round.players:
        # check if this player is in a group
        # if they are, just continue
        if (SqlTypes.session.query(SqlTypes.Group).filter(SqlTypes.Group.round_id==this_round.id).filter(SqlTypes.Group.players.any(id=player.id)).all()):
            continue

        wins, losses = get_player_win_loss(this_round.tournament_id, player.id)
        score = wins - losses
        if score in result_players_dict:
            result_players_dict[score].append(player)
        else:
            result_players_dict[score] = [player]

    # now get the groups
    groups = SqlTypes.session.query(SqlTypes.Group).filter(SqlTypes.Group.round_id==this_round.id).all()
    for group in groups:
        group_score = 0
        # find the highest scoring player and that will represent the group win loss
        for player in group.players:
            wins, losses = get_player_win_loss(this_round.tournament_id, player.id)
            if group_score < wins - losses:
                group_score = wins - losses
        # after iterating, the group score will be determined
        if score in grouped_players_dict:
            grouped_players_dict[score].append(group)
        else:
            grouped_players_dict[score] = [group]

    return result_players_dict, grouped_players_dict

def get_round_players_groups_tuple(round_id):
    result_players = []
    grouped_players = []
    # first get round data
    this_round = SqlTypes.session.query(SqlTypes.Round).get(round_id)
    # for each player see if they are in a group
    for player in this_round.players:
        # check if this player is in a group
        # if they are, just continue
        if (SqlTypes.session.query(SqlTypes.Group).filter(SqlTypes.Group.round_id==this_round.id).filter(SqlTypes.Group.players.any(id=player.id)).all()):
            continue

        result_players.append(player)

    # now get the groups
    groups = SqlTypes.session.query(SqlTypes.Group).filter(SqlTypes.Group.round_id==this_round.id).all()
    for group in groups:
        grouped_players.append(group)

    return result_players, grouped_players


def query_by_round_id(object_type, round_id):
    return SqlTypes.session.query(object_type).filter(object_type.rounds.any(SqlTypes.Round.id == round_id))

def get_win_loss(team_id, round_id):
    return SqlTypes.session.query(SqlTypes.TeamRounds) \
        .filter(SqlTypes.TeamRounds.team_id==team_id) \
        .filter(SqlTypes.TeamRounds.round_id==round_id).first()

def get_teams_grouped_by_wins(tournament_id):
    teams = SqlTypes.get_teams_by_tournament_id(tournament_id)
    rounds = SqlTypes.get_rounds_by_tournament_id(tournament_id)

    team_score_map = {}
    for team in teams:
        # get match results
        wins = 0
        for round_iter in rounds:
            match_results = get_win_loss(team.id, round_iter.id)
            if match_results.win_loss != SqlTypes.WinLossEnum.Lose:
                wins += 1
        if wins in team_score_map:
            team_score_map[wins].append(team)
        else:
            team_score_map[wins] = [team]
    return team_score_map

def get_player_win_loss(this_tournament_id, player_id):
    # get player data
    player = SqlTypes.get_by_id(SqlTypes.Player, player_id)
    #get rounds this player played
    rounds = SqlTypes.session.query(SqlTypes.Round).filter(SqlTypes.Round.tournament_id==this_tournament_id).filter(SqlTypes.Round.players.any(id=player_id)).all()
    team = SqlTypes.session.query(SqlTypes.Team).filter(SqlTypes.Team.tournament_id==this_tournament_id).filter(SqlTypes.Team.players.any(id=player_id)).first()

    wins = 0
    losses = 0
    if team:
        for this_round in rounds:
            team_round = get_win_loss(team.id, this_round.id)
            # count this player's score
            if team_round.win_loss == SqlTypes.WinLossEnum.Win:
                wins += 1
            elif team_round.win_loss == SqlTypes.WinLossEnum.Lose:
                losses += 1
    return (wins, losses)

