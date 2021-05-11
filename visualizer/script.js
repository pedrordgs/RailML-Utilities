function netElementFunc(id, length) {
    this.id = id;
    this.length = length;
};

function drawNodes(xmlDoc, relations){
		var arr = []
    var nodes = [];
    let netElements = xmlDoc.getElementsByTagName('netElement');
    for (i=0; i<netElements.length; i++){
        arr.push(new netElementFunc(netElements[i].getAttribute('id'), netElements[i].getAttribute('length')))
        var node_name = netElements[i].getAttribute('id');
        nodes.push(node_name + "_0");
        nodes.push(node_name + "_1");
    }
    //console.log(arr)
    var cy = cytoscape({
        container: document.getElementById('cy'), // container to render in
        elements: [],
        style: [ // the stylesheet for the graph
            {
                selector: 'node',
                style: {
                    'background-color': '#666'
                    // 'label': 'data(id)' -> para desenhar o nome dos nodos
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 3,
                    'line-color': '#ccc',
                    'target-arrow-color': '#ccc',
                    'curve-style': 'bezier',
										'label': 'data(relation)'
                }
            }
        ],

        layout: {
            name: 'grid',
            rows: 1
        }

    });
    var hasBeenDrawn = [];
    for (i=0; i<arr.length; i++){
        var pos_x = 100;
        var pos_y = 100;
        var k = i * 50;
        var elem0;
        var elem1;

        if (relations.has(arr[i].id + "_0")){
            elem0 = relations.get(arr[i].id + "_0");
        }
        else {
            elem0 = arr[i].id + "_0";
        }

        if (relations.has(arr[i].id + "_1")){
            elem1 = relations.get(arr[i].id + "_1");
        }
        else {
            elem1 =  arr[i].id + "_1";
        }

        if (!hasBeenDrawn.includes(elem0)){
            cy.add({ group: 'nodes', data: { id: elem0}, position: { x: pos_x , y: pos_y + k }});
            hasBeenDrawn.push(elem0);
        }
        if (!hasBeenDrawn.includes(elem1)){
            cy.add({ group: 'nodes', data: { id: elem1}, position: { x: pos_x + 100, y: pos_y + k }});
            hasBeenDrawn.push(elem1);
        }

        cy.add({ group: 'edges', selectable: true, data: { relation: arr[i].id,  id: i, source: elem0, target: elem1}})
    }
    cy.fit();
    return nodes;
}

function netRel(xmlDoc){
    let netRelations = xmlDoc.getElementsByTagName('netRelation');
    let lists = [];
    for (i=0; i<netRelations.length; i++){
        var pos_A = netRelations[i].getAttribute('positionOnA');
        var pos_B = netRelations[i].getAttribute('positionOnB');
        var elem_A = netRelations[i].getElementsByTagName('elementA')[0].getAttribute('ref') + "_" + pos_A;
        var elem_B = netRelations[i].getElementsByTagName('elementB')[0].getAttribute('ref') + "_" + pos_B;
        if (lists.length == 0){
            lists.push(new Set([elem_A, elem_B]))
        }
        else{
            for (j=0; j<lists.length; j++){
                if (lists[j].has(elem_A) || lists[j].has(elem_B)){
                    lists[j].add(elem_A);
                    lists[j].add(elem_B);
                    break;
                }
            }
            if (j >= lists.length)
                lists.push(new Set([elem_A, elem_B]))
        }
    }
    let relations = new Map();
    for (i=0; i<lists.length; i++){
        var arr = Array.from(lists[i]);
        for (j=0; j<arr.length; j++){
            relations.set(arr[j], arr[0]);
        }
    }
    return relations;
}

if (window.File && window.FileReader && window.FileList && window.Blob) {
    function loadFile() {
        var file = document.querySelector('input[type=file]').files[0];
        var reader = new FileReader()

        var textFile = /text.xml/;

        if (file.type.match(textFile)) {
            reader.onload = function (event) {
                let parser = new DOMParser();
                let xmlDoc = parser.parseFromString(event.target.result, 'text/xml');
                let relations = netRel(xmlDoc);
                let nodes = drawNodes(xmlDoc, relations);
            }
        } else {
            alert("It doesn't seem to be a xml file!");
        }
        reader.readAsText(file);

    }

} else {
    alert("Your browser is too old to support HTML5 File API");
}
