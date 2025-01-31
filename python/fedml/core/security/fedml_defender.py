import logging
from .defense.cclip_defense import CClipDefense
from .defense.dp import DifferentialPrivacy
from .defense.geometric_median_defense import GeometricMedianDefense
from .defense.krum_defense import KrumDefense
from .defense.robust_learning_rate_defense import RobustLearningRateDefense
from .defense.slsgd_defense import SLSGDDefense
from .defense.weak_dp_defense import WeakDPDefense
from ...core.security.defense.norm_diff_clipping_defense import NormDiffClippingDefense
from ...core.security.constants import (
    DEFENSE_NORM_DIFF_CLIPPING,
    DEFENSE_ROBUST_LEARNING_RATE,
    DEFENSE_KRUM,
    DEFENSE_SLSGD,
    DEFENSE_GEO_MEDIAN,
    DEFENSE_CCLIP, DEFENSE_WEAK_DP, DEFENSE_DP
)
from typing import List, Tuple, Dict, Any, Callable


class FedMLDefender:

    _defender_instance = None

    @staticmethod
    def get_instance():
        if FedMLDefender._defender_instance is None:
            FedMLDefender._defender_instance = FedMLDefender()

        return FedMLDefender._defender_instance

    def __init__(self):
        self.is_enabled = False
        self.defense_type = None
        self.defender = None

    def init(self, args):
        if hasattr(args, "enable_defense") and args.enable_defense:
            self.is_enabled = True
            self.defense_type = args.defense_type.strip()
            logging.info("self.defense_type = {}".format(self.defense_type))
            self.defender = None
            if self.defense_type == DEFENSE_NORM_DIFF_CLIPPING:
                self.defender = NormDiffClippingDefense(args)
            elif self.defense_type == DEFENSE_ROBUST_LEARNING_RATE:
                self.defender = RobustLearningRateDefense(args)
            elif self.defense_type == DEFENSE_KRUM:
                self.defender = KrumDefense(args)
            elif self.defense_type == DEFENSE_SLSGD:
                self.defender = SLSGDDefense(args)
            elif self.defense_type == DEFENSE_GEO_MEDIAN:
                self.defender = GeometricMedianDefense(args)
            elif self.defense_type == DEFENSE_WEAK_DP:
                self.defender = WeakDPDefense(args)
            elif self.defense_type == DEFENSE_CCLIP:
                self.defender = CClipDefense(args)
            elif self.defense_type == DEFENSE_DP:
                self.defender = DifferentialPrivacy(args)
            else:
                raise Exception("args.attack_type is not defined!")
        else:
            self.is_enabled = False

    def is_defense_enabled(self):
        return self.is_enabled

    def get_defense_types(self):
        return self.defense_type

    def defend(
        self,
        raw_client_grad_list: List[Tuple[float, Dict]],
        base_aggregation_func: Callable = None,
        extra_auxiliary_info: Any = None,
    ):
        if self.defender is None:
            raise Exception("defender is not initialized!")
        return self.defender.run(
            raw_client_grad_list, base_aggregation_func, extra_auxiliary_info
        )

