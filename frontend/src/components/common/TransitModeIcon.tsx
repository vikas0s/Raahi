import React from 'react';
import { Footprints, Train, Bus, CarTaxiFront, Car, Zap } from 'lucide-react';
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
    case 'ebus':
      return <Bus size={size} className={`text-[#00A86B] ${className}`} />;
    case 'auto':
      return <CarTaxiFront size={size} className={`text-[#E68A00] ${className}`} />;
    case 'taxi':
      return <Car size={size} className={`text-[#3B5360] ${className}`} />;
    case 'erickshaw':
      return <Zap size={size} className={`text-[#00897B] ${className}`} />;
    case 'rail':
      return <Train size={size} className={`text-[#8B1E1E] ${className}`} />;
    default:
      return <Train size={size} className={className} />;
  }
};
