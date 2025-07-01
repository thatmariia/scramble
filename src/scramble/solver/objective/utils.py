from ortools.sat.python.cp_model import CpModel, IntVar
from scramble.solver.model_variables import ModelVariables
from scramble.solver.utils import define_and_var


def map_players_to_teams(mdl: CpModel, mv: ModelVariables) -> dict[str, IntVar]:
    """
    Map players to teams, returning a dictionary where keys are player IDs and values are IntVars representing team indices.
    """
    team_of_player: dict[str, IntVar] = {}
    for player in mv.active_players:
        tid = mdl.new_int_var(0, mv.nr_teams - 1, f"team_of_{player.id}")
        team_of_player[player.id] = tid
        for team_id in range(mv.nr_teams):
            mdl.add(tid == team_id).only_enforce_if(mv.player_in_team[(player.id, team_id)])

    return team_of_player


def map_players_to_courts(mdl: CpModel, mv: ModelVariables) -> dict[str, IntVar]:
    """
    Map players to courts, returning a dictionary where keys are player IDs and values are IntVars representing court indices.
    """
    court_id2idx = {court.id: i for i, court in enumerate(mv.courts)}

    court_of_player: dict[str, IntVar] = {}
    for player in mv.active_players:
        cvar = mdl.new_int_var(0, len(mv.courts) - 1, f"court_of_{player.id}")
        court_of_player[player.id] = cvar
        # self.model.add_element(team_of_player[player.id], court_idx_of_team, cvar)
        for team_id in range(mv.nr_teams):
            for court_id, court_idx in court_id2idx.items():
                # player p is in team t AND team t is on court cid → p is on that court
                cond = define_and_var(
                    mdl,
                    f"{player.id}_in_t{team_id}_on_c{court_id}",
                    [
                        mv.player_in_team[(player.id, team_id)],
                        mv.team_on_court[(team_id, court_id)]
                    ]
                )
                mdl.add(cvar == court_idx).only_enforce_if(cond)

    return court_of_player


def map_teams_to_courts(mdl: CpModel, mv: ModelVariables) -> list[IntVar]:
    """
    Map teams to courts, returning a list of IntVars where each index corresponds to a team.
    """
    court_id2idx = {court.id: i for i, court in enumerate(mv.courts)}

    court_idx_of_team: list[IntVar] = []
    for team_id in range(mv.nr_teams):
        court_idx = mdl.new_int_var(0, len(mv.courts) - 1, f"court_idx_t{team_id}")
        court_idx_of_team.append(court_idx)
        for court_id, idx in court_id2idx.items():
            mdl.add(court_idx == idx).only_enforce_if(mv.team_on_court[(team_id, court_id)])

    return court_idx_of_team

