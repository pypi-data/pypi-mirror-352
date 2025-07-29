"""Microbial

Utilities for modeling various microbiological systems.
"""
# ─── import statements ────────────────────────────────────────────────── ✦✦ ─
from . import bacteria, fungi, frameworks, genomics, phylogeny, viruses

from .phylogeny import Phylogeny

from .bacteria import Bacterium
from .fungi import Fungus
from .genomics import Genome, BacterialGenome, FungalGenome, ViralGenome
from .viruses import Virus

from .frameworks import (
    environment, events, executor, queue, scheduler, simulator
)
from .frameworks.environment import Environment
from .frameworks.executor import Executor
from .frameworks.events import Event, Eventful, MutationEvent, ReplicationEvent
from .frameworks.queue import Queue
from .frameworks.scheduler import Scheduler
from .frameworks.simulator import Simulator

__all__ = [
    # ─── modules ─────────────────────────────────────────────────────────────
    "bacteria",
    "environment",
    "events",
    "executor",
    "frameworks",
    "fungi",
    "genomics",
    "phylogeny",
    "scheduler",
    "simulator",
    "queue",
    "viruses",

    # ─── classes ─────────────────────────────────────────────────────────────
    "BacterialGenome",
    "Bacterium",
    "Environment",
    "Event",
    "Eventful",
    "Executor",
    "FungalGenome",
    "Fungus",
    "Genome",
    "MutationEvent",
    "Queue",
    "ReplicationEvent",
    "Scheduler",
    "Simulator",
    "Phylogeny",
    "ViralGenome",
    "Virus"
]
