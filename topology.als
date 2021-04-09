module topology
open util/natural as nat

/**
	RailML topology
**/


// https://wiki3.railml.org/wiki/IS:netElement
sig NetElement {
	// Atributes
	length: lone Natural, // in meters but can be decimal (?)
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

// https://wiki3.railml.org/wiki/IS:netRelation
sig NetRelation {
	// Atributes
	navigability: one Navigability,
	positionOnA: one Positioning,
	positionOnB: one Positioning,
	-- id: one Id

	// Children
	elementA: one NetElement,
	elementB: one NetElement
	-- isValid: set Validation,
	-- name: set Name,
}

// Possible navigability values
abstract sig Navigability {}
one sig None, Both, AB, BA extends Navigability {}

// Possible positioning values
abstract sig Positioning {}
one sig Zero, One extends Positioning {}



// https://wiki3.railml.org/wiki/IS:network
sig Network {
	// Atributes
	-- id: one Id

	// Children
	level: some Level
	-- name: set Name,
	-- networkResource: set NetElement+NetRelation
}


abstract sig Level {}
one sig Micro, Meso, Macro extends Level {}

fun elementOn : NetElement -> Positioning -> NetElement {
	{ a : NetElement, p : Positioning, b : NetElement | 
		some r : NetRelation {
			r.elementA = a and p = r.positionOnA and r.elementB = b or
			r.elementB = a and p = r.positionOnB and r.elementA = b
		}
	}
}


fact Topology {
	// Assumptions
	-- If a NetElement is connected to two different NetElements in same endpoint, those must also be connected
	all a: NetElement, disj b,c: a.elementOn[Positioning] | c in b.elementOn[b.elementOn.a]
	
}

run{
} for exactly 5 NetElement, 5 NetRelation, 1 Network








