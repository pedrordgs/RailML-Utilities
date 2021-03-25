/*****
	Topology model for the rule validation tool

	Ids and Refs factored out
	We assume the XML obbeys referential integrity
*****/

module topology
open common
open util/natural as nat

// https://wiki3.railml.org/wiki/IS:netElement
some sig NetElement {
	// Attributes 
	length : lone Natural, 	// length of the NetElement in metres
	// Children
	relation : set NetRelation // NetRelations of a NetElement
	// Irrelevant children
	-- associatedPositioningSystem : one AssociatedPositioningSystem,
	-- elementCollectionOrdered : seq NetElement,
	-- elementCollectionUnordered : set NetElement,
	-- isValid : set IsValid,
	-- name : set Name	
}

fact NetElement {
	// Assumptions
	-- All NetLengths must have length
	all n : NetElement | some n.length
	-- Relation is redundant
	relation = ~(elementA+elementB)
}

// https://wiki3.railml.org/wiki/IS:netRelation
sig NetRelation {
	// Attributes
	navigability : lone Navigability,	// Navigability
	positionOnA : one Zero+One, 		// position on element A
	positionOnB : one Zero+One,		// position on element B
	// Children
	elementA : one NetElement,		// NetElement A
	elementB : one NetElement,		// NetElement B
	// Irrelevant children
	-- isValid : set IsValid
	-- name : set Name	
}

// Navigability options
abstract sig Navigability {}
one sig None, Both, AB, BA extends Navigability {}

// View relation
// Elements connected to end positions
fun elementOn : NetElement -> Natural -> NetElement {
	{ a : NetElement, p : Natural, b : NetElement | 
		some r : NetRelation {
			r.elementA = a and p = mul[r.positionOnA,a.length] and r.elementB = b or
			r.elementB = a and p = mul[r.positionOnB,a.length] and r.elementA = b
		}
	}
}

// View relation
// Adjacent elements
fun adjacent : NetElement -> NetElement {
	relation.~relation - iden
}

fact Topology {
	// Assumptions
	-- If a NetElement is connected to two different NetElements in same endpoint, those must also be connected
	all a : NetElement, disj c,b : a.elementOn[Natural] | c in b.elementOn[b.elementOn.a]
}

// https://wiki3.railml.org/wiki/IS:network
some sig Network {
	// Attributes
	// Children
	level : some Level,								// views of the newtwork at different abstraction levels
	// Irrelevant children
	-- networkResource : set NetElement+NetRelation,	// resources common to all views
	-- name : set Name								// option set of names
}

// https://wiki3.railml.org/wiki/RTM:level
sig Level {
	// Attributes
	descriptionLevel : lone DescriptionLevel,			// level of the network
	// Children
	networkResource : set NetElement+NetRelation	// resources at the level
}

// Possible description levels
enum DescriptionLevel {Micro, Meso, Macro}

fact Network {
	// Assumptions
	one Network
	one Level
	one Network.level
	Network.level.descriptionLevel = Micro
	Network.level.networkResource = NetElement+NetRelation
}
