// Initialize AOS with updated settings
AOS.init({
  duration: 600,
  offset: 100,
  once: true,
  easing: "ease-out-cubic",
  anchorPlacement: "top-bottom",
  disable: window.innerWidth < 768 // Disable animations on mobile
});

// Scroll to top function
function scrollToTop(e) {
  e.preventDefault();
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
}

// Copy code functionality
function copyCode(button) {
  const codeBlock = button.closest(".hero-code").querySelector("code");
  const text = codeBlock.textContent;

  navigator.clipboard
    .writeText(text)
    .then(() => {
      // Visual feedback
      button.textContent = "Copied!";
      button.classList.add("copied");

      // Reset after 2 seconds
      setTimeout(() => {
        button.textContent = "Copy";
        button.classList.remove("copied");
      }, 2000);
    })
    .catch((err) => {
      console.error("Failed to copy:", err);
      button.textContent = "Failed to copy";
      setTimeout(() => {
        button.textContent = "Copy";
      }, 2000);
    });
}

// Example tabs with smooth reveal
function showExample(type) {
  document.querySelectorAll('[id^="example-"]').forEach((el) => {
    el.style.display = "none";
    el.setAttribute("data-aos-delay", "600");
  });

  const selectedExample = document.getElementById(`example-${type}`);
  selectedExample.style.display = "block";

  // Refresh AOS for the newly displayed element
  setTimeout(() => {
    AOS.refresh();
  }, 10);

  document.querySelectorAll(".tab-button").forEach((btn) => {
    btn.classList.remove("active");
  });
  event.target.classList.add("active");
}

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });
});

// Waves animation
let scene, camera, renderer, ribbon;
const container = document.querySelector("#waves");

const init = () => {
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(75, 1, 0.1, 10000);
  camera.position.z = 2;

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  container.appendChild(renderer.domElement);

  ribbon = new THREE.Mesh(
    new THREE.PlaneGeometry(1, 1, 128, 128),
    new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 1.0 },
      },
      vertexShader: `
        varying vec3 vEC;
        uniform float time;

        float iqhash(float n) {
          return fract(sin(n) * 43758.5453);
        }

        float noise(vec3 x) {
          vec3 p = floor(x);
          vec3 f = fract(x);
          f = f * f * (3.0 - 2.0 * f);
          float n = p.x + p.y * 57.0 + 113.0 * p.z;
          return mix(mix(mix(iqhash(n), iqhash(n + 1.0), f.x),
                     mix(iqhash(n + 57.0), iqhash(n + 58.0), f.x), f.y),
                     mix(mix(iqhash(n + 113.0), iqhash(n + 114.0), f.x),
                     mix(iqhash(n + 170.0), iqhash(n + 171.0), f.x), f.y), f.z);
        }

        float xmb_noise2(vec3 x) {
          return cos(x.z * 4.0) * cos(x.z + time / 10.0 + x.x);
        }

        void main() {
          vec4 pos = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          vec3 v = vec3(pos.x, 0.0, pos.y);
          vec3 v2 = v;
          vec3 v3 = v;

          v.y = xmb_noise2(v2) / 8.0;

          v3.x -= time / 5.0;
          v3.x /= 4.0;

          v3.z -= time / 10.0;
          v3.y -= time / 100.0;

          v.z -= noise(v3 * 7.0) / 15.0;
          v.y -= noise(v3 * 7.0) / 15.0 + cos(v.x * 2.0 - time / 2.0) / 5.0 - 0.3;

          vEC = v;
          gl_Position = vec4(v, 1.0);
        }
      `,
      fragmentShader: `
        uniform float time;
        varying vec3 vEC;

        void main() {
          const vec3 up = vec3(0.0, 0.0, 1.0);
          vec3 x = dFdx(vEC);
          vec3 y = dFdy(vEC);
          vec3 normal = normalize(cross(x, y));
          float c = 1.0 - dot(normal, up);
          c = (1.0 - cos(c * c)) / 3.0;
          gl_FragColor = vec4(1.0, 1.0, 1.0, c * 1.5);
        }
      `,
      extensions: {
        derivatives: true,
        fragDepth: false,
        drawBuffers: false,
        shaderTextureLOD: false,
      },
      side: THREE.DoubleSide,
      transparent: true,
      depthTest: false,
    })
  );

  scene.add(ribbon);
  resize();
  window.addEventListener("resize", resize);
};

const resize = () => {
  const { offsetWidth, offsetHeight } = container;
  renderer.setSize(offsetWidth, offsetHeight);
  renderer.setPixelRatio(devicePixelRatio);
  camera.aspect = offsetWidth / offsetHeight;
  camera.updateProjectionMatrix();
  ribbon.scale.set(camera.aspect * 1.55, 0.75, 1);
};

const animate = () => {
  ribbon.material.uniforms.time.value += 0.017;
  renderer.render(scene, camera);
  requestAnimationFrame(() => animate());
};

// Initialize waves animation if container exists
if (container) {
  init();
  animate();
}

// Initialize syntax highlighting with custom options
hljs.configure({
  languages: ["python"],
  cssSelector: "pre code",
});
hljs.highlightAll(); 