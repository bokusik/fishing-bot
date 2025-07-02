Telegram.WebApp.ready();
Telegram.WebApp.expand();

const points = {
    "Шебеньгское озеро": {
        coords: [60.600, 43.450],
        depth: "4-8 м",
        fish: ["щука", "окунь", "плотва"]
    },
    // ... другие водоёмы
};

function renderPoints() {
    const container = document.getElementById('points-list');
    
    Object.entries(points).forEach(([name, data]) => {
        const point = document.createElement('div');
        point.className = 'point-card';
        point.innerHTML = `
            <h3>${name}</h3>
            <p>Глубина: ${data.depth}</p>
            <p>Рыба: ${data.fish.join(', ')}</p>
            <button onclick="selectPoint('${name}')">Подробнее</button>
        `;
        container.appendChild(point);
    });
}

function selectPoint(name) {
    Telegram.WebApp.sendData(JSON.stringify({
        action: "select_point",
        point: name
    }));
}

document.addEventListener('DOMContentLoaded', renderPoints);