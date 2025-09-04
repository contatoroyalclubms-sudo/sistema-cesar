import React from 'react';
import { LucideIcon } from 'lucide-react';
import { Button } from '../ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '../ui/tooltip';

interface ActionButtonProps {
  icon: LucideIcon;
  tooltip: string;
  onClick: () => void;
  color?: 'blue' | 'green' | 'red' | 'orange' | 'purple' | 'gray';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  variant?: 'solid' | 'outline' | 'ghost';
}

const ActionButton: React.FC<ActionButtonProps> = ({
  icon: Icon,
  tooltip,
  onClick,
  color = 'blue',
  size = 'md',
  disabled = false,
  variant = 'solid'
}) => {
  const colorClasses = {
    solid: {
      blue: 'bg-blue-600 hover:bg-blue-700 text-white',
      green: 'bg-green-600 hover:bg-green-700 text-white',
      red: 'bg-red-600 hover:bg-red-700 text-white',
      orange: 'bg-orange-600 hover:bg-orange-700 text-white',
      purple: 'bg-purple-600 hover:bg-purple-700 text-white',
      gray: 'bg-gray-600 hover:bg-gray-700 text-white'
    },
    outline: {
      blue: 'border-blue-600 text-blue-600 hover:bg-blue-50',
      green: 'border-green-600 text-green-600 hover:bg-green-50',
      red: 'border-red-600 text-red-600 hover:bg-red-50',
      orange: 'border-orange-600 text-orange-600 hover:bg-orange-50',
      purple: 'border-purple-600 text-purple-600 hover:bg-purple-50',
      gray: 'border-gray-600 text-gray-600 hover:bg-gray-50'
    },
    ghost: {
      blue: 'text-blue-600 hover:bg-blue-50',
      green: 'text-green-600 hover:bg-green-50',
      red: 'text-red-600 hover:bg-red-50',
      orange: 'text-orange-600 hover:bg-orange-50',
      purple: 'text-purple-600 hover:bg-purple-50',
      gray: 'text-gray-600 hover:bg-gray-50'
    }
  };

  const sizeClasses = {
    sm: 'h-8 w-8 p-1.5',
    md: 'h-9 w-9 p-2',
    lg: 'h-10 w-10 p-2.5'
  };

  const iconSizes = {
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5'
  };

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            onClick={onClick}
            disabled={disabled}
            variant={variant === 'solid' ? 'default' : variant === 'outline' ? 'outline' : 'ghost'}
            size="sm"
            className={`
              ${sizeClasses[size]}
              ${colorClasses[variant][color]}
              transition-all duration-200
              ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <Icon className={iconSizes[size]} />
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>{tooltip}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

export default ActionButton;