(function() {
  var config = window.INVITE_CONFIG;
  var form = document.getElementById('invForm');
  var preview = document.getElementById('invPreview');
  var canvas = document.getElementById('invCanvas');
  var ctx = canvas.getContext('2d');
  var dlBtn = document.getElementById('invDownload');
  var regenBtn = document.getElementById('invRegen');
  var logoImg = new Image();

  function loadLogo() {
    return new Promise(function(resolve) {
      logoImg.onload = resolve;
      logoImg.onerror = resolve;
      logoImg.src = config.logoUrl;
    });
  }

  function drawCard(name) {
    var W = 1600, H = 900;
    ctx.clearRect(0, 0, W, H);

    var grad = ctx.createRadialGradient(W/2, H/2, 0, W/2, H/2, W*0.7);
    grad.addColorStop(0, '#1a0a2e');
    grad.addColorStop(0.5, '#0f0518');
    grad.addColorStop(1, '#020617');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = 'rgba(71,85,105,0.12)';
    ctx.lineWidth = 1;
    for (var x = 0; x < W; x += 40) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (var y = 0; y < H; y += 40) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

    var glow = ctx.createRadialGradient(W*0.3, H*0.4, 0, W*0.3, H*0.4, 400);
    glow.addColorStop(0, 'rgba(217,70,239,0.12)');
    glow.addColorStop(1, 'transparent');
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = 'rgba(217,70,239,0.25)';
    ctx.lineWidth = 3;
    ctx.strokeRect(30, 30, W-60, H-60);

    [[30,30],[W-30,30],[30,H-30],[W-30,H-30]].forEach(function(c) {
      ctx.fillStyle = '#d946ef';
      ctx.beginPath();
      ctx.arc(c[0], c[1], 4, 0, Math.PI*2);
      ctx.fill();
    });

    ctx.drawImage(logoImg, 60, 50, 80, 80);

    ctx.fillStyle = '#eeeef8';
    ctx.font = 'bold 36px "Press Start 2P", monospace';
    ctx.textAlign = 'left';
    ctx.fillText(config.festTitle, 160, 80);

    ctx.fillStyle = '#d946ef';
    ctx.font = 'bold 28px "Press Start 2P", monospace';
    ctx.fillText(config.festYear, 160, 118);

    ctx.font = 'bold 20px "Press Start 2P", monospace';
    ctx.textAlign = 'center';
    var bpw = ctx.measureText('VISITOR PASS').width + 40;
    ctx.fillStyle = 'rgba(217,70,239,0.15)';
    roundRect(ctx, W/2 - bpw/2, 200, bpw, 50, 25);
    ctx.fill();
    ctx.strokeStyle = 'rgba(217,70,239,0.4)';
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.fillStyle = '#d946ef';
    ctx.fillText('VISITOR PASS', W/2, 232);

    ctx.fillStyle = '#efe9f2';
    ctx.font = 'bold 52px "Press Start 2P", monospace';
    var displayName = name.length > 20 ? name.substring(0, 20) : name;
    ctx.fillText(displayName, W/2, 370);

    ctx.strokeStyle = 'rgba(217,70,239,0.3)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(W/2 - 200, 410);
    ctx.lineTo(W/2 + 200, 410);
    ctx.stroke();

    if (config.festDate) {
      ctx.fillStyle = '#c8c8e0';
      ctx.font = '28px "VT323", monospace';
      ctx.fillText(config.festDate + '  •  BAIUST Campus', W/2, 470);
    }

    ctx.fillStyle = '#6a6a88';
    ctx.font = '22px "VT323", monospace';
    ctx.fillText('Non-transferable  •  Organized by BAIUST Computer Club', W/2, H - 80);

    ctx.strokeStyle = '#d946ef';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(W/2 - 150, H - 60);
    ctx.lineTo(W/2 + 150, H - 60);
    ctx.stroke();
  }

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    var name = document.getElementById('invName').value.trim();
    if (!name) return;
    document.fonts.ready.then(function() {
      return loadLogo();
    }).then(function() {
      drawCard(name);
      form.style.display = 'none';
      preview.style.display = '';
    });
  });

  dlBtn.addEventListener('click', function() {
    canvas.toBlob(function(blob) {
      if (!blob) return;
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'CSE-Fest-' + config.festYear + '-Invitation-' + document.getElementById('invName').value.trim().replace(/\s+/g, '-') + '.png';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 'image/png');
  });

  regenBtn.addEventListener('click', function() {
    preview.style.display = 'none';
    form.style.display = '';
    document.getElementById('invName').value = '';
    document.getElementById('invName').focus();
  });
})();
