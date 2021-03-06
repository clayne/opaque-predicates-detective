from .op_detective import (bb_llil_analysis, bb_mlil_analysis, bb_analysis,
                                  get_authentic_bbs, get_non_generic_spec)

from .op_helpers import *
from binaryninja import *

from collections import namedtuple, defaultdict


AnalysisMetadata = namedtuple("AnalysisMetadata", "spec good_bbs")
LOGGING = True  # set to False if don't want logging 


def find_op_setup(bv, status=None):
    """
    Perform necessary setup before core analysis
    """
    # --- LOGGING ---
    if LOGGING:
        # debug is the lowest level == LOG EVERYTHING
        log_to_stdout(LogLevel.DebugLog)
    # --- LOGGING ---

    # maybe binja will find more functions
    # same as following in GUI:
    #     Tools -> Run Analysis Module -> Linear Sweep
    bv.update_analysis_and_wait()

    metadata = AnalysisMetadata(spec=get_non_generic_spec(),
                                good_bbs=get_authentic_bbs(bv))
    analysis = [
        bb_analysis,
        bb_llil_analysis,
        bb_mlil_analysis,
    ]

    (total_patch_locations, total_conds) = find_op(bv, analyses=analysis,
            metadata=metadata, status=status)

    # determine OP authenticity
    identify_authentic_op(total_patch_locations, total_conds, 
                          metadata, bv, patch=True)


class FindOpaqueInBackground(BackgroundTaskThread):
    def __init__(self, bv, msg):
        BackgroundTaskThread.__init__(self, msg, True)
        self.bv = bv

    def run(self):
        find_op_setup(self.bv, self)


def find_opaque_in_background(bv):
    """
    Start `FindOpaqueInBackground`
    """
    background_task = FindOpaqueInBackground(bv, "Finding opaque predicates")
    background_task.start()


PluginCommand.register("Opaque Predicate Detective",
                       "find opaque predicate", find_opaque_in_background)
