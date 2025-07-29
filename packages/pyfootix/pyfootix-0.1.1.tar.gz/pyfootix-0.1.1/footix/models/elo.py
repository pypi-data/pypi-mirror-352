import numpy as np
import pandas as pd

from footix.data_io.data_reader import EloDataReader
from footix.models.team_elo import EloTeam
from footix.utils.typing import ProbaResult


# TODO: A dataclass for agnostic_probs?
class EloDavidson:
    def __init__(
        self,
        n_teams: int,
        k0: int,
        lambd: float,
        sigma: int,
        agnostic_probs: ProbaResult,
        **kwargs,
    ):
        self.n_teams = n_teams
        self.check_probas(agnostic_probs)
        agn_home_proba, agn_draw_proba, agn_away_proba = agnostic_probs
        self.kappa = self.compute_kappa(P_H=agn_home_proba, P_D=agn_draw_proba, P_A=agn_away_proba)
        self.eta = self.compute_eta(P_H=agn_home_proba, P_A=agn_away_proba)
        self.k0 = k0
        self.lamda = lambd
        self.sigma = sigma
        self.championnat: dict[str, EloTeam] = {}

    # TODO: check the game.result warning
    def fit(self, X_train: pd.DataFrame | EloDataReader):
        if isinstance(X_train, pd.DataFrame):
            X_train = EloDataReader(df_data=X_train)
        clubs = X_train.unique_teams()
        if len(clubs) != self.n_teams:
            raise ValueError(
                "Number of teams in the training dataset is not the same as in the class"
                "instanciation"
            )

        for club in clubs:
            self.championnat[club] = EloTeam(club)

        for game in X_train:
            Home = game.home_team
            Away = game.away_team
            result = self.correspondance_result(game.result)
            gamma = np.abs(game.home_goals - game.away_goals)
            K = self.define_k_param(gamma)
            self.update_rank(self.championnat[Home], self.championnat[Away], result, K)

    def reset(self):
        self.championnat = {}

    @staticmethod
    def compute_kappa(P_H: float, P_D: float, P_A: float) -> float:
        return P_D / np.sqrt(P_H * P_A)

    @staticmethod
    def compute_eta(P_H: float, P_A: float) -> float:
        return np.log10(P_H / P_A)

    @staticmethod
    def check_probas(agnostic_probs: ProbaResult) -> None:
        if not np.isclose(np.sum(agnostic_probs), b=1.0):
            raise ValueError("Probabilities do not sum to one.\n")

    def define_k_param(self, gamma: int) -> float:
        return self.k0 * (1.0 + gamma) ** self.lamda

    @staticmethod
    def correspondance_result(result: str) -> float:
        if result not in ["D", "H", "A"]:
            raise ValueError("result must be 'H', 'D' or 'A'")
        if result == "D":
            return 0.5
        if result == "H":
            return 1.0
        return 0.0

    def estimated_res(self, difference: float) -> float:
        denom = 0.5 * difference / self.sigma
        return (10**denom + 0.5 * self.kappa) / (10**denom + 10 ** (-denom) + self.kappa)

    def update_rank(self, home_team: EloTeam, away_team: EloTeam, result: float, k: float) -> None:
        diff_rank = home_team.rank - away_team.rank + self.eta * self.sigma
        new_rankH = home_team.rank + k * (result - self.estimated_res(diff_rank))
        new_rankA = away_team.rank + k * (1.0 - result - self.estimated_res(-diff_rank))
        home_team.rank = new_rankH
        away_team.rank = new_rankA

    def __str__(self):
        if hasattr(self, "championnat"):
            classement = ""
            sorted_championnat = {
                k: v for k, v in sorted(self.championnat.items(), key=lambda item: -item[1].rank)
            }
            for i, k in enumerate(sorted_championnat.keys()):
                classement += f"{i+1}. {k} : {sorted_championnat[k].rank} \n"
            return classement
        else:
            return "{}"

    def predict(self, home_team: str, away_team: str) -> ProbaResult:
        return self.compute_proba(self.championnat[home_team], self.championnat[away_team])

    def proba_w(self, diff: float) -> float:
        num = 0.5 * diff / self.sigma
        return 10 ** (num) / (10**num + 10 ** (-num) + self.kappa)

    def proba_d(self, diff: float) -> float:
        num = 0.5 * diff / self.sigma
        return self.kappa / (10**num + 10 ** (-num) + self.kappa)

    def compute_proba(self, home_team: EloTeam, away_team: EloTeam) -> ProbaResult:
        diff = home_team.rank - away_team.rank
        diff = diff + self.eta * self.sigma
        probaH = self.proba_w(diff)
        probaA = self.proba_w(-diff)
        probaDraw = self.proba_d(diff)
        return ProbaResult(proba_home=probaH, proba_draw=probaDraw, proba_away=probaA)
