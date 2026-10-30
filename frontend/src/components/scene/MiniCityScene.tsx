import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

// Animated Metro Train moving back and forth smoothly
const MetroTrain: React.FC = () => {
  const trainRef = useRef<THREE.Group>(null);

  useFrame(() => {
    if (trainRef.current) {
      const t = performance.now() * 0.001 * 0.4;
      // Linear smooth back-and-forth transit loop
      trainRef.current.position.x = Math.sin(t) * 2.8;
    }
  });

  return (
    <group ref={trainRef} position={[0, 0.42, 0.9]}>
      {/* Metro track viaduct */}
      <mesh position={[0, -0.15, 0]}>
        <boxGeometry args={[0.9, 0.12, 0.22]} />
        <meshStandardMaterial color="#64836D" roughness={0.4} />
      </mesh>
      {/* Yellow line stripe */}
      <mesh position={[0, -0.12, 0.115]}>
        <boxGeometry args={[0.85, 0.02, 0.01]} />
        <meshBasicMaterial color="#E5A919" />
      </mesh>
      {/* Windows */}
      <mesh position={[0, -0.10, 0]}>
        <boxGeometry args={[0.7, 0.04, 0.23]} />
        <meshBasicMaterial color="#304B3C" />
      </mesh>
    </group>
  );
};

// Animated Electric Bus moving along the road
const ElectricBus: React.FC = () => {
  const busRef = useRef<THREE.Group>(null);

  useFrame(() => {
    if (busRef.current) {
      const t = performance.now() * 0.001 * 0.25;
      busRef.current.position.z = Math.cos(t) * 2.2;
    }
  });

  return (
    <group ref={busRef} position={[-0.8, 0.15, 0]}>
      {/* DTC Green electric bus body */}
      <mesh>
        <boxGeometry args={[0.22, 0.16, 0.55]} />
        <meshStandardMaterial color="#2E7D32" roughness={0.3} />
      </mesh>
      {/* Bus roof white */}
      <mesh position={[0, 0.085, 0]}>
        <boxGeometry args={[0.21, 0.02, 0.53]} />
        <meshStandardMaterial color="#EEECE3" />
      </mesh>
      {/* Windshield */}
      <mesh position={[0, 0.02, 0.28]}>
        <boxGeometry args={[0.18, 0.08, 0.02]} />
        <meshBasicMaterial color="#304B3C" />
      </mesh>
    </group>
  );
};

// Isometric Buildings & City Environment
const CityEnvironment: React.FC = () => {
  return (
    <group>
      {/* Ground Base / Warm Ivory Slab */}
      <mesh position={[0, -0.05, 0]} receiveShadow>
        <boxGeometry args={[7, 0.1, 7]} />
        <meshStandardMaterial color="#EEECE3" roughness={0.9} />
      </mesh>

      {/* Roads */}
      {/* East-West Metro Viaduct */}
      <mesh position={[0, 0.22, 0.9]}>
        <boxGeometry args={[6.5, 0.05, 0.35]} />
        <meshStandardMaterial color="#D7D4CA" roughness={0.6} />
      </mesh>
      {/* Viaduct pillars */}
      {[-2, -1, 0, 1, 2].map((x) => (
        <mesh key={x} position={[x, 0.1, 0.9]}>
          <cylinderGeometry args={[0.06, 0.06, 0.2, 12]} />
          <meshStandardMaterial color="#C4C0B5" />
        </mesh>
      ))}

      {/* North-South Road */}
      <mesh position={[-0.8, 0.01, 0]}>
        <boxGeometry args={[0.65, 0.02, 6.5]} />
        <meshStandardMaterial color="#DDD9CE" roughness={0.8} />
      </mesh>

      {/* Buildings: Terracotta & Sage Warm Minimal Blocks */}
      {/* Tall Modern Office */}
      <mesh position={[1.4, 0.8, -1.2]} castShadow>
        <boxGeometry args={[0.9, 1.6, 0.9]} />
        <meshStandardMaterial color="#64836D" roughness={0.5} />
      </mesh>
      {/* Building roof cap */}
      <mesh position={[1.4, 1.62, -1.2]}>
        <boxGeometry args={[0.7, 0.05, 0.7]} />
        <meshStandardMaterial color="#304B3C" />
      </mesh>

      {/* Mid-rise Landmark (Terracotta) */}
      <mesh position={[-1.8, 0.5, -1.0]} castShadow>
        <boxGeometry args={[1.0, 1.0, 1.1]} />
        <meshStandardMaterial color="#C8795A" roughness={0.6} />
      </mesh>

      {/* Heritage / Station Canopy */}
      <mesh position={[0.8, 0.35, 1.8]} castShadow>
        <boxGeometry args={[1.2, 0.7, 0.8]} />
        <meshStandardMaterial color="#E3DFD4" roughness={0.7} />
      </mesh>
      {/* Yellow canopy highlight */}
      <mesh position={[0.8, 0.72, 1.8]}>
        <boxGeometry args={[1.3, 0.04, 0.9]} />
        <meshStandardMaterial color="#E7B75B" roughness={0.4} />
      </mesh>

      {/* Indian Neem / Ashoka Stylized Low-poly Trees */}
      {[
        [-0.2, 0.25, -0.5],
        [0.3, 0.25, -0.6],
        [-1.5, 0.25, 1.2],
        [2.2, 0.25, 0.2],
        [-2.2, 0.25, -2.0]
      ].map(([x, y, z], idx) => (
        <group key={idx} position={[x, y, z]}>
          <mesh position={[0, -0.1, 0]}>
            <cylinderGeometry args={[0.03, 0.04, 0.2, 8]} />
            <meshStandardMaterial color="#8D7A68" />
          </mesh>
          <mesh position={[0, 0.08, 0]}>
            <sphereGeometry args={[0.16, 8, 8]} />
            <meshStandardMaterial color="#5B8A6E" roughness={0.8} />
          </mesh>
        </group>
      ))}

      {/* Metro Station Marker Pin */}
      <group position={[0, 0.8, 0.9]}>
        <mesh>
          <sphereGeometry args={[0.09, 12, 12]} />
          <meshBasicMaterial color="#E5A919" />
        </mesh>
        <mesh position={[0, -0.18, 0]}>
          <cylinderGeometry args={[0.015, 0.015, 0.25, 8]} />
          <meshBasicMaterial color="#304B3C" />
        </mesh>
      </group>
    </group>
  );
};

