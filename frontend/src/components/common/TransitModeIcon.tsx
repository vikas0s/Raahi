import React from 'react';
import { Footprints, Train, Bus, Landmark } from 'lucide-react';
import { TransitMode } from '../../types/transit';

interface Props {
  mode: TransitMode;
  className?: string;
  size?: number;
}

export const TransitModeIcon: React.FC<Props> = ({ mode, className = '', size = 18 }) => {
  switch (mode) {
    case 'walk':
      return <Footprints size={size} className={`text-[#77776F] ${className}`} />;
    case 'metro':
      return <Train size={size} className={`text-[#64836D] ${className}`} />;
    case 'bus':
      return <Bus size={size} className={`text-[#C8795A] ${className}`} />;
    case 'rail':
      return <Landmark size={size} className={`text-[#304B3C] ${className}`} />;
    default:
      return <Train size={size} className={className} />;
  }
};
