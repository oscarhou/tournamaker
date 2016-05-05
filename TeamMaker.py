from random import shuffle
from SqlTypes import Team

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

def shuffle_and_assign_score_bias(team_size, pair_dict):
    sorted_keys = sorted(pair_dict.keys())
    print sorted_keys
    # fill the total item list with the highest ranked group
    total_item_list = []
    total_team_list = []
    count = 0
    while True:
        count += 1
        # get at least 2 times the team size so there is a match
        if len(total_item_list) >= (2 * team_size):
            shuffle(total_item_list)
            total_team_list += assign_to_teams(team_size, total_item_list)
            print total_team_list
            total_item_list = []
        else:
            # if we don't have enough in the current list but still have items to add
            if len(sorted_keys):
                # get a list corresponding to the next rank of players
                if len(pair_dict[sorted_keys[-1]]):
                    total_item_list.append(pair_dict[sorted_keys[-1]].pop())
                else: # next item is empty
                    sorted_keys.pop()
            else: # ran out of groups to get items from
# commented out since we want to assign those players to byes
#                shuffle(total_item_list)
#                total_team_list += assign_to_teams(team_size, total_item_list)
                break

    return total_team_list

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

