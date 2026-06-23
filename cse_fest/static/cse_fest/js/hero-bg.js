import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { GammaCorrectionShader } from 'three/addons/shaders/GammaCorrectionShader.js';
import { CopyShader } from 'three/addons/shaders/CopyShader.js';

(function init() {
  const canvas = document.getElementById('hero-bg-canvas');
  if (!canvas) return;
  const hero = canvas.parentElement;

  function hexToVec3(hex) {
    const n = parseInt(hex.slice(1), 16);
    return new THREE.Vector3(((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255);
  }

  const CONFIG = {
    bgColor: '#0a0a24',
    flameColor: '#aee9ff',
    flameColor2: '#c79bff',
    flameAmt: 0.2,
    colorA: '#aef6cf',
    colorB: '#5fe6a0',
    colorC: '#eafff2',
    opacity: 2,
    pointSize: 50,
    brightness: 1.85,
    drift: 2.35,
    twinkle: 1,
    spin: 0.03,
    repelRadius: 5,
    repelStrength: 0.35,
    parallax: 0.6,
  };

  const LAYERS = { NONE: 0, TORUS_SCENE: 1, BLOOM_SCENE: 2, ENTIRE_SCENE: 3 };
  const dpr = Math.min(devicePixelRatio, 2);
  const initRect = hero.getBoundingClientRect();

  let renderer;
  try {
    renderer = new THREE.WebGL1Renderer({ canvas, antialias: true });
  } catch (e) { console.warn('Three.js init failed:', e); return; }

  renderer.setPixelRatio(dpr);
  renderer.setSize(initRect.width || window.innerWidth, initRect.height || window.innerHeight, false);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.VSMShadowMap;
  renderer.outputEncoding = THREE.sRGBEncoding;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000000);
  scene.fog = new THREE.Fog(0x000000, 0, 15);

  const camera = new THREE.PerspectiveCamera(45, (initRect.width || window.innerWidth) / (initRect.height || window.innerHeight), 0.1, 80);
  camera.position.set(0, 0, 5);
  camera.layers.enable(LAYERS.TORUS_SCENE);
  camera.layers.enable(LAYERS.BLOOM_SCENE);
  camera.layers.enable(LAYERS.ENTIRE_SCENE);
  scene.add(camera);

  const renderScene = new RenderPass(scene, camera);

  const torusComposer = new EffectComposer(renderer);
  torusComposer.addPass(renderScene);
  torusComposer.addPass(new ShaderPass(GammaCorrectionShader));
  torusComposer.addPass(new UnrealBloomPass(new THREE.Vector2(initRect.width || 1920, initRect.height || 1080), 0.22, 0.2, 0));
  torusComposer.addPass(new ShaderPass(CopyShader));
  torusComposer.renderToScreen = false;

  const bloomComposer = new EffectComposer(renderer);
  bloomComposer.addPass(renderScene);
  bloomComposer.addPass(new UnrealBloomPass(new THREE.Vector2(initRect.width || 1920, initRect.height || 1080), 0.4, 0.55, 0));
  bloomComposer.addPass(new ShaderPass(GammaCorrectionShader));
  bloomComposer.renderToScreen = false;

  // Halo fallback texture
  const haloCanvas = document.createElement('canvas');
  haloCanvas.width = haloCanvas.height = 1;
  const haloCtx = haloCanvas.getContext('2d');
  haloCtx.fillStyle = '#000';
  haloCtx.fillRect(0, 0, 1, 1);
  const haloTexture = new THREE.CanvasTexture(haloCanvas);
  haloTexture.minFilter = haloTexture.magFilter = THREE.NearestFilter;

  const finalPassShader = {
    uniforms: {
      iTime: { value: 0 },
      tDiffuse: { value: null },
      torusTexture: { value: null },
      bloomTexture: { value: null },
      haloTexture: { value: haloTexture },
      uBg: { value: hexToVec3(CONFIG.bgColor) },
      uFlameA: { value: hexToVec3(CONFIG.flameColor) },
      uFlameB: { value: hexToVec3(CONFIG.flameColor2) },
      uFlameAmt: { value: CONFIG.flameAmt },
    },
    vertexShader: `varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position, 1.0); }`,
    fragmentShader: `
uniform float iTime;
uniform sampler2D tDiffuse;
uniform sampler2D bloomTexture;
uniform sampler2D torusTexture;
uniform sampler2D haloTexture;
uniform vec3 uBg;
uniform vec3 uFlameA;
uniform vec3 uFlameB;
uniform float uFlameAmt;
varying vec2 vUv;

vec3 warp3d(vec3 pos, float t) {
  float curv=.8, a=1.9, b=0.7;
  pos*=2.; pos.x+=curv*sin(t+a*pos.y)+t*b;
  pos.y+=curv*cos(t+a*pos.x); pos.y+=curv*sin(t+a*pos.z)+t*b;
  pos.z+=curv*cos(t+a*pos.y); pos.z+=curv*sin(t+a*pos.x)+t*b;
  pos.x+=curv*cos(t+a*pos.z);
  return 0.5+0.5*cos(pos.xyz+vec3(1,2,4));
}

void main() {
  vec2 uv=2.*vUv-1.;
  vec3 w=pow(warp3d(vec3(uv.x,sin(uv.y),uv.y),iTime*1.5),vec3(1.5));
  vec3 flame=1.5*uFlameA*w.x; flame*=w.y; flame+=uFlameB*w.z;
  flame*=smoothstep(0.25,1.,abs(uv.y));
  float md=smoothstep(-0.7,1.,-uv.y*uv.x); flame*=md*md;
  vec3 bg=uBg*(1.-0.4*length(uv));
  vec3 color=bg+flame*uFlameAmt;
  color+=texture2D(bloomTexture,vUv).xyz;
  color+=texture2D(torusTexture,vUv).xyz;
  color+=texture2D(tDiffuse,vUv).xyz;
  gl_FragColor=vec4(color,1.);
}
`,
  };

  const finalComposer = new EffectComposer(renderer);
  finalComposer.addPass(renderScene);
  const finalPass = new ShaderPass(finalPassShader);
  finalPass.uniforms.bloomTexture.value = bloomComposer.renderTarget1.texture;
  finalPass.uniforms.torusTexture.value = torusComposer.renderTarget1.texture;
  finalComposer.addPass(finalPass);
  finalComposer.renderToScreen = true;

  // Starfield
  const count = 4200;
  const depth = 30;
  const positions = new Float32Array(count * 3);
  const paletteArr = new Float32Array(count);
  const brightArr = new Float32Array(count);
  const scalesArr = new Float32Array(count);
  const phasesArr = new Float32Array(count);

  for (let i = 0; i < count; i++) {
    const i3 = i * 3;
    positions[i3] = (Math.random() - 0.5) * 24;
    positions[i3 + 1] = (Math.random() - 0.5) * 16;
    positions[i3 + 2] = (Math.random() - 0.5) * 30;
    paletteArr[i] = Math.floor(Math.random() * 3);
    brightArr[i] = 0.7 + Math.random() * 0.6;
    scalesArr[i] = 0.5 + Math.pow(Math.random(), 1.4) * 2.5;
    phasesArr[i] = Math.random();
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('aScale', new THREE.Float32BufferAttribute(scalesArr, 1));
  geometry.setAttribute('aPhase', new THREE.Float32BufferAttribute(phasesArr, 1));
  geometry.setAttribute('aPalette', new THREE.Float32BufferAttribute(paletteArr, 1));
  geometry.setAttribute('aBright', new THREE.Float32BufferAttribute(brightArr, 1));

  const uniforms = {
    uTime: { value: 0 },
    uSize: { value: CONFIG.pointSize },
    uOpacity: { value: 0 },
    uDrift: { value: 0 },
    uDepth: { value: depth },
    uTwinkle: { value: CONFIG.twinkle },
    uCursor: { value: new THREE.Vector3() },
    uRepelRadius: { value: CONFIG.repelRadius },
    uRepelStrength: { value: CONFIG.repelStrength },
    uActivity: { value: 0 },
    uColorA: { value: hexToVec3(CONFIG.colorA) },
    uColorB: { value: hexToVec3(CONFIG.colorB) },
    uColorC: { value: hexToVec3(CONFIG.colorC) },
    uBrightness: { value: CONFIG.brightness },
  };

  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: `
uniform float uTime;
uniform float uSize;
uniform float uDrift;
uniform float uDepth;
uniform float uTwinkle;
uniform vec3 uCursor;
uniform float uRepelRadius;
uniform float uRepelStrength;
uniform float uActivity;
uniform vec3 uColorA;
uniform vec3 uColorB;
uniform vec3 uColorC;
attribute float aScale;
attribute float aPhase;
attribute float aPalette;
attribute float aBright;
varying vec3 vColor;
varying float vTwinkle;

void main() {
  vec3 pos = position;
  pos.z = mod(pos.z + uDrift + (uDepth * 0.5), uDepth) - (uDepth * 0.5);
  float tw = sin(uTime * 1.6 + aPhase * 6.2831);
  vTwinkle = (1.0 - uTwinkle) + uTwinkle * (0.55 + 0.45 * tw);
  vec4 modelPosition = modelMatrix * vec4(pos, 1.0);
  vec3 toParticle = modelPosition.xyz - uCursor;
  float dist = length(toParticle);
  float falloff = smoothstep(uRepelRadius, 0.0, dist);
  modelPosition.xyz += normalize(toParticle + vec3(0.0001)) * falloff * uRepelStrength * uActivity;
  vec4 viewPosition = viewMatrix * modelPosition;
  gl_Position = projectionMatrix * viewPosition;
  gl_PointSize = uSize * aScale;
  gl_PointSize *= (1.0 / -viewPosition.z);
  vec3 base = aPalette < 0.5 ? uColorA : (aPalette < 1.5 ? uColorB : uColorC);
  vColor = base * aBright;
}
`,
    fragmentShader: `
uniform float uOpacity;
uniform float uBrightness;
varying vec3 vColor;
varying float vTwinkle;

void main() {
  vec2 uv = gl_PointCoord - 0.5;
  float d = length(uv);
  if (d > 0.5) discard;
  float strength = pow(1.0 - d * 2.0, 4.0);
  vec3 color = mix(vec3(0.0), vColor, strength);
  gl_FragColor = vec4(color * uBrightness, strength * uOpacity * vTwinkle);
}
`,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  });

  const points = new THREE.Points(geometry, material);
  const group = new THREE.Group();
  group.add(points);
  group.layers.set(LAYERS.ENTIRE_SCENE);
  scene.add(group);

  const POINTER = {
    world: new THREE.Vector3(),
    target: new THREE.Vector3(),
    activity: 0,
    active: false,
    lastMove: performance.now(),
  };

  const mouseNDC = { x: 0, y: 0 };
  const mouseSmooth = { x: 0, y: 0 };
  let uDriftAccum = 0;
  const appearStart = performance.now();

  function onPointerMove(e) {
    const rect = canvas.getBoundingClientRect();
    mouseNDC.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouseNDC.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    POINTER.active = true;
    POINTER.lastMove = performance.now();
  }
  function onPointerLeave() { POINTER.active = false; }

  canvas.addEventListener('mousemove', onPointerMove, { passive: true });
  canvas.addEventListener('mouseleave', onPointerLeave, { passive: true });

  function updatePointer() {
    if (POINTER.active) {
      const ndc = new THREE.Vector3(mouseNDC.x, mouseNDC.y, 0.5);
      const raycaster = new THREE.Raycaster();
      raycaster.setFromCamera(ndc, camera);
      const dir = raycaster.ray.direction;
      const camPos = camera.position;
      let target = new THREE.Vector3(0, 0, 0);
      if (Math.abs(dir.z) > 1e-4) {
        const t = -camPos.z / dir.z;
        if (t > 0 && isFinite(t)) target.copy(camPos).addScaledVector(dir, t);
      }
      POINTER.target.copy(target);
    }
    const idleSec = (performance.now() - POINTER.lastMove) / 1000;
    const want = POINTER.active && idleSec < 3 ? 1 : 0;
    POINTER.activity += (want - POINTER.activity) * 0.06;
    POINTER.world.lerp(POINTER.target, 0.12);
  }

  function resize() {
    const rect = hero.getBoundingClientRect();
    const w = rect.width;
    const h = rect.height;
    if (w < 1 || h < 1) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    torusComposer.setSize(w, h);
    bloomComposer.setSize(w, h);
    finalComposer.setSize(w, h);
    [torusComposer, bloomComposer].forEach(c => {
      c.passes.forEach(p => { if (p instanceof UnrealBloomPass && p.resolution) p.resolution.set(w, h); });
    });
  }

  let t0 = performance.now() / 1000;

  function render() {
    requestAnimationFrame(render);

    const now = performance.now() / 1000;
    const dt = Math.min(0.05, now - t0);
    t0 = now;

    mouseSmooth.x += (mouseNDC.x - mouseSmooth.x) * 0.06;
    mouseSmooth.y += (mouseNDC.y - mouseSmooth.y) * 0.06;

    updatePointer();

    uniforms.uTime.value = now;
    uDriftAccum += dt * CONFIG.drift;
    uniforms.uDrift.value = uDriftAccum;
    uniforms.uCursor.value.copy(POINTER.world);
    uniforms.uActivity.value = POINTER.activity;

    const camX = mouseSmooth.x * CONFIG.parallax;
    const camY = mouseSmooth.y * CONFIG.parallax;
    camera.position.set(camX, camY, 5);
    camera.lookAt(camX, camY, -10);

    const elapsed = performance.now() - appearStart;
    const fade = Math.min(Math.max((elapsed - 300) / 1400, 0), 1);
    uniforms.uOpacity.value = fade * CONFIG.opacity;

    group.rotation.z += dt * CONFIG.spin;

    finalPass.uniforms.iTime.value = now;

    camera.layers.set(LAYERS.TORUS_SCENE);
    torusComposer.render();
    camera.layers.set(LAYERS.BLOOM_SCENE);
    bloomComposer.render();
    camera.layers.set(LAYERS.ENTIRE_SCENE);
    finalComposer.render();
  }

  window.addEventListener('resize', resize, { passive: true });
  new ResizeObserver(resize).observe(hero);
  resize();
  render();
})();
