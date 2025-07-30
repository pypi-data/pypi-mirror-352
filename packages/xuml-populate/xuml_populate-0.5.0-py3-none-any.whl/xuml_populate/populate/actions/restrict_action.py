"""
restrict_action.py – Populate a Restrict Action instance in PyRAL
"""

import logging
from typing import Set
from xuml_populate.config import mmdb
from xuml_populate.populate.actions.aparse_types import Flow_ap, Activity_ap
from xuml_populate.populate.actions.action import Action
from xuml_populate.populate.actions.expressions.restriction_condition import RestrictCondition
from xuml_populate.populate.flow import Flow
from xuml_populate.populate.mmclass_nt import (Relational_Action_i, Table_Action_i, Restrict_Action_i,
                                               Table_Restriction_Condition_i)
from pyral.relvar import Relvar
from pyral.relation import Relation  # Here for debugging
from pyral.transaction import Transaction
from scrall.parse.visitor import Criteria_Selection_a, Rank_Selection_a

_logger = logging.getLogger(__name__)

# Transactions
tr_Restrict_Action = "Restrict Action"


class RestrictAction:
    """
    Create all relations for a Restrict Action
    """

    def __init__(self, input_relation_flow: Flow_ap, selection_parse: Criteria_Selection_a,
                 activity_data: Activity_ap):
        """
        Populate the Restrict Action

        :param input_relation_flow: The source table flow into this restriction
        :param selection_parse:  The parsed Scrall select action group
        :param activity_data:
        """
        # Save attribute values that we will need when creating the various select subsystem
        # classes
        domain = activity_data.domain
        anum = activity_data.anum

        # Populate the Action superclass instance and obtain its action_id
        Transaction.open(db=mmdb, name=tr_Restrict_Action)
        self.action_id = Action.populate(tr=tr_Restrict_Action, anum=anum, domain=domain, action_type="restrict")

        # Populate the output Table Flow using same Table as input flow
        self.output_relation_flow = Flow.populate_relation_flow_by_reference(ref_flow=input_relation_flow, anum=anum,
                                                                             domain=domain)

        # Walk through the criteria parse tree storing any attributes or input flows
        rcond = RestrictCondition(tr=tr_Restrict_Action, action_id=self.action_id, input_nsflow=input_relation_flow,
                                  selection_parse=selection_parse, activity_data=activity_data)
        self.sflows = rcond.input_scalar_flows
        # The first two return values are relevant only to instance selection (Select Action)
        # Restrict action does not use the returned cardinality since output is always a Table Flow
        # Nor does it use the comparision critieria to test for identifier selection

        Relvar.insert(db=mmdb, tr=tr_Restrict_Action, relvar='Table_Restriction_Condition', tuples=[
            Table_Restriction_Condition_i(Restrict_action=self.action_id, Activity=anum, Domain=domain)
        ])
        Relvar.insert(db=mmdb, tr=tr_Restrict_Action, relvar='Relational_Action', tuples=[
            Relational_Action_i(ID=self.action_id, Activity=anum, Domain=domain)
        ])
        Relvar.insert(db=mmdb, tr=tr_Restrict_Action, relvar='Table_Action', tuples=[
            Table_Action_i(ID=self.action_id, Activity=anum, Domain=domain,
                           Input_a_flow=input_relation_flow.fid, Output_flow=self.output_relation_flow.fid)
        ])
        Relvar.insert(db=mmdb, tr=tr_Restrict_Action, relvar='Restrict_Action', tuples=[
            Restrict_Action_i(ID=self.action_id, Activity=anum, Domain=domain)
        ])
        # We now have a transaction with all select-action instances, enter into the metamodel db
        Transaction.execute(db=mmdb, name=tr_Restrict_Action)  # Restrict Action
