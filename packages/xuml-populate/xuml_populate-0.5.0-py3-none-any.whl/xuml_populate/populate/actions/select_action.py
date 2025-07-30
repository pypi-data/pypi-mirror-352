"""
select_action.py – Populate a selection action instance in PyRAL
"""

import logging
from typing import List
from xuml_populate.config import mmdb
from xuml_populate.populate.actions.aparse_types import Flow_ap, MaxMult, Activity_ap, Attribute_Comparison
from xuml_populate.populate.actions.action import Action
from xuml_populate.populate.flow import Flow
from xuml_populate.populate.actions.expressions.restriction_condition import RestrictCondition
from xuml_populate.populate.mmclass_nt import (Select_Action_i, Single_Select_i, Identifier_Select_i,
                                               Zero_One_Cardinality_Select_i, Many_Select_i,
                                               Class_Restriction_Condition_i)
from pyral.relvar import Relvar
from pyral.relation import Relation
from pyral.transaction import Transaction

_logger = logging.getLogger(__name__)

# Transactions
tr_Select = "Select Action"


class SelectAction:
    """
    Create all relations for a Select Statement
    """

    def __init__(self, input_instance_flow: Flow_ap, selection_parse, activity_data: Activity_ap):
        """

        :param input_instance_flow: The source flow into this selection
        :param selection_parse:  The parsed Scrall select action group
        :param activity_data:
        """
        self.input_instance_flow = input_instance_flow  # We are selecting instances from this instance flow
        self.selection_parse = selection_parse
        self.activity_data = activity_data
        self.domain = activity_data.domain
        self.anum = activity_data.anum

        self.attr_comparisons: List[Attribute_Comparison]

        self.expression = None
        self.comparison_criteria = []
        self.equivalence_criteria = []
        self.restriction_text = ""
        self.criterion_ctr = 0
        self.max_mult: MaxMult

        # Save attribute values that we will need when creating the various select subsystem
        # classes

        # Populate the Action superclass instance and obtain its action_id
        Transaction.open(db=mmdb, name=tr_Select)
        self.action_id = Action.populate(tr=tr_Select, anum=self.anum, domain=self.domain,
                                         action_type="select")  # Transaction open
        Relvar.insert(db=mmdb, tr=tr_Select, relvar='Select_Action', tuples=[
            Select_Action_i(ID=self.action_id, Activity=self.anum, Domain=self.domain,
                            Input_flow=self.input_instance_flow.fid)
        ])
        # Walk through the criteria parse tree storing any attributes or input flows
        # Also check to see if we are selecting on an identifier
        rcond = RestrictCondition(tr=tr_Select, action_id=self.action_id,
                                  input_nsflow=self.input_instance_flow,
                                  selection_parse=self.selection_parse,
                                  activity_data=self.activity_data
                                  )
        self.attr_comparisons = rcond.comparison_criteria
        self.selection_cardinality = rcond.cardinality
        self.sflows = rcond.input_scalar_flows

        Relvar.insert(db=mmdb, tr=tr_Select, relvar='Class_Restriction_Condition', tuples=[
            Class_Restriction_Condition_i(Select_action=self.action_id, Activity=self.anum, Domain=self.domain)
        ])
        # Create output flows
        self.max_mult, self.output_instance_flow = self.populate_multiplicity_subclasses()

        # We now have a transaction with all select-action instances, enter into the metamodel db
        Transaction.execute(db=mmdb, name=tr_Select)  # Select Action

    def identifier_selection(self) -> int:
        """
        | Determine whether we are selecting based on an identifier match.
        An identifier match supplies one value per identifier attribute for some identifier defined on
        the class.
         | Each comparison must be == (equivalence)
         |
         | **For example:**
         |
         | Assume Floor, Shaft is an identifier defined on the Accessible Shaft Level class
         | This means that if you supply a value for each attribute like so
         |
         | Accessible Shaft Level( Floor == x, Shaft == y )
         |
         | you will select at most one instance. But if you select based on:
         |
         | Accessible Shaft Level( Shaft == y )
         |
         | you may select multiple instances since a Shaft intersects multiple Floors
         :returns: An identifier number 1,2, ... or 0 if none found
        """
        idcheck = {c.attr for c in self.attr_comparisons if c.op == '=='}
        R = f"Class:<{self.input_instance_flow.tname}>, Domain:<{self.domain}>"
        Relation.restrict(db=mmdb, relation='Identifier_Attribute', restriction=R)
        Relation.project(db=mmdb, attributes=('Identifier', 'Attribute',), svar_name='all_id_attrs')
        # We have created a named relation with a projection of each id_attr and its id_num
        # Now we must step through each id_num to see if we are selecting on any of them
        i = 1  # Start with inum 1 {I}, (identifier 1). Every class has at least this identifier
        while True:
            # Step through every identifier of the class and see if there is a set of equivalence
            # comparisons that forms a superset of this identifier. If we are selecting at most one instance
            R = f"Identifier:<{str(i)}>"
            t_id_n_attrs = Relation.restrict(db=mmdb, relation='all_id_attrs', restriction=R)
            if not t_id_n_attrs.body:
                # This i num is not defined on the class, no more i nums to check
                break
            t_id_n_attr_names = Relation.project(db=mmdb, attributes=('Attribute',))
            id_n_attr_names = {t['Attribute'] for t in t_id_n_attr_names.body}
            if not id_n_attr_names - idcheck:
                # The set of identifier attributes for the current id number
                # is present in the set of attribute equivalence matches
                # So we are selecting on an identifier and at most one instance can flow out of the selection
                return i
            i += 1  # Increment to the next I num (I1, I2, etc)
        return 0

    def populate_multiplicity_subclasses(self) -> (MaxMult, Flow_ap):
        """
        Determine multiplicity of output and populate the relevant Select Action subclasses
        """
        # Determine if this should be an Identifier Select subclass that yields at most one instance
        selection_idnum = self.identifier_selection()
        if selection_idnum or self.selection_cardinality == 'ONE':
            max_mult = MaxMult.ONE
            # Populate a single instance flow for the selection output
            output_instance_flow = Flow.populate_instance_flow(
                cname=self.input_instance_flow.tname, anum=self.anum, domain=self.domain,
                label=None, single=True
            )
            _logger.info(f"INSERT Select action output single instance Flow: [{self.domain}:"
                         f"{self.input_instance_flow.tname}:{self.activity_data.activity_path.split(':')[-1]}"
                         f":{output_instance_flow}]")
            # Populate the Single Select subclass
            Relvar.insert(db=mmdb, tr=tr_Select, relvar='Single_Select', tuples=[
                Single_Select_i(ID=self.action_id, Activity=self.anum, Domain=self.domain,
                                Output_flow=output_instance_flow.fid)
            ])
            if selection_idnum:
                # Populate an Identifier Select subclass
                Relvar.insert(db=mmdb, tr=tr_Select, relvar='Identifier_Select', tuples=[
                    Identifier_Select_i(ID=self.action_id, Activity=self.anum, Domain=self.domain,
                                        Identifier=selection_idnum, Class=self.input_instance_flow.tname)
                ])
            else:
                # Populate an Identifier Select subclass
                # Note that if both ONE cardinality specified and identifier select, identifier select takes precedence
                Relvar.insert(db=mmdb, tr=tr_Select, relvar='Zero_One_Cardinality_Select', tuples=[
                    Zero_One_Cardinality_Select_i(ID=self.action_id, Activity=self.anum, Domain=self.domain)
                ])
        else:
            # Many select with Multiple Instance Flow output
            max_mult = MaxMult.MANY
            output_instance_flow = Flow.populate_instance_flow(
                cname=self.input_instance_flow.tname, anum=self.anum,
                domain=self.domain, label=None, single=False
            )
            _logger.info(f"INSERT Select action output multiple instance Flow: [{self.domain}:"
                         f"{self.input_instance_flow.tname}:{self.activity_data.activity_path.split(':')[-1]}"
                         f":{output_instance_flow}]")
            # Populate the Many Select subclass
            Relvar.insert(db=mmdb, tr=tr_Select, relvar='Many_Select', tuples=[
                Many_Select_i(ID=self.action_id, Activity=self.anum, Domain=self.domain,
                              Output_flow=output_instance_flow.fid)
            ])
        return max_mult, output_instance_flow
