(function() {
  const canvas = document.getElementById('fire-speckles');
  if (!canvas) return;
  const hero = canvas.parentElement;
  const ctx = canvas.getContext('2d');
  let W, H;
  const particles = [];
  const COUNT = 70;

  const colors = [
    { r: 255, g: 80, b: 20 },
    { r: 255, g: 140, b: 30 },
    { r: 255, g: 200, b: 50 },
    { r: 220, g: 60, b: 30 },
    { r: 180, g: 40, b: 20 },
  ];

  function resize() {
    const rect = hero.getBoundingClientRect();
    W = canvas.width = rect.width;
    H = canvas.height = rect.height;
  }

  function createParticle() {
    return {
      x: Math.random() * W,
      y: H + Math.random() * 40,
      vx: (Math.random() - 0.5) * 0.4,
      vy: -(0.3 + Math.random() * 0.6),
      size: 1.5 + Math.random() * 3.5,
      life: 0.6 + Math.random() * 0.4,
      maxLife: 0.6 + Math.random() * 0.4,
      color: colors[Math.floor(Math.random() * colors.length)],
      drift: (Math.random() - 0.5) * 0.3,
    };
  }

  for (let i = 0; i < COUNT; i++) {
    const p = createParticle();
    p.y = Math.random() * H;
    p.life = Math.random() * p.maxLife;
    particles.push(p);
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);

    for (const p of particles) {
      p.x += p.vx + Math.sin(p.life * 20) * p.drift;
      p.y += p.vy;
      p.life -= 0.003;
      p.vy *= 0.998;

      if (p.life <= 0 || p.y < -20) {
        Object.assign(p, createParticle());
        p.y = H + Math.random() * 20;
      }

      const alpha = Math.min(p.life / p.maxLife * 0.8, 0.8);
      const c = p.color;
      const radius = p.size * (0.5 + 0.5 * (p.life / p.maxLife));

      const grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, radius * 3);
      grad.addColorStop(0, `rgba(${c.r},${c.g},${c.b},${alpha})`);
      grad.addColorStop(0.3, `rgba(${c.r},${c.g},${c.b},${alpha * 0.4})`);
      grad.addColorStop(1, `rgba(${c.r},${c.g},${c.b},0)`);

      ctx.beginPath();
      ctx.fillStyle = grad;
      ctx.arc(p.x, p.y, radius * 3, 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', resize, { passive: true });
  new ResizeObserver(resize).observe(hero);
  resize();
  draw();
})();
