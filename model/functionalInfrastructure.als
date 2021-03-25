/*****
	Functional infrastructure model for the rule validation tool

	Ids and Refs factored out
	We assume the XML obbeys referential integrity
*****/

module functionalInfrastructure
open topology
open util/natural as nat

// All things that can be positioned on net elements
-- How to name this?
abstract sig Element {
	// Children
	spotLocation : set SpotLocation,
	// View relation
	distance : Natural -> Element
}

fact Element {
	// Assumptions
	-- RaIL-AiD: All signals have exactly one spot location
	all s : Element | one s.spotLocation
	-- All signals have the position defined
	all s : Element | one s.spotLocation.pos
	-- Position makes sense
	all s : Element | nat/lte[s.spotLocation.pos, s.spotLocation.netElementRef.length]
}

// Distance is the shortest path length
// Assumes network is connected
fact Distance {
	all x,y : Element | 
	some x.adjacent.y 
	implies {
		x.distance.y = min[x.adjacent.y]
	} else {
		some z : x.adjacent[Natural] - x | x.distance.y = add[min[x.adjacent.z], z.distance.y]
		all z : x.adjacent[Natural] - x | lte[x.distance.y, add[min[x.adjacent.z], z.distance.y]]
	}
}

// https://wiki3.railml.org/wiki/RTM:spotLocation
sig SpotLocation {
	// Attributes
	netElementRef : one NetElement, 	// NetElement where the signal is located
	pos : lone Natural			// Position on the net element
	// Irrelevant attributes
	-- applicationDirection : lone ApplicationDirection
	
}

// View relation
-- Position of elements on net elements
fun position : Element -> Natural -> NetElement {
	{ e : Element, p : Natural, n : NetElement | 
		(p = e.spotLocation.pos and n = e.spotLocation.netElementRef)
		or
		(n in e.spotLocation.netElementRef.elementOn[e.spotLocation.pos] and p in n.elementOn.(e.spotLocation.netElementRef)) }
}

// View relation
-- Net elements where elements are located
fun location : Element -> NetElement {
	{ e : Element, n : e.position[Natural] }
} 

// View relation
-- Elements located in the same net element (and the respective distance)
fun adjacent : Element -> Natural -> Element {
	{ x : Element, n : Natural, y : Element | 
		some l : x.location & y.location {
			some px : x.position.l, py : y.position.l | n = sub[max[px+py],min[px+py]]
		}
	}
}

// View relation
-- The closest adjacent elements
fun prox : Element -> Element {
	{ x : Element, y : Element | some l : x.location & y.location, px : x.position.l, py : y.position.l | py = min[Element.position.l - px.*nat/prev] or py = max[Element.position.l - px.*nat/next] }
}

// https://wiki3.railml.org/wiki/IS:signalIS
sig SignalIS extends Element {
	// Attributes

	// Irrelevant attributes
	-- belongsToParent : lone SignalIS
	-- basedOnTemplate : lone SignalIS

	// Children
}

// Boolean attributes
sig isSwitchable in SignalIS {}

// Types of signals
-- marked with children elements in railML, assuming they are exclusive
-- many still missing
-- can all of them be switchable?
sig isDangerSignal, isInformationSignal, isMilePost, isSpeedSignal extends SignalIS {}	

// https://wiki3.railml.org/wiki/IS:switchIS
sig SwitchIS extends Element {
	// Attributes
	continueCourse : lone Direction,
	branchCourse : lone Direction,
	
	// Irrelevant attributes
	-- type : lone SwitchISType
	-- belongsToParent : lone SwitchIS
	-- basedOnTemplate : lone SwitchIS

	// Children
	leftBranch : lone Branch,
	rightBranch : lone Branch

	// Irrelevant children
	-- straightBranch : set Branch
	-- turningBranch : set Branch
}

abstract sig Direction {}
one sig Left, Right extends Direction {}

// https://wiki3.railml.org/wiki/IS:leftBranch
// https://wiki3.railml.org/wiki/IS:rightBranch
// https://wiki3.railml.org/wiki/IS:straightBranch
// https://wiki3.railml.org/wiki/IS:turningBranch
sig Branch {
	// Attributes
	netRelationRef : one NetRelation

	// Irrelevant attributes
	-- branchingSpeed : lone Natural
	-- joiningSpeed : lone Natural
	-- radius : lone Natural
	-- length	: lone Natural
}

// View relation
-- Assumes switch is located in the net element facing it
fun branch : SwitchIS -> Direction -> NetElement {
	{ s : SwitchIS, d : Left, n : s.leftBranch.netRelationRef.(elementA+elementB) - s.spotLocation.netElementRef } +
	{ s : SwitchIS, d : Right, n : s.rightBranch.netRelationRef.(elementA+elementB) - s.spotLocation.netElementRef }
}


