console.log("vocabulary.js loaded");
console.log(window.typeTree);

const typeTree = window.typeTree;

const treeviewContainer1 = document.getElementById('standardTree');
const tree1 = new Treeview({
    containerId: 'standardTree',   // ID of the HTML element to render the tree into
    data: typeTree.standard,             // Your hierarchical data
    searchEnabled: true,          // Enable the search bar (default: true)
    initiallyExpanded: false,     // Start with nodes collapsed (default: false)
    multiSelectEnabled: false,     // Enable multi-selection by clicking nodes
    nodeSelectionEnabled: true,
    onSelectionChange: async (selectedNodesData) => {

        if (!selectedNodesData.length) return;

        const node = selectedNodesData[selectedNodesData.length - 1];

        const panel = document.getElementById('detailsPanel');

        panel.innerHTML = `
        <p>Loading...</p>
    `;

        const response = await fetch(`/api/vocabulary/${node.id}`);
        const data = await response.json();

        panel.innerHTML = `
        <h2>${data.name}</h2>

        <hr>

        <p>
            <strong>ID:</strong><br>
            ${data.id}
        </p>

        <p>
            <strong>Description:</strong><br>
            ${data.description || 'No description available.'}
        </p>

        <p>
            <a href="/vocabulary/${data.id}">
                Open full detail page →
            </a>
        </p>
    `;
    }
});

const treeviewContainer2 = document.getElementById('customTree');
const tree2 = new Treeview({
    containerId: 'customTree',   // ID of the HTML element to render the tree into
    data: typeTree.custom,             // Your hierarchical data
    searchEnabled: true,          // Enable the search bar (default: true)
    initiallyExpanded: false,     // Start with nodes collapsed (default: false)
    multiSelectEnabled: true,     // Enable multi-selection by clicking nodes
    nodeSelectionEnabled: true,
    onSelectionChange: (selectedNodesData) => { // Callback when selection changes
        console.log('Selected Nodes (Tree 1):', selectedNodesData);
        // Example: Update a display area with selected nodes
        // document.getElementById('output-area').textContent = JSON.stringify(selectedNodesData, null, 2);
    }
});

const treeviewContainer3 = document.getElementById('valueTree');
const tree3 = new Treeview({
    containerId: 'valueTree',   // ID of the HTML element to render the tree into
    data: typeTree.value,             // Your hierarchical data
    searchEnabled: true,          // Enable the search bar (default: true)
    initiallyExpanded: false,     // Start with nodes collapsed (default: false)
    multiSelectEnabled: true,     // Enable multi-selection by clicking nodes
    nodeSelectionEnabled: false,
    onSelectionChange: (selectedNodesData) => { // Callback when selection changes
        console.log('Selected Nodes (Tree 1):', selectedNodesData);
        // Example: Update a display area with selected nodes
        // document.getElementById('output-area').textContent = JSON.stringify(selectedNodesData, null, 2);
    }
});

document.querySelectorAll('.tab-links a').forEach(link => {
    link.addEventListener('click', function (e) {
        e.preventDefault();
        const target = this.getAttribute('href').substring(1);

        document.querySelectorAll('.tab-links li').forEach(li => li.classList.remove('active'));
        this.parentElement.classList.add('active');

        document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
        document.getElementById(target).classList.add('active');
    });
});