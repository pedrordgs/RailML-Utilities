module topology
 -- open util/natural as nat

/**
	RailML topology
**/


/* https://wiki3.railml.org/wiki/IS:netElement */
some sig NetElement {
	// Atributes
	-- length: lone Natural, // in meters but can be decimal (?)
	-- id: one Id,

	// Children
	relation: set NetRelation,
	-- associatedPositionSystem: set AssociatedPositionSystem,
	-- elementCollectionOrdered: seq NetElement,
	elementCollectionUnordered: set NetElement
	-- isValid: set Validation,
	-- name: set Name,
}

pred NetElementAssumptions {
	-- Relation is redundant
	relation = ~(elementA+elementB)
	-- there are no loops on elementCollectionUnordered
	no iden & ^elementCollectionUnordered
}


// Possible navigability values
abstract sig Navigability {}
one sig None, Both, AB, BA extends Navigability {}

// Possible positioning values
abstract sig Position {}
one sig Zero, One extends Position {}

/* https://wiki3.railml.org/wiki/IS:netRelation */
sig NetRelation {
	// Atributes
	navigability: one Navigability,
	positionOnA: one Position,
	positionOnB: one Position,
	-- id: one Id

	// Children
	elementA: one NetElement,
	elementB: one NetElement
	-- isValid: set Validation,
	-- name: set Name,
}

/* Create a set of NetRelations related to one NetRelation */
fun associated: NetRelation -> NetRelation {
	/* Associated on element A */
	((elementA.~elementA & positionOnA.~positionOnA) - iden)
	+
	/* Associated on element B */
	((elementB.~elementB & positionOnB.~positionOnB) - iden)
	+
	/* Element A on one, is the Element B on the other */
	((elementA.~elementB & positionOnA.~positionOnB) - iden)
	+
	/* Element A on one, is the Element B on the other */
	((elementB.~elementA & positionOnB.~positionOnA) - iden)
}


fun elementOn : NetElement -> Position -> NetElement -> Position {
	{ a : NetElement, pa : Position, b : NetElement, pb : Position |
		some r : NetRelation {
			r.elementA = a and pa = r.positionOnA and r.elementB = b and pb = r.positionOnB or
			r.elementB = a and pa = r.positionOnB and r.elementA = b and pb = r.positionOnA
		}
	}
}


// Extends a level relating it with every element they have, considering elementCollectionUnordered
fun extend: Level -> NetElement {
	{ l: Level, n: NetElement | n in l.networkResource or n in l.networkResource.^elementCollectionUnordered }
}

// Adjacent elements
fun adjacent : NetElement -> NetElement {
	relation.~relation - iden
}

/*
	Every pair of elements that are related in some level.
	Two elements are related iff:
		- they both have the same parent (considering elementCollectionUnordered)
		- there is a relation between them or between their parents (considering elementCollectionUnordered)
*/
fun relatedOn: Level -> NetElement -> NetElement {
	{ l: Level, disj a, b: NetElement {
			some e: l.networkResource:>NetElement | a + b in e.^elementCollectionUnordered or
			some r: l.networkResource:>NetRelation, disj e1, e2: l.networkResource:>NetElement {
				r in e1.relation & e2.relation and
				a in e1.*elementCollectionUnordered and
				b in e2.*elementCollectionUnordered
			}
		}
	}
}


