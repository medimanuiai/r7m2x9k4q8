import { useEffect, useRef } from 'react';

/**
 * LoginBackground
 *
 * Props:
 *   darkMode       {boolean}  – switches to deep cosmic gradient
 *   accentColor    {string}   – optional CSS color to tint overlay
 *   blurIntensity  {number}   – px value for backdrop-filter blur
 *   overlayOpacity {number}   – 0–1 opacity for dot overlay (default 0.15)
 */
export default function LoginBackground({
  darkMode       = false,
  accentColor,
  blurIntensity  = 0,
  overlayOpacity = 0.15,
}) {
  const silRef = useRef(null);

  // Parallax on pointer move
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const handle = (e) => {
      if (!silRef.current) return;
      const x = (e.clientX / window.innerWidth  - 0.5) * 14;
      const y = (e.clientY / window.innerHeight - 0.5) * 10;
      silRef.current.style.transform = `translate(${x}px, ${y}px)`;
    };
    window.addEventListener('mousemove', handle);
    return () => window.removeEventListener('mousemove', handle);
  }, []);

  const bgGradient = darkMode
    ? 'linear-gradient(135deg, #0f2027 0%, #203a43 40%, #2c5364 100%)'
    : 'linear-gradient(135deg, #43e8d8 0%, #4e9df5 35%, #9e5ee3 70%, #f064d2 100%)';

  return (
    <div
      className="fixed inset-0 overflow-hidden"
      style={{ background: bgGradient }}
      aria-hidden="true"
      role="presentation"
    >
      {/* Geometric shapes */}
      <div className="auth-bg-shape-1" />
      <div className="auth-bg-shape-2" />

      {/* Dot / star overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          opacity: overlayOpacity,
          backgroundImage: `
            radial-gradient(circle, rgba(255,255,255,0.22) 1px, transparent 1px),
            radial-gradient(circle, rgba(255,255,255,0.12) 1px, transparent 1px)
          `,
          backgroundSize: '44px 44px, 22px 22px',
          backgroundPosition: '0 0, 11px 11px',
          ...(blurIntensity ? { backdropFilter: `blur(${blurIntensity}px)` } : {}),
          ...(accentColor ? { backgroundColor: accentColor } : {}),
        }}
      />

      {/* Yoga / meditation silhouette */}
      <div
        ref={silRef}
        className="absolute inset-0 flex items-center justify-center pointer-events-none transition-transform duration-75"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 200 250"
          className="animate-breathe opacity-[0.18]"
          style={{ width: 'min(260px, 28vw)', height: 'auto' }}
          aria-hidden="true"
          focusable="false"
        >
          <g fill="white">
            <ellipse cx="100" cy="31" rx="19" ry="21"/>
            <path d="M90 50 Q100 57 110 50 L108 63 Q100 67 92 63Z"/>
            <path d="M92 63 Q73 69 66 87 Q84 95 100 93 Q116 95 134 87 Q127 69 108 63Z"/>
            <path d="M66 87 Q60 108 58 124 L100 130 L142 124 Q140 108 134 87Z"/>
            <path d="M70 75 Q55 85 45 98 Q38 111 41 123 Q50 126 56 119 Q56 108 63 98 Q72 88 78 80Z"/>
            <path d="M130 75 Q145 85 155 98 Q162 111 159 123 Q150 126 144 119 Q144 108 137 98 Q128 88 122 80Z"/>
            <path d="M58 124 Q46 142 44 162 Q46 177 60 182 Q77 187 92 179 Q88 163 84 148 Q75 136 58 124Z"/>
            <path d="M142 124 Q154 142 156 162 Q154 177 140 182 Q123 187 108 179 Q112 163 116 148 Q125 136 142 124Z"/>
            <ellipse cx="44"  cy="125" rx="11" ry="7" transform="rotate(-8 44 125)"/>
            <ellipse cx="156" cy="125" rx="11" ry="7" transform="rotate(8 156 125)"/>
            <circle cx="100" cy="31"  r="30"  fill="none" stroke="white" strokeWidth="0.8" opacity="0.35"/>
            <circle cx="100" cy="125" r="85"  fill="none" stroke="white" strokeWidth="0.5" opacity="0.15"/>
          </g>
        </svg>
      </div>
    </div>
  );
}
