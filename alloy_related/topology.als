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




/**
	NetElement Assumptions
**/


/*
[0] Every element's relation must reference the latter, 
		implying that relation must be redundant.
*/
pred rule0 {
	relation = ~(elementA+elementB)	
}


// [1] An element can't ever be a recursively part of itself.
pred rule1 {
	no iden & ^elementCollectionUnordered
}


// [2] An element must have at most one parent
pred rule2 {
	all elem: NetElement | lone elem.~elementCollectionUnordered
}


/*
[3] If an element is connected to two different elements in the same endpoint, 
		those must also be connected and their positions must be preserved.
*/
pred rule3 {
	all a,b,c : NetElement, x,y,z : Position | a->x->b->y in elementOn and a->x->c->z in elementOn and (b != c or y != z) implies b->y->c->z in elementOn
}


// [4] An element must be a networkResource of one and only one level
pred rule4 {
	all elem: NetElement | one elem.~networkResource
}


pred NetElementAssumptions {
	rule0
	rule1
	rule2
	rule3
	rule4
}




/**
	NetRelation Assumptions
**/


// [5] A netRelation must be a networkResource of one and only one level
pred rule5 {
	all rel: NetRelation | one rel.~networkResource
}

// [6] Must not exist different relations representing the same relation between elements.
pred rule6 {
	(elementA.~elementA & elementB.~elementB) + (elementA.~elementB & elementB.~elementA) in iden
}


/*
[7] An element can't relate to itself at the same position. 
		So, can't exist a relation with elementA = elementB and positionA = positionB.
*/
pred rule7 {
	no (elementA.~elementB & positionOnA.~positionOnB & iden)
}


/*
[8] Each relation has a set of associated relations, 
		where they relate with each other by having one shared element at the same position. 
		Each relation, on micro level, can either have 1, 2 (switch abstraction) or 5 (double-switch abstraction) associated relations.
*/
pred rule8 {
	all n : descriptionLevel.Micro.networkResource:>NetRelation | #associated[n] < 6 && #associated[n] != 4 && #associated[n] != 3
}

/*
[9] Navigability Property: 
		If 3 relations are associated, one of them must have its navigability to None. 
		If 5 relations are associated, two of them must have its navigability to None
*/
pred rule9 {
	all disj a,b,c: NetRelation | a->b->c in simpleIntersection implies one navigability.None & (a+b+c)
	all disj a,b,c,d,e,f: NetRelation | b->c->d->e->f in doubleIntersection[a] implies #(navigability.None & (a+b+c+d+e+f)) = 2	
}

pred NetRelationsAssumptions {
	rule5
	rule6
	rule7
	rule8
	rule9
}





/**
	Network Assumptions
**/


/*
[10] Elements defined at the Micro level can't be extended by other elements, 
		meaning that elementCollectionUnordered of these elements must be empty.
*/
pred rule10 {
	all n: Network, elem: getElems[n,Micro] | no elem.elementCollectionUnordered
}


/*
[11] Extending every element at the Meso level, they must represent a micro element. 
		 Meaning that, Micro level must be the same as the extended Meso level.
*/
pred rule11 {
	all n: Network | hasLevel[n,Meso] implies {
		getElems[n,Micro] = extend[getLevel[n,Meso]]
		hasLevel[n,Micro] implies no getElems[n,Meso] - getElems[n,Micro].~elementCollectionUnordered
	}
}


/*
[12] Extending every element at the Macro level, 
		 they either represent a meso element or a micro element. 
		 Meaning that, the logic disjunction of both Micro and Meso level must be the same as the extended Macro level.
*/
pred rule12 {	
	all n: Network | hasLevel[n,Macro] implies {
		getElems[n,Micro] + getElems[n,Meso] = extend[getLevel[n,Macro]]
		(hasLevel[n,Micro] or hasLevel[n,Meso]) implies{
	 		no getElems[n,Macro] - (getElems[n,Micro].~elementCollectionUnordered + getElems[n,Meso].~elementCollectionUnordered)
		}
	}
}


// [13] Every relation defined at any level, their corresponding elements must be defined at the same level.
pred rule13 {
	all l: Level | all r: l.networkResource:>NetRelation | r.elementA + r.elementB  in l.networkResource:>NetElement
}


/*
[14] Relations defined at the Micro level, must also be defined at both Meso and Macro levels. 
		 Same for relations defined at the Meso level, which must be defined at the Macro level.
*/
pred rule14 {
	all n: Network | hasLevel[n,Meso] implies {
		relations[getLevel[n,Micro]] in extendRelations[getLevel[n,Meso]]
		hasLevel[n,Micro] implies no relations[getLevel[n,Meso]] - parentRelations[n,Micro]
	}
	all n: Network | hasLevel[n,Macro] implies {
		hasLevel[n,Meso] implies {
			relations[getLevel[n,Meso]] in extendRelations[getLevel[n,Macro]]
			no relations[getLevel[n,Macro]] - parentRelations[n,Meso]
		}
		(hasLevel[n,Micro] and not hasLevel[n,Meso]) implies {
			relations[getLevel[n,Micro]] in extendRelations[getLevel[n,Macro]]
			no relations[getLevel[n,Macro]] - parentRelations[n,Micro]
		}
	}
}



pred NetworkAssumptions {
	rule10
	rule11
	rule12
	rule13
	rule14
}



