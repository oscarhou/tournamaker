from random import shuffle
from CustomDialogs import MessageDialog
import SqlTypes
import MatchHelpers

def assign_to_teams(team_size, player_list):
    team_list = []
    players = []
    count = 0

    # put players in groups of 2
    while len(player_list) > 0:
        if (len(players) < team_size):
            player = player_list.pop()
            players.append(player)
        else:
            team_list.append(players)
            count += 1
            players = []

    # after iterating if have remaining
    if len(players) > 0:
        team_list.append(players)

    return team_list

def shuffle_and_assign_score_bias(team_size, players_tuple, min_team_count=1):
    groups = sorted(players_tuple[1], key=lambda x: len(x.players), reverse=True)
    players = players_tuple[0]
    shuffle(players)

    # fill the total item list with the highest ranked group
    total_item_list = []
    total_team_list = []
    count = 0

    # while we still have players/groups
    while len(groups) or len(players):
        has_progress = False
        # if we have enough players for a team, store the completed team
        # and start a new team

        add_group = None
        for group in groups:
            # if the current group has less than or equal to the number of players
            # needed to complete the team, remove group and continue
            if len(group.players) <= (team_size - len(total_item_list)):
                total_item_list += group.players
                add_group = group
                groups.remove(add_group)
                has_progress = True
                break

        # if no group was found, resort to adding individual players to fill the team
        if add_group == None:
            while len(total_item_list) < team_size and len(players):
                total_item_list.append(players.pop())
                has_progress = True

        if len(total_item_list) >= team_size:
            total_team_list.append(list(total_item_list))
            total_item_list = []

        # if no progress has been made, then break out
        if not has_progress:
            raise Exception("Failed to form teams (try breaking up groups)")

    return total_team_list

def generate_teams(this_round_id):
    current_round = SqlTypes.session.query(SqlTypes.Round).filter(SqlTypes.Round.id==this_round_id).first()
    # clear existing teams
    current_teams = current_round.teams

    for team in current_teams:
        SqlTypes.session.delete(team)

    try:
        generated_teams = shuffle_and_assign_score_bias(
            5,
            MatchHelpers.get_round_players_groups_tuple(this_round_id),
            2)

        # get list that contains a list of 5 SQLType.Players
        count = 0
        for team in generated_teams:
            # for each team create a record and add it to the current round
            count += 1
            new_team = SqlTypes.Team(name=count, players=team, tournament_id=current_round.tournament_id)
            current_round.teams.append(new_team)
            SqlTypes.session.add(new_team)

        SqlTypes.session.commit()

        match_teams(this_round_id)
    except Exception:
        raise

def match_teams(this_round_id):
    this_round = SqlTypes.get_by_id(SqlTypes.Round, this_round_id)
    matched_pairs = pair_teams(MatchHelpers.get_teams_grouped_by_wins(this_round.tournament_id))
    for this_pair in matched_pairs:
        first_team = MatchHelpers.get_win_loss(this_pair[0].id, this_round.id)
        if len(this_pair) > 1:
            second_team = MatchHelpers.get_win_loss(this_pair[1].id, this_round.id)
            first_team.opponent_id = this_pair[1].id
            second_team.opponent_id = this_pair[0].id
        else:
            first_team.opponent_id = None

    SqlTypes.session.commit()

def pair_teams(team_score_dict):
    """
        This function can actually group more than 
        2 items together.
    """
    matched_pairs = []
    # iterate through all the teams
    current_pair = []
    for key,item in sorted(team_score_dict.iteritems(), reverse=True):
        shuffle(item)
        # every team that is seen add to the list
        for team in item:
            current_pair.append(team)

            if (len(current_pair) >= 2):
                # if we have 2 teams create a new one
                # after adding to the main list
                matched_pairs.append(list(current_pair))
                current_pair = []
    if len(current_pair):
        matched_pairs.append(current_pair)

    return matched_pairs

def shuffle_and_assign(teamsize, item_list):
    """
       shuffles and incoming list of items and sorts them
       into groups of specified size
       used for randomly matching players to teams and also
       for team matchmaking
    """
    # if empty then just return
    if len(item_list) <= 0:
        return []

    shuffled_list = list(item_list)
    shuffle(shuffled_list)
    return assign_to_teams(teamsize, shuffled_list)

