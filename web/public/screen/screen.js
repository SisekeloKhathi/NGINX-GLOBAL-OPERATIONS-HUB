(function () {
  'use strict';

  var REFRESH_MS = 30000;
  var API_BASE = '/api/display';

  var params = new URLSearchParams(window.location.search);
  var source = (params.get('source') || 'fx').toLowerCase();
  document.body.dataset.source = source;

  var boardEl = document.getElementById('board');
  var clockEl = document.getElementById('clock');
  var dotEl = document.getElementById('dot');
  var statusEl = document.getElementById('status-text');
  var updatedEl = document.getElementById('updated');

  var lastValues = {};

  function pad(n) { return n < 10 ? '0' + n : '' + n; }

  function tickClock() {
    var d = new Date();
    clockEl.textContent = pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
  }
  tickClock();
  setInterval(tickClock, 1000);

  function setStatus(state, text) {
    dotEl.className = 'dot ' + state;
    statusEl.textContent = text;
  }

  function fmt(n, decimals) {
    if (n === null || n === undefined || isNaN(n)) return '—';
    return Number(n).toFixed(decimals === undefined ? 0 : decimals);
  }

  function fmtThousands(n) {
    if (n === null || n === undefined || isNaN(n)) return '—';
    return Number(n).toLocaleString('en-ZA');
  }

  function makeTile(label, value, unit) {
    var div = document.createElement('div');
    div.className = 'tile';
    var l = document.createElement('div');
    l.className = 'label';
    l.textContent = label;
    var v = document.createElement('div');
    v.className = 'value';
    v.textContent = value;
    if (unit) {
      var u = document.createElement('span');
      u.className = 'unit';
      u.textContent = unit;
      v.appendChild(u);
    }
    div.appendChild(l);
    div.appendChild(v);
    return div;
  }

  function render(source, data) {
    boardEl.innerHTML = '';
    boardEl.className = 'board ' + source;

    if (source === 'fx' && data.rates) {
      var pairs = { ZAR: 'USD → ZAR', EUR: 'USD → EUR', GBP: 'USD → GBP', JPY: 'USD → JPY', CHF: 'USD → CHF' };
      Object.keys(pairs).forEach(function (cur) {
        if (data.rates[cur] !== undefined) {
          boardEl.appendChild(makeTile(pairs[cur], fmt(data.rates[cur], 4)));
        }
      });
    } else if (source === 'weather' && data.data) {
      var w = data.data;
      boardEl.appendChild(makeTile('Temperature', fmt(w.temperature, 1), '°C'));
      boardEl.appendChild(makeTile('Wind Speed',  fmt(w.windspeed, 1),  'km/h'));
      boardEl.appendChild(makeTile('Wind Dir',    fmt(w.winddirection, 0), '°'));
      boardEl.appendChild(makeTile('Weather Code', fmt(w.weathercode, 0)));
    } else if (source === 'flights' && data.data) {
      boardEl.appendChild(makeTile('Aircraft in airspace', fmtThousands(data.data.aircraft_count)));
    } else if (source === 'economics' && data.data) {
      var g = data.data;
      var billions = g.value ? (g.value / 1e9).toFixed(2) : null;
      boardEl.appendChild(makeTile('GDP (billions)', fmt(billions, 2), 'R bn'));
      boardEl.appendChild(makeTile('Reporting Year', g.reporting_year || '—'));
    } else {
      boardEl.appendChild(makeTile('No data', '—'));
    }
  }

  function fetchAndRender() {
    var url = API_BASE + '/' + source;
    fetch(url, { cache: 'no-store' })
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function (data) {
        render(source, data);
        setStatus('live', 'live');
        if (data.updated) {
          var age = Math.floor((Date.now() - new Date(data.updated).getTime()) / 1000);
          updatedEl.textContent = 'data ' + age + 's old · polled ' + new Date().toLocaleTimeString();
          if (age > 300) setStatus('stale', 'stale (' + age + 's)');
        } else {
          updatedEl.textContent = 'polled ' + new Date().toLocaleTimeString();
        }
      })
      .catch(function (err) {
        setStatus('dead', 'error: ' + err.message);
        updatedEl.textContent = 'last attempt ' + new Date().toLocaleTimeString();
      });
  }

  fetchAndRender();
  setInterval(fetchAndRender, REFRESH_MS);

  // Fullscreen on click (some kiosk browsers need this)
  document.addEventListener('dblclick', function () {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen && document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen && document.exitFullscreen();
    }
  });
})();