/**
	Needed facts for alloy
**/

fact networkFacts {
	no Level - Network.level -- every level is associated to a network
	no Network - Level.~level -- every network has at least one level associated
	all l: Level | one l.descriptionLevel -- every level has a descriptionlevel
	all l: Level | some l.networkResource -- every level has networkResources
	all n:Network, l: DescriptionLevel | lone n.level & descriptionLevel.l -- foreach network, we can have at most 1 micro, 1 meso and 1 macro level
}


run Correct{
	NetElementAssumptions
	NetRelationsAssumptions
	NetworkAssumptions
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level


run negRule0{
	not rule0
	rule1
	rule2
	rule3
	rule4
	NetRelationsAssumptions
	NetworkAssumptions
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level


run negRule1{
	rule0
	not rule1
	rule2
	rule3
	rule4
	NetRelationsAssumptions
	NetworkAssumptions
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level



run negRule2{
	rule0
	rule1
	not rule2
	rule3
	rule4
	NetRelationsAssumptions
	NetworkAssumptions
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level


run negRule3{
	rule0
	rule1
	rule2
	not rule3
	rule4
	NetRelationsAssumptions
	NetworkAssumptions
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level


run negRule4{
	rule0
	rule1
	rule2
	rule3
	not rule4
	NetRelationsAssumptions
	NetworkAssumptions
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level


run negRule5{
	NetElementAssumptions
	not rule5
	rule6
	rule7
	rule8
	rule9
	NetworkAssumptions
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level



run negRule6{
	NetElementAssumptions
	rule5
	not rule6
	rule7
	rule8
	rule9
	NetworkAssumptions
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level


run negRule7{
	NetElementAssumptions
	rule5
	rule6
	not rule7
	rule8
	rule9
	NetworkAssumptions
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level


run negRule8{
	NetElementAssumptions
	rule5
	rule6
	rule7
	not rule8
	rule9
	NetworkAssumptions
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level


run negRule9{
	NetElementAssumptions
	rule5
	rule6
	rule7
	rule8
	not rule9
	NetworkAssumptions
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level


run negRule10{
	NetElementAssumptions
	NetRelationsAssumptions
	not rule10
	rule11
	rule12
	rule13
	rule14
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level


run negRule11{
	NetElementAssumptions
	NetRelationsAssumptions
	rule10
	not rule11
	rule12
	rule13
	rule14
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level


run negRule12{
	NetElementAssumptions
	NetRelationsAssumptions
	rule10
	rule11
	not rule12
	rule13
	rule14
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level


run negRule13{
	NetElementAssumptions
	NetRelationsAssumptions
	rule10
	rule11
	rule12
	not rule13
	rule14
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level


run negRule14{
	NetElementAssumptions
	NetRelationsAssumptions
	rule10
	rule11
	rule12
	rule13
	not rule14
} for exactly 12 NetElement, exactly 6 NetRelation, exactly 1 Network, exactly 3 Level



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
	//{disj a,b,c: NetRelation | b in a.associated and c in a.associated and b in c.associated}
	{disj a,b,c: NetRelation | a->b + a->c in associated}
}


fun doubleIntersection[a: NetRelation]: NetRelation -> NetRelation -> NetRelation -> NetRelation -> NetRelation {
	{disj b,c,d,e,f: NetRelation {
			a->b + a->c + a->d + a->e + a->f in associated
	 		/*
			b in a.associated and c in a.associated and d in a.associated and e in a.associated and f in a.associated
			c in b.associated and d in b.associated and e in b.associated and f in b.associated
			d in c.associated and e in c.associated and f in c.associated
			e in d.associated and f in d.associated
			f in e.associated
		  */
		}
	}
}



// Extends a level relating it with every element they have, considering elementCollectionUnordered
fun extend: Level -> NetElement {
	{ l: Level, n: NetElement | n in l.networkResource.^elementCollectionUnordered }
}



/*
	Every pair of elements that are related in some level.
	Two elements are related iff:
		- they both have the same parent (considering elementCollectionUnordered)
		- there is a relation between them or between their parents (considering elementCollectionUnordered)
*/
fun extendRelations[l:Level] : NetElement -> NetElement {
	{ a, b: NetElement {
			some e: l.networkResource:>NetElement | a + b in e.elementCollectionUnordered or
			some r: l.networkResource:>NetRelation, e1, e2: l.networkResource:>NetElement {
				(e1 = r.elementA and e2 = r.elementB) or (e1 = r.elementB and e2 = r.elementA)
				a in e1.elementCollectionUnordered
				b in e2.elementCollectionUnordered
			}
		}
	}
}


fun relations[l:Level]: NetElement -> NetElement {
	{a,b: NetElement | some r: l.networkResource:>NetRelation | (a = r.elementA and b = r.elementB) or (a = r.elementB and b = r.elementA)}
}


fun getLevel[n:Network, d:DescriptionLevel] : Level{
	n.level & descriptionLevel.d
}

fun getElems[n:Network, d:DescriptionLevel] : NetElement{
	getLevel[n,d].networkResource:>NetElement
}


fun parentRelations[n:Network, d: DescriptionLevel] : NetElement -> NetElement {
	{a,b: NetElement | some e: a.elementCollectionUnordered, f: b.elementCollectionUnordered | e->f in relations[getLevel[n,d]]}
}
