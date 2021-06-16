module topology

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




pred NetElementAssumptions {
	-- [0] Every element's relation must reference the latter, implying that relation must be redundant.
	relation = ~(elementA+elementB)	
	-- [1] An element can't ever be a recursively part of itself.
	no iden & ^elementCollectionUnordered
	-- [2] If an element is connected to two different elements in the same endpoint, those must also be connected and their positions must be preserved.
	all a,b,c : NetElement, x,y,z : Position | a->x->b->y in elementOn and a->x->c->z in elementOn and (b != c or y != z) implies b->y->c->z in elementOn
}


pred NetRelationsAssumptions {
	-- [3] Must not exist different relations representing the same relation between elements.
	(elementA.~elementA & elementB.~elementB) + (elementA.~elementB & elementB.~elementA) in iden
	-- [4] An element can't relate to itself at the same position. So, can't exist a relation with elementA = elementB and positionA = positionB.
	no (elementA.~elementB & positionOnA.~positionOnB & iden)
	-- [5] Each relation has a set of associated relations, where they relate with each other by having one shared element at the same position. Each relation can either have 1, 2 (switch abstraction) or 5 (double-switch abstraction) associated relations.
	all n : NetRelation | #associated[n] < 6 && #associated[n] != 4 && #associated[n] != 3
	-- [6] Navigability Property: If 3 relations are associated, one of them must have its navigability to None. If 5 relations are associated, two of them must have its navigability to None
	all disj a,b,c: NetRelation | a->b->c in simpleIntersection implies one navigability.None & (a+b+c)
	all disj a,b,c,d,e,f: NetRelation | b->c->d->e->f in doubleIntersection[a] implies #(navigability.None & (a+b+c+d+e+f)) = 2	
}


pred NetworkAssumptions {
	-- [7] Elements defined at the Micro level can't be extended by other elements, meaning that elementCollectionUnordered of these elements must be empty.
	all n: Network, elem: (n.level & descriptionLevel.Micro).networkResource:>NetElement | no elem.elementCollectionUnordered
	-- [8] Extending every element at the Meso level, they must represent a micro element. Meaning that, Micro level must be the same as the extended Meso level.
	all n: Network | hasLevel[n,Micro] and hasLevel[n,Meso] implies {
		 inside[n.level & descriptionLevel.Micro,n.level & descriptionLevel.Meso]
		 extend[n.level & descriptionLevel.Meso] in (n.level & descriptionLevel.Micro).networkResource
	}

	-- [9] Extending every element at the Macro level, they either represent a meso element or a micro element. Meaning that, the logic disjunction of both Micro and Meso level must be the same as the extended Macro level.
	all n: Network | (hasLevel[n,Micro] or hasLevel[n,Meso]) and hasLevel[n,Macro] implies {
		 extend[n.level & descriptionLevel.Macro] in (n.level & descriptionLevel.(Micro+Macro)).networkResource
		 hasLevel[n,Micro] implies inside[n.level & descriptionLevel.Micro,n.level & descriptionLevel.Macro]
		 hasLevel[n,Meso] implies inside[n.level & descriptionLevel.Meso,n.level & descriptionLevel.Macro]
	}

	-- [10] Every relation defined at any level, their corresponding elements must be defined at the same level.
	all l: Level | all r: l.networkResource:>NetRelation | r.elementA + r.elementB  in l.networkResource:>NetElement
	-- [11] Relations defined at the Micro level, must also be defined at both Meso and Macro levels. Same for relations defined at the Meso level, which must be defined at the Macro level.
	all n: Network | hasLevel[n,Micro] and hasLevel[n,Meso] implies {
		 relatedOn[n.level & descriptionLevel.Micro] in relatedOn[n.level & descriptionLevel.Meso]
	}
	all n: Network | (hasLevel[n,Micro] or hasLevel[n,Meso]) and hasLevel[n,Macro] implies {
		 relatedOn[n.level & descriptionLevel.Micro] + relatedOn[n.level & descriptionLevel.Meso] in relatedOn[n.level & descriptionLevel.Meso]
	}


	-- foreach network, we can have at most 1 micro, 1 meso and 1 macro level
	all n:Network, l: DescriptionLevel | lone n.level & descriptionLevel.l
	-- An element inside another element can't be a netResource of the same level
	all l: Level | all disj a, b: l.networkResource:>NetElement | no a & b.elementCollectionUnordered
}


run{
	NetElementAssumptions
	NetRelationsAssumptions
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



fact networkFacts {
	no Level - Network.level -- every level is associated to a network
	no Network - Level.~level -- every network has at least one level associated
}





pred hasLevel[n:Network, d: DescriptionLevel]{
	one n.level & descriptionLevel.d
}


fun elementOn : NetElement -> Position -> NetElement -> Position {
	{ a : NetElement, pa : Position, b : NetElement, pb : Position |
		some r : NetRelation {
			r.elementA = a and pa = r.positionOnA and r.elementB = b and pb = r.positionOnB or
			r.elementB = a and pa = r.positionOnB and r.elementA = b and pb = r.positionOnA
		}
	}
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



fun simpleIntersection: NetRelation -> NetRelation -> NetRelation {
	{disj a,b,c: NetRelation | b in a.associated and c in a.associated and b in c.associated}
}


fun doubleIntersection[a: NetRelation]: NetRelation -> NetRelation -> NetRelation -> NetRelation -> NetRelation {
	{disj b,c,d,e,f: NetRelation {
	 		b in a.associated
			c in a.associated
			d in a.associated
			e in a.associated
			f in a.associated
			c in b.associated
			d in b.associated
			e in b.associated
			f in b.associated
			d in c.associated
			e in c.associated
			f in c.associated
			e in d.associated
			f in d.associated
			f in e.associated
		}
	}
}



// Extends a level relating it with every element they have, considering elementCollectionUnordered
fun extend: Level -> NetElement {
	{ l: Level, n: NetElement | n in l.networkResource.^elementCollectionUnordered }
}

pred inside[a: Level, b: Level]{
	a.networkResource:>NetElement in b.networkResource.*elementCollectionUnordered
}


/*
	Two elements are extended related iff:
		- they both have the same parent (considering elementCollectionUnordered)
		- there is a relation between their parents (considering elementCollectionUnordered)
*/
fun relatedOn[l:Level] : NetElement -> NetElement {
	{ disj a, b: NetElement {
			some e: l.networkResource:>NetElement | a + b in e.^elementCollectionUnordered or
			some r: l.networkResource:>NetRelation, disj e1, e2: l.networkResource:>NetElement {
				r in e1.relation & e2.relation and
				a in e1.*elementCollectionUnordered and
				b in e2.*elementCollectionUnordered
			}
		}
	}
}

