abstract sig Direction {}
one sig Right, Left extends Direction {}


sig NetElement {
	relation: set NetRelation
}

sig NetRelation {
	elementA: one NetElement,
	elementB: one NetElement
}

sig Line {
	beginOp: one OperationalPoint,
	endOp: one OperationalPoint,
	associatedNetElements set NetElement
}

sig Switch in NetElement {
	leftBranch: one Direction,
	rightBranch: one Direction,
	defaultCourse: one Direction,
	branchCourse: one Direction
}

sig BufferStop in NetElement {}

sig Track {
	trackBegin: one NetElement,
	trackEnd: one NetElement,
	associatedNetElement: set NetElement
}

sig OperationalPoint {
	platform: set Platform
}

sig Platform in NetElement { // in NetElement ??
	platformEdges: set Platform,
	associatedNetElement: set NetElement
}

sig LevelCrossing in NetElement {} // maybe need track

sig Signal in NetElement {} // maybe need track

sig TrainDetection in NetElement {} // maybe need track
