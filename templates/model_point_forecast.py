<!DOCTYPE html>
<html>
<head>
  <title>City Temperature Map</title>
  <meta charset="utf-8" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    #map { height: 100vh; }
  </style>
</head>
<body>
  <div id="map"></div>

  <script>
    const map = L.map('map').setView([0, 0], 2);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
    }).addTo(map);

    function getTempColor(temp) {
      if (temp <= 32) return 'blue';
      if (temp <= 50) return 'cyan';
      if (temp <= 70) return 'green';
      if (temp <= 85) return 'orange';
      return 'red';
    }

    console.log("Fetching gfs_dump.json...");

    fetch('https://tropicainnovations.pythonanywhere.com/static/gfs_dump/gfs_dump.json')
      .then(res => res.json())
      .then(data => {
        for (const city in data) {
          const values = data[city];
          const lat = values[0];
          const lon = values[1];
          const temps = values[6];  // temps is a dictionary {0: temp0, 1: temp1, ...}

          if (lat !== null && lon !== null && temps !== undefined) {
            const tempAtHour0 = temps["0"] !== undefined ? temps["0"] : temps[0]; // fix here
            const color = getTempColor(tempAtHour0);

            const marker = L.circleMarker([lat, lon], {
              radius: 8,
              fillColor: color,
              color: '#333',
              weight: 1,
              fillOpacity: 0.85
            }).addTo(map);

            marker.bindPopup(
              `<b>${city}</b><br>` +
              `Temp: ${tempAtHour0} °F<br>` +
              `Lat: ${lat}, Lon: ${lon}`
            );
          }
        }
      });
  </script>
</body>
</html>