#!/usr/bin/env python

import sys
import math

from gsp import GSP
from util import argmax_index

from nautilusbb import Nautilusbb

def iround(x):
    """Round x and return an int"""
    return int(round(x))

class NautilusBudget(Nautilusbb):
    """Balanced bidding agent"""
    min_value = 0.25
    max_value = 1.75
    competitors = 4
    dropoff = 0.75

    def __init__(self, id, value, budget):
        super(NautilusBudget, self).__init__(id,value,budget)
        self.values_of_agents = {}

    def initial_bid(self, reserve):
        # initial bid is a balanced bid
        max_bid = self.max_value/2
        min_bid = self.min_value/2
        expected_min_bid = lambda s: ((float(self.competitors) - s) / float(self.competitors)) * (max_bid - min_bid) + min_bid
        expected_bids = [expected_min_bid(k) for k in range(1,self.competitors+1)]
        info = [(i,bid,bid) for (i,bid) in enumerate(expected_bids)]

        # clicks for initial round
        clicks = self.get_clicks(0,None)

        # maximal utility
        utilities = self.expected_utils_h(info, clicks, self.value)
        target = argmax_index(utilities)
        p = expected_bids[target]

        # written for clarity
        if p >= self.value:
            bid = self.value
        elif target > 0:
            # use click ratio as a measure of quality ratio
            bid = self.value - (clicks[target]/clicks[target-1]) * (self.value - p)
        else:
            bid = self.value

        return bid

    def get_clicks(self,t, history):
        '''
        Modified to take advantage of next round clicks
        '''
        top_slot = iround(30*math.cos(math.pi*t/24) + 50)
        return [iround(top_slot * pow(self.dropoff, i))
                              for i in range(self.competitors)]

    def get_bid(t, history, reserve, value):
        if t == 0:
            return value/2
        else:
            return super(NautilusBudget,self).bid_value(t,history,reserve,value)

    def bid(self, t, history, reserve):
        # if t = 1, we've finished t = 0 round, so save what everyone's values are
        # simulate a balanced bidding strategy (if we find that 2 or less are saving, then we save)
        # if 3 or more are saving, then we balance bid
        prev_bids = history.round(t-1).bids
        prev_occupants = history.round(t-1).occupants
        prev_round = zip(prev_occupants, prev_bids)
        if t == 1:
            self.values_of_agents = {occupant : bid*2 for (occupant,bid) in prev_round if occupant != self.id}

        # on every round, we first calculate what the other agents would bid under balanced bidding using our value
        other_agent_pred_bids = { agent: self.get_bid(t-1,history,reserve, value) for agent, value in self.values_of_agents}
        other_agent_real_bids = { agent: bid for (agent, bid) in prev_round }

        # count how many of the agents bid more than they should have the last round
        nsavers = 0
        for agent, pred_bid in other_agent_pred_bids:
            # we have a saver!
            if other_agent_real_bids[agent] < pred_bid:
                nsavers += 1

        # more than 2 savers, so compete now
        if nsavers > 2:
            easiness = 1

        # <= 2 saving, so wait until the world gets a little less harsh
        else:
            easiness = 0.5

        return easiness*super(NautilusBudget, self).bid(t,history,reserve) 



