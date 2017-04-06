from __future__ import absolute_import

import random

randgen = random.Random()

randgen.state_set = False


def get_random_state():
    """Retrieve the state of factory.fuzzy's random generator."""
    return randgen.getstate()


def set_random_state(state):
    """Force-set the state of factory.fuzzy's random generator."""
    randgen.state_set = True
    return randgen.setstate(state)


def reseed_random(seed):
    """Reseed factory.fuzzy's random generator."""
    r = random.Random(seed)
    set_random_state(r.getstate())