// Camera drift controller
const CameraController: React.FC<{ mousePos: { x: number; y: number } }> = ({ mousePos }) => {
  useFrame(({ camera }) => {
    const elapsed = performance.now() * 0.001 * 0.15;
    const targetX = 4.2 + Math.sin(elapsed) * 0.4 + mousePos.x * 0.5;
    const targetY = 3.6 + Math.cos(elapsed * 0.8) * 0.2 - mousePos.y * 0.3;
    const targetZ = 4.2 + Math.cos(elapsed) * 0.4;

    camera.position.x = THREE.MathUtils.lerp(camera.position.x, targetX, 0.04);
    camera.position.y = THREE.MathUtils.lerp(camera.position.y, targetY, 0.04);
    camera.position.z = THREE.MathUtils.lerp(camera.position.z, targetZ, 0.04);
    camera.lookAt(0, 0.3, 0);
  });
  return null;
};

// Static Fallback for low power or prefers-reduced-motion
const StaticCityFallback: React.FC = () => {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-[#EEECE3] to-[#F7F5EF] rounded-2xl border border-[#E3E0D6] p-6 relative overflow-hidden">
      <div className="absolute inset-0 opacity-15 bg-[radial-gradient(#64836D_1px,transparent_1px)] [background-size:16px_16px]" />
      <div className="relative z-10 flex flex-col items-center text-center">
        <div className="w-16 h-16 rounded-2xl bg-[#64836D]/15 flex items-center justify-center text-[#304B3C] mb-3">
          <svg className="w-9 h-9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
            <rect x="4" y="3" width="16" height="16" rx="2" />
            <path d="M4 11h16" />
            <path d="M12 3v8" />
            <circle cx="8" cy="15" r="1" />
            <circle cx="16" cy="15" r="1" />
          </svg>
        </div>
        <h4 className="font-heading font-medium text-base text-[#292D29]">City Transit Grid</h4>
        <p className="text-xs text-[#77776F] max-w-xs mt-1">
          Connected Metro, Electric Bus, and Suburban Rail network.
        </p>
      </div>
    </div>
  );
};

export const MiniCityScene: React.FC = () => {
  const [hasWebGL, setHasWebGL] = useState(true);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    try {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      if (!gl) setHasWebGL(false);
    } catch {
      setHasWebGL(false);
    }
  }, []);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const y = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
    setMousePos({ x, y });
  };

  if (!hasWebGL) {
    return <StaticCityFallback />;
  }

  return (
    <div
      className="w-full h-full min-h-[220px] rounded-2xl overflow-hidden relative border border-[#E3E0D6] bg-[#EEECE3]/60 shadow-[0_4px_20px_-4px_rgba(48,75,60,0.06)]"
      onMouseMove={handleMouseMove}
    >
      <div className="absolute top-3 left-3 z-10 pointer-events-none flex items-center gap-2">
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-[#F7F5EF]/85 backdrop-blur-sm text-[#304B3C] border border-[#E3E0D6]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#5B8A6E] animate-pulse" />
          Live 3D Transit Grid
        </span>
      </div>

      <Canvas
        camera={{ position: [4.2, 3.6, 4.2], fov: 38 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={1.1} />
        <directionalLight position={[6, 9, 4]} intensity={1.5} color="#FFFBF0" castShadow />
        <directionalLight position={[-4, 3, -4]} intensity={0.5} color="#D7E1D8" />

        <CameraController mousePos={mousePos} />
        <CityEnvironment />
        <MetroTrain />
        <ElectricBus />
      </Canvas>
    </div>
  );
};