fact SwitchIS {
	// Assumptions
	all s : SwitchIS {
		-- Switches are at the end of net elements
		s.spotLocation.pos = Zero or s.spotLocation.pos = s.spotLocation.netElementRef.length
		-- Continue and branch course are mandatory
		some s.continueCourse
		some s.branchCourse
		some s.leftBranch
		some s.rightBranch
		-- Branch course is redundant
		s.branchCourse = Direction - s.continueCourse
	}
}

// https://wiki3.railml.org/wiki/IS:bufferStop
sig BufferStop extends Element {}

fact BufferStop {
	// Assumptions
	-- Buffer stops are at the end of net elements
	all s : BufferStop | s.spotLocation.pos = Zero or s.spotLocation.pos = s.spotLocation.netElementRef.length
}


/***** Rule examples *****/

// Distances

-- Signals must be at least 5m appart
pred signalToSignal {
	all disj x,y : SignalIS | gte[x.distance.y,Five]
}

-- Signals must be at least 2m appart from switches
pred signalToSwitch {
	all x : SignalIS, y : SwitchIS | gte[x.distance.y,Two]
}

// Coverage


// Existence

-- In all netElements connected to a switch there must be a signal at most 3m away
pred switchRequiresSignals {
	all s : SwitchIS, n : s.location | some x : SignalIS & location.n | lte[s.distance.x,Three]
}

-- Between a buffer stop and a switch there must exist a signal
pred signalInBetween {
	all b : BufferStop, s : SwitchIS | some SignalIS & (b.^prox & ^prox.s) and some SignalIS & (s.^prox & ^prox.b)
}

check Subsumes {
	switchRequiresSignals implies signalInBetween
} for 5

/***** Network examples *****/

let Two { One.nat/next }
let Three { Two.nat/next }
let Four { Three.nat/next }
let Five { Four.nat/next }

/* Example of network with just one switch, two signals, and three buffer stops
a1 --s1---
          \
           w ----s2--- a3
          /
a2 -------
*/

pred oneSwitch {
	some
	disj a1,a2,a3 : NetElement, 
	disj a1a2, a1a3, a2a3 : NetRelation,
	disj s1,s2 : SignalIS,
	disj w : SwitchIS,
	disj b1,b2,b3 : BufferStop
	{
	NetElement = a1+a2+a3
	a1.length = Three
	a2.length = Two
	a3.length = Four
	NetRelation = a1a2+a1a3+a2a3
	a1a2.navigability = None
	a1a2.positionOnA = One
	a1a2.positionOnB = One
	a1a2.elementA = a1
	a1a2.elementB = a2
	a1a3.navigability = Both
	a1a3.positionOnA = One
	a1a3.positionOnB = Zero
	a1a3.elementA = a1
	a1a3.elementB = a3
	a2a3.navigability = Both
	a2a3.positionOnA = One
	a2a3.positionOnB = Zero
	a2a3.elementA = a2
	a2a3.elementB = a3
	SignalIS = s1+s2
	s1.spotLocation.netElementRef = a1
	s1.spotLocation.pos = One
	s2.spotLocation.netElementRef = a3
	s2.spotLocation.pos = Two
	isSwitchable = s1
	SwitchIS = w
	w.spotLocation.netElementRef = a3
	w.spotLocation.pos = Zero
	w.continueCourse = Right
	w.rightBranch.netRelationRef = a1a3
	w.leftBranch.netRelationRef = a2a3
	BufferStop = b1+b2+b3
	b1.spotLocation.netElementRef = a1
	b1.spotLocation.pos = Zero
	b2.spotLocation.netElementRef = a2
	b2.spotLocation.pos = Zero
	b3.spotLocation.netElementRef = a3
	b3.spotLocation.pos = Four
	}
}
run oneSwitch for 6 but 10 Natural

pred racket {
	some 
	disj a1,a2 : NetElement,
	disj a1a20,a1a21,a20a21 : NetRelation,
	w : SwitchIS,
	b : BufferStop,
	s : SignalIS
	{
	NetElement = a1+a2
	NetRelation = a1a20+a1a21+a20a21
	SwitchIS = w
	BufferStop = b
	SignalIS = s
	a1.length = Two
	a2.length = Four
	a1a20.navigability = Both
	a1a20.elementA = a1
	a1a20.positionOnA = One
	a1a20.elementB = a2
	a1a20.positionOnB = Zero
	a1a21.navigability = Both
	a1a21.elementA = a1
	a1a21.positionOnA = One
	a1a21.elementB = a2
	a1a21.positionOnB = One
	a20a21.navigability = None
	a20a21.elementA = a2
	a20a21.positionOnA = Zero
	a20a21.elementB = a2
	a20a21.positionOnB = One
	w.spotLocation.netElementRef = a1
	w.spotLocation.pos = Two
	w.continueCourse = Right
	w.rightBranch.netRelationRef = a1a21
	w.leftBranch.netRelationRef = a1a20
	b.spotLocation.netElementRef = a1
	b.spotLocation.pos = Zero
	s.spotLocation.netElementRef = a2
	s.spotLocation.pos = One
	}
}
run racket for 5 but 8 Natural
