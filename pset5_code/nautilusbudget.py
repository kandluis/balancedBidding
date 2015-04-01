#!/usr/bin/env python

import sys

from gsp import GSP
from util import argmax_index

from nautilus import Nautilusbb

def iround(x):
    """Round x and return an int"""
    return int(round(x))

class NautilusbbBudget(Nautilusbb):
    """Balanced bidding agent"""
    min_value = 0.25
    max_value = 1.75
    competitors = 4.0
    dropoff = 0.75

    def __init__(self, id, value, budget):
        super(NautilusbbBudget, self).__init__(id,value)
        self.values_of_agents = {id : value}

    def initial_bid(self, reserve):
        # initial bid is a balanced bid
        max_bid = self.max_value/2
        min_bid = self.min_value/2
        expected_min_bid = lambda s: ((self.competitors - s) / self.competitors) * (max_bid - min_bid) + min_bid
        expected_bids = [expected_min_bid(k) for k in range(1,self.competitors+1)]
        info = [(i,bid,bid) for enumerate(expected_bids)] + [(self.competitors,reserve,reserve)]

        # clicks for initial round
        clicks = get_clicks(0)

        # maximal utility
        utilities = self.expected_utils_h(info, clicks)
        target = argmax_index(utilities)
        p = expected_bids[target]

        # written for clarity
        if p >= self.value:
            bid = self.value
        elif k > 0:
            # use click ratio as a measure of quality ratio
            bid = self.value - (clicks[k]/clicks[k-1]) * (self.value - p)
        else:
            bid = self.value

        return bid

    def get_clicks(t):
        '''
        Modified to take advantage of next round clicks
        '''
        top_slot = iround(30*math.cos(math.pi*t/24) + 50)
        return [iround(top_slot_clicks * pow(self.dropoff, i))
                              for i in range(self.competitors)]

    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
        the other-agent bid for that slot in the last round.  If slot_id = 0,
        max_bid is min_bid * 2
        """
        i =  argmax_index(self.expected_utils(t, history, reserve))
        info = self.slot_info(t, history, reserve)
        return info[i]

    def bid(self, t, history, reserve):
        # if t = 1, we've finished t = 0 round, so save what everyone's values are
        prev_bids = history.round(t).bids
        prev_occupants = history.round(t).occupants

        if t == 1:
            self.values_of_agents = self.values_of_agents.update(
                {occupant : bid*2 for (occupant,bid) in zip(prev_occupants, prev_bids) if occupant != self.id})

        

