"""Executor Framework

This module provides the `Executor` class for managing and executing
the tasks scheduled and managed by the `Scheduler` class.
"""

# ─── interfaces ───────────────────────────────────────────────────────── ✦✦ ──

class Executor:
    """Base class for task execution."""
    def __init__(self, scheduler):
        self.scheduler = scheduler

