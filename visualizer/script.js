function netElementFunc(id, length) {
    this.id = id;
    this.length = length;
};

var arr = []

if (window.File && window.FileReader && window.FileList && window.Blob) {
    function showFile() {
        // var preview = document.getElementById('show-text');
        var file = document.querySelector('input[type=file]').files[0];
        var reader = new FileReader()

        var textFile = /text.xml/;

        if (file.type.match(textFile)) {
            reader.onload = function (event) {
                let parser = new DOMParser();
                let xmlDoc = parser.parseFromString(event.target.result, 'text/xml');
                let netElements = xmlDoc.getElementsByTagName('netElement');
                for (i=0; i<netElements.length; i++){
                    arr.push(new netElementFunc(netElements[i].getAttribute('id'), netElements[i].getAttribute('length')))
                }
                console.log(arr)
                var cy = cytoscape({

                    container: document.getElementById('cy'), // container to render in

                    elements: [],

                    style: [ // the stylesheet for the graph
                        {
                            selector: 'node',
                            style: {
                                'background-color': '#666',
                                'label': 'data(id)'
                            }
                        },

                        {
                            selector: 'edge',
                            style: {
                                'width': 3,
                                'line-color': '#ccc',
                                'target-arrow-color': '#ccc',
                                'target-arrow-shape': 'triangle',
                                'curve-style': 'bezier'
                            }
                        }
                    ],

                    layout: {
                        name: 'grid',
                        rows: 1
                    }

                });

                for (i=0; i<arr.length; i++){
                    var pos_x = 100;
                    var pos_y = 100;
                    var k = i * 50;
                    cy.add({ group: 'nodes', data: { id: arr[i].id + "_0"}, position: { x: pos_x , y: pos_y + k }});
                    cy.add({ group: 'nodes', data: { id: arr[i].id + "_1"}, position: { x: pos_x + 100, y: pos_y + k }});
                    cy.add({ group: 'edges', data: { id: i, source: arr[i].id + "_0", target: arr[i].id + "_1"}})
                }

            }
        } else {
            alert("It doesn't seem to be a xml file!");
        }
        reader.readAsText(file);

        // var eles = cy.add([
        //     { group: 'nodes', data: { id: 'n0' }, position: { x: 100, y: 100 } },
        //     { group: 'nodes', data: { id: 'n1' }, position: { x: 200, y: 200 } },
        //     { group: 'edges', data: { id: 'e0', source: 'n0', target: 'n1' } },
        //     { group: 'edges', data: { id: 'e1', source: 'n1', target: 'n1' } }
        // ]);
    }

} else {
    alert("Your browser is too old to support HTML5 File API");
}

