const startTime = document.body.dataset.startTime;
let nodes = [];

setInterval(() =>{
    fetch('http://localhost:5000/peers')
    .then(response => response.json())
    .then(data => {
        const nodeContainer = document.getElementById('nodes-here') ;
        
        while (nodeContainer.firstChild) {
            nodeContainer.removeChild(nodeContainer.firstChild);
        }

        for (const node of data.peers) {
            const div = document.createElement('div');
            div.classList.add("node-indv")
            const circle = document.createElement('p');
            circle.textContent = '🟢';
            const nodeP = document.createElement('p');
            nodeP.textContent = node.replace('http://', '').replace(':5000', '');
            div.appendChild(circle);
            div.appendChild(nodeP);
            nodeContainer.appendChild(div);

            if (!nodes.includes(node)) {
                nodes.push(node);                     
            }
        }

        document.getElementById("total-count").innerText = nodes.length;
        document.getElementById("active-count").innerText = data.peers.length;
        document.getElementById("uptime").innerText = `${Math.floor((new Date().getTime() - new Date(startTime)) / (1000 * 60))} MINS`;
    });
}, 2500);


setInterval(() =>{
    fetch('http://localhost:5000/logs')
    .then(response => response.json())
    .then(data => {
        const logsText = document.getElementById('logs-text') ;
        logsText.value = '';

        for (const l of data.logs) {
            logsText.value += `[${l[1]}] ${l[0]}\n`
        }
    })
}, 2500);