pred TopologyAssumptions {
	/* ASSUMPTIONS */

	-- If a NetElement is connected to two different NetElements in same endpoint, those must also be connected
	all a,b,c : NetElement, x,y,z : Position | a->x->b->y in elementOn and a->x->c->z in elementOn and (b != c or y != z) implies b->y->c->z in elementOn

	-- Can't exist more than 1 netRelation with the same elementA and elementB. Se for circular deve ser considerado a mesma NetRelation.
	(elementA.~elementA & elementB.~elementB) + (elementA.~elementB & elementB.~elementA) in iden

	-- If 3 elements are connected in a endpoint, then its a switch, meaning navigability must be none in 1 out of 3.
	-- Esta regra será definida quando forem implementados os switch
	-- all n : NetRelation | n.navigability = None iff (n.positionOnA = n.positionOnB)

	-- No relations with elementA = elementB and positionA = positionB. As raquetes devem ter as positions de A e B diferentes.
	no (elementA.~elementB & positionOnA.~positionOnB & iden)

	-- All associated relations must have less than 6 relations with others. 6 net relations associated (associated[n] = 5) means that we have a double switch.
	-- However, we cant have 5 or 4 netRelations associated.
 	-- Esta regra será definida quando forem implementados os switch
	-- all n : NetRelation | #associated[n] < 6 && #associated[n] != 4 && #associated[n] != 3


	-- If all elementCollectionUnordered need to be defined on lower levels
	all n: Network, nelem: (n.level & descriptionLevel.Meso).networkResource & NetElement {
		nelem.elementCollectionUnordered in (n.level & descriptionLevel.Micro).networkResource
	}

	all n: Network, nelem: (n.level & descriptionLevel.Macro).networkResource & NetElement {
		nelem.elementCollectionUnordered in (n.level & descriptionLevel.(Micro+Meso)).networkResource
	}


	-- Micro elements need to be on meso and macro elements, fails when there isn't a Meso or Macro level
	all n: Network | some n.level & descriptionLevel.Meso implies {
		 extend[n.level & descriptionLevel.Micro] in extend[n.level & descriptionLevel.Meso]
	}
	all n: Network | some n.level & descriptionLevel.Macro implies {
		 extend[n.level & descriptionLevel.Micro] in extend[n.level & descriptionLevel.Macro] and
		 extend[n.level & descriptionLevel.Meso] in extend[n.level & descriptionLevel.Macro]
	}

	-- If two elements are related on micro, they are related on meso and macro too
	all n: Network | some n.level & descriptionLevel.Meso implies {
		 relatedOn[n.level & descriptionLevel.Micro] in relatedOn[n.level & descriptionLevel.Meso]
	}
	all n: Network | some n.level & descriptionLevel.Macro implies {
		 relatedOn[n.level & descriptionLevel.Micro] in relatedOn[n.level & descriptionLevel.Macro] and
		 relatedOn[n.level & descriptionLevel.Meso] in relatedOn[n.level & descriptionLevel.Macro]
	}
}


/* https://wiki3.railml.org/wiki/IS:network */
some sig Network {
	level : some Level,								// Network at different abstraction levels
}

/* https://wiki3.railml.org/wiki/RTM:level */
sig Level {
	// Attributes
	descriptionLevel : lone DescriptionLevel,			// level of the network
	// Children
	networkResource : set NetElement+NetRelation	// resources at the level
}

/* Possible description levels */
abstract sig DescriptionLevel {}
one sig Micro, Meso, Macro extends DescriptionLevel {}

pred NetworkAssumptions {
	// Assumptions
	all n:Network, l: DescriptionLevel | lone n.level & descriptionLevel.l -- foreach network, we can have at most 1 micro, 1 meso and 1 macro level
	no Level - Network.level -- every level is associated to a network
	no Network - Level.~level -- every network has at least one level associated
	-- if some netRelation is a networkResource of a level, then its elements need to be a networkResource of the same level
	all l: Level | all r: l.networkResource:>NetRelation | r.elementA + r.elementB  in l.networkResource:>NetElement
	-- An element inside another element can't be a netResource of the same level
	all l: Level | all disj a, b: l.networkResource:>NetElement | no a & b.elementCollectionUnordered
}

run{
	NetElementAssumptions
	TopologyAssumptions
	NetworkAssumptions
	no (NetElement+NetRelation) - Level.networkResource -- every netelement and netrelation is a networkResource
	all l: Level | one l.descriptionLevel -- every level has a descriptionlevel
	all l: Level | some l.networkResource -- every level has networkResources
	-- higher levels have more extended elements
	all n: Network {
		some extend[n.level & descriptionLevel.Macro] - extend[n.level & descriptionLevel.Micro] and
		some extend[n.level & descriptionLevel.Macro] - extend[n.level & descriptionLevel.Meso] and
		some extend[n.level & descriptionLevel.Meso] - extend[n.level & descriptionLevel.Micro]
	}
	no iden & elementA.~elementB -- no rackets
	some elementCollectionUnordered
} for exactly 5 NetElement, exactly 5 NetRelation, exactly 1 Network, exactly 3 Level
