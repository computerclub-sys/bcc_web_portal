import * as THREE from 'three';

(function init() {
  const canvas = document.getElementById('hero-bg-canvas');
  if (!canvas) return;
  const hero = canvas.parentElement;

  function hexToVec3(hex) {
    const n = parseInt(hex.slice(1), 16);
    return new THREE.Vector3(
      ((n >> 16) & 255) / 255,
      ((n >> 8) & 255) / 255,
      (n & 255) / 255
    );
  }

  const CONFIG = {
    coreColor: '#6a0a2a',
    midColor: '#ff2d6b',
    rimColor: '#ffd36b',
    pointSize: 80,
    brightness: 1.6,
    opacity: 2,
    spin: 0.03,
  };

  const dpr = Math.min(devicePixelRatio, 2);
  const initRect = hero.getBoundingClientRect();

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  } catch (e) {
    console.warn('Three.js init failed:', e);
    return;
  }
  renderer.setPixelRatio(dpr);
  renderer.setSize(initRect.width || window.innerWidth, initRect.height || window.innerHeight, false);
  renderer.setClearColor(0x000000, 1);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, (initRect.width || window.innerWidth) / (initRect.height || window.innerHeight), 0.1, 20);
  camera.position.set(0, 0, 7);

  const count = 30000;
  const radius = 2.5;
  const positions = new Float32Array(count * 3);
  const mixv = new Float32Array(count);

  for (let i = 0; i < count; i++) {
    const i3 = i * 3;
    let u, v, s;
    do { u = Math.random() * 2 - 1; v = Math.random() * 2 - 1; s = u * u + v * v; } while (s >= 1 || s === 0);
    const factor = 2 * Math.sqrt(1 - s);
    const rN = Math.pow(Math.random(), 0.4);
    const r = radius * (0.55 + rN * 0.45);
    positions[i3] = (u * factor) * r;
    positions[i3 + 1] = (v * factor) * r;
    positions[i3 + 2] = (1 - 2 * s) * r;
    mixv[i] = rN;
  }

  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geom.setAttribute('aMix', new THREE.Float32BufferAttribute(mixv, 1));

  const uniforms = {
    uTime: { value: 0 },
    uOpacity: { value: 0 },
    uCore: { value: hexToVec3(CONFIG.coreColor) },
    uMid: { value: hexToVec3(CONFIG.midColor) },
    uRim: { value: hexToVec3(CONFIG.rimColor) },
    uBrightness: { value: CONFIG.brightness },
  };

  const mat = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: `
      uniform float uTime;
      attribute float aMix;
      uniform vec3 uCore;
      uniform vec3 uMid;
      uniform vec3 uRim;
      varying vec3 vColor;
      void main() {
        vec3 pos = position;
        float t = uTime * 1.2;
        float wobble = sin(t + aMix * 6.28) * 0.08;
        pos *= 1.0 + wobble;
        float swirl = uTime * 0.04 + aMix * 6.28;
        mat2 rot = mat2(cos(swirl), -sin(swirl), sin(swirl), cos(swirl));
        pos.xz = rot * pos.xz;
        vec4 mv = viewMatrix * modelMatrix * vec4(pos, 1.0);
        gl_PointSize = 40.0 * (1.0 / -mv.z);
        gl_Position = projectionMatrix * mv;
        float t1 = smoothstep(0.25, 0.85, aMix);
        vec3 m1 = mix(uCore, uMid, t1);
        float t2 = clamp((aMix - 0.7) * 3.0, 0.0, 1.0);
        vColor = mix(m1, uRim, t2);
      }
    `,
    fragmentShader: `
      uniform float uOpacity;
      uniform float uBrightness;
      varying vec3 vColor;
      void main() {
        vec2 uv = gl_PointCoord - 0.5;
        float d = length(uv);
        if (d > 0.5) discard;
        float s = pow(1.0 - d * 2.0, 4.0);
        gl_FragColor = vec4(vColor * uBrightness * s, s * uOpacity);
      }
    `,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  });

  const points = new THREE.Points(geom, mat);
  const group = new THREE.Group();
  group.add(points);
  scene.add(group);

  const appearStart = performance.now();

  function render() {
    requestAnimationFrame(render);
    const now = performance.now() / 1000;
    const dt = Math.min(0.05, now - (render._lastTime || now));
    render._lastTime = now;

    uniforms.uTime.value = now;
    const elapsed = performance.now() - appearStart;
    uniforms.uOpacity.value = Math.max(0, Math.min(1, (elapsed - 300) / 1400)) * CONFIG.opacity;

    group.rotation.y += dt * CONFIG.spin;
    group.rotation.x += dt * CONFIG.spin * 0.33;

    renderer.render(scene, camera);
  }
  render._lastTime = null;

  function resize() {
    const rect = hero.getBoundingClientRect();
    const w = rect.width;
    const h = rect.height;
    if (w < 1 || h < 1) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }

  window.addEventListener('resize', resize, { passive: true });
  new ResizeObserver(resize).observe(hero);
  resize();
  render();
})();
