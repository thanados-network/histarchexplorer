const hierachy = {
    id: 'ms',
    data: {
        imageURL: 'https://i.pravatar.cc/300?img=68',
        name: 'PLACE',
    },
    options: {
        nodeBGColor: '#cdb4db',
        nodeBGColorHover: '#cdb4db',
    },
    children: [
        {
            id: 'mh',
            data: {
                imageURL: 'https://i.pravatar.cc/300?img=69',
                name: 'FEATURE',
            },
            options: {
                nodeBGColor: '#ffafcc',
                nodeBGColorHover: '#ffafcc',
            },
            children: [
                {
                    id: 'kb',
                    data: {
                        imageURL: 'https://i.pravatar.cc/300?img=65',
                        name: 'ARTIFACT 1',
                    },
                    options: {
                        nodeBGColor: '#f8ad9d',
                        nodeBGColorHover: '#f8ad9d',
                    },
                },
                {
                    id: 'cr',
                    data: {
                        imageURL: 'https://i.pravatar.cc/300?img=60',
                        name: 'ARTIFACT 2',
                    },
                    options: {
                        nodeBGColor: '#c9cba3',
                        nodeBGColorHover: '#c9cba3',
                    },
                },
            ],
        },
    ],
};

const options = {
    contentKey: 'data',
    nodeWidth: 100,
    nodeHeight: 70,
    fontColor: '#fff',
    borderColor: '#333',
    childrenSpacing: 50,
    siblingSpacing: 20,
    direction: 'top',
    enableExpandCollapse: true,
    nodeTemplate: (content) => {
        // Calculate dynamic font size based on node width (scale between 10px and 16px)
        const fontSize = Math.max(10, Math.min(16, options.nodeWidth * 0.1));

        return `
        <div style='display: flex; flex-direction: column; gap: 10px; justify-content: center; align-items: center; height: 100%;'>
            <img style='width: 30px; height: 30px; border-radius: 50%;' src='${content.imageURL}' alt='' />
            <div style="font-weight: bold; font-family: Arial; font-size: ${fontSize}px">${content.name}</div>
        </div>`;
    },
    canvasStyle: 'background: #f6f6f6;',
    enableToolbar: true,
};

const tree = new ApexTree(document.getElementById('svg-tree'), options);
tree.render(hierachy);
