// Инициализация Telegram WebApp
Telegram.WebApp.ready();
Telegram.WebApp.expand();

// Данные водоёмов (можно получать через API бота)
const waterPoints = {
    "Шебеньгское озеро": {
        coords: [60.600, 43.450],
        depth: "4-8 м",
        fish: ["щука", "окунь", "плотва"],
        rating: 4
    },
    "Озеро Ромашевское": {
        coords: [60.489, 43.352],
        depth: "5-10 м",
        fish: ["лещ", "окунь", "язь"],
        rating: 3
    }
};

// Погодные данные (имитация - в реальности нужно получать от бота)
const weatherData = {
    "Шебеньгское озеро": {
        temp: "15°C",
        wind: "3 м/с (СЗ)",
        pressure: "1005 гПа (🟡 Нормальное)",
        humidity: "65%",
        updated: "2023-05-15 14:30"
    }
};

// Отображаем список водоёмов
function renderPointsList() {
    const pointsList = document.getElementById('points-list');
    pointsList.innerHTML = '';
    
    Object.keys(waterPoints).forEach(pointName => {
        const pointCard = document.createElement('div');
        pointCard.className = 'water-point-card';
        pointCard.innerHTML = `
            <h2>${pointName}</h2>
            <p>Глубина: ${waterPoints[pointName].depth}</p>
            <p>Рыба: ${waterPoints[pointName].fish.join(', ')}</p>
        `;
        pointCard.onclick = () => showWeatherInfo(pointName);
        pointsList.appendChild(pointCard);
    });
}

// Показываем информацию о погоде
function showWeatherInfo(pointName) {
    document.getElementById('points-list').style.display = 'none';
    const weatherInfo = document.getElementById('weather-info');
    
    document.getElementById('point-name').textContent = pointName;
    document.getElementById('point-depth').textContent = waterPoints[pointName].depth;
    document.getElementById('point-fish').textContent = waterPoints[pointName].fish.join(', ');
    document.getElementById('fish-rating').textContent = '⭐'.repeat(waterPoints[pointName].rating);
    
    // В реальном приложении эти данные должны приходить от бота
    const weather = weatherData[pointName] || {
        temp: "Нет данных",
        wind: "Нет данных",
        pressure: "Нет данных",
        humidity: "Нет данных",
        updated: "Нет данных"
    };
    
    document.getElementById('temp').textContent = weather.temp;
    document.getElementById('wind').textContent = weather.wind;
    document.getElementById('pressure').textContent = weather.pressure;
    document.getElementById('humidity').textContent = weather.humidity;
    document.getElementById('updated').textContent = weather.updated;
    
    weatherInfo.style.display = 'block';

    Telegram.WebApp.sendData(JSON.stringify({
        action: "get_weather",
        point_name: pointName
    }));
}

// Возврат к списку
function backToList() {
    document.getElementById('weather-info').style.display = 'none';
    document.getElementById('points-list').style.display = 'block';
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', renderPointsList);
