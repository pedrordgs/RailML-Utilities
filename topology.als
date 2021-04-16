module topology
 -- open util/natural as nat

/**
	RailML topology
**/


/* https://wiki3.railml.org/wiki/IS:netElement */
sig NetElement {
	// Atributes
	-- length: lone Natural, // in meters but can be decimal (?)
	-- id: one Id,

	// Children
	relation: set NetRelation
	-- associatedPositionSystem: set AssociatedPositionSystem,
	-- elementCollectionOrdered: seq NetElement,
	-- elementCollectionUnordered: set NetElement,
	-- isValid: set Validation,
	-- name: set Name,
}

fact NetElement {
	-- Relation is redundant
	relation = ~(elementA+elementB)
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

fun elementOn: NetElement -> Position -> NetElement {
	{a: NetElement, p: Position, b: NetElement |
		some r: NetRelation {
			a = r.elementA and p = r.positionOnA and b = r.elementB or
			a = r.elementB and p = r.positionOnB and b = r.elementB
		}
	}
}

// Adjacent elements
fun adjacent : NetElement -> NetElement {
	relation.~relation - iden
}

fact Topology {
	/* ASSUMPTIONS */

	-- If a NetElement is connected to two different NetElements in same endpoint, those must also be connected
	all a: NetElement, disj b,c: Position.(a.elementOn) | a.elementOn.b = a.elementOn.c implies some b.elementOn.c

	-- Can't exist 2 NetRelations with the same elementA and elementB. Se for circular deve ser considerado a mesma NetRelation.
	(elementA.~elementA & elementB.~elementB) in iden /* ker<elementA,elementB> in iden */

	-- If 3 elements are connected in a endpoint, then its a switch, meaning navigability must be none in 1 out of 3.
	all n : NetRelation | n.navigability = None iff (n.positionOnA = n.positionOnB)

	-- No relations with elementA = elementB.
	/* no (elementA.~elementB & iden) → False, Raquetes (navigabilidade raquetes?) */

	-- No relations with elementA = elementB and positionA = positionB. As raquetes devem ter as positions de A e B diferentes.
	no (elementA.~elementB & positionOnA.~positionOnB & iden)

	-- All associated relations must have less than 6 relations with others. 6 net relations associated (associated[n] = 5) means that we have a double switch.
	-- However, we cant have 5 or 4 netRelations associated.
	all n : NetRelation | #associated[n] < 6 && #associated[n] != 4 && #associated[n] != 3
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
enum DescriptionLevel {Micro, Meso, Macro}

fact Network {
	// Assumptions
	one Network
	one Level
	one Network.level
	Network.level.descriptionLevel = Micro
	Network.level.networkResource = NetElement+NetRelation
}

/*
	abstract sig Level {}
	one sig Micro, Meso, Macro extends Level {}
*/

run{
} for exactly 5 NetElement, 5 NetRelation, 1 Network, 1 Level

