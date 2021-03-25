module topology

/**
	RailML topology
**/


// https://wiki3.railml.org/wiki/IS:netElement
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


// https://wiki3.railml.org/wiki/IS:netRelation
sig NetRelation {
	// Atributes
	navigability: lone Navigability,
	positionOnA: lone Positioning,
	positionOnB: lone Positioning,
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

fun elementOn: NetElement -> Positioning -> NetElement {
	{a: NetElement, p: Positioning, b: NetElement |
		some r: NetRelation {
			a = r.elementA and p = r.positionOnA and b = r.elementB or
			a = r.elementB and p = r.positionOnB and b = r.elementB
		}
	}
}

// https://wiki3.railml.org/wiki/IS:network
sig Network {
	// Atributes
	-- id: one Id

	// Children
	-- level: some Level
	-- name: set Name,
	-- networkResource: set NetElement+NetRelation
}


fact Topology {
	// Assumptions
	-- If a NetElement is connected to two different NetElements in same endpoint, those must also be connected
	all a: NetElement, disj b,c: Positioning.(a.elementOn) | a.elementOn.b = a.elementOn.c implies some b.elementOn.c
}

run{
} for exactly 5 NetElement, 5 NetRelation, 1 Network

