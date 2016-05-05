import markup

def export_teams_to_file(location, teams, player_info_dict):
    page = markup.page()
    outfile = open(location, 'w')
    # temp way to print teams
    player_print_info = []
    for team in teams:
        for player in team.players:
            player_data_dict = player_info_dict[player.id]
            player_print_info.append( \
                (player.nickname, team.name, "{}/{}".format(player_data_dict["win"],player_data_dict["loss"])))
            del player_info_dict[player.id]
    for key,item in player_info_dict.iteritems():
        player_print_info.append(
            (item["player"].nickname, \
            "Bye", \
            "{}/{}".format(item["win"],item["loss"])))

    page.table()
    page.tr()
    page.th(("Name", "Team", "Win/Loss"))
    page.tr.close()
    for sorted_player in sorted(player_print_info, key=lambda item: item[0].lower()):
        page.tr()
        page.td(sorted_player)
        page.tr.close()

    page.table.close()
    outfile.write(str(page))

def export_players_to_file(location, players):
    outfile = open(location, 'w')
    # temp way to print teams
    names = []
    for player in players:
        names.append(player.nickname)

    for name in sorted(names, key=lambda item: item.lower()):
      outfile.write("{}\n".format(name))


"""
    outfile = open(location, 'w')
    print teams
    for team in teams:
        player_str = ""
        for player in team.players:
            if player_str:
                player_str += ","

            player_str += "{}".format(player.nickname)

        outfile.write("Team Name: {}, Players: {}\n".format(team.name, player_str))
"""


