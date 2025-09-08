import React from 'react';
import { motion } from 'framer-motion';

interface StatusToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  color?: 'green' | 'blue' | 'purple' | 'yellow' | 'red';
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}

const StatusToggle: React.FC<StatusToggleProps> = ({
  checked,
  onChange,
  color = 'green',
  disabled = false,
  size = 'md',
  label
}) => {
  const colorClasses = {
    green: checked ? 'bg-green-600' : 'bg-gray-200',
    blue: checked ? 'bg-blue-600' : 'bg-gray-200',
    purple: checked ? 'bg-purple-600' : 'bg-gray-200',
    yellow: checked ? 'bg-yellow-500' : 'bg-gray-200',
    red: checked ? 'bg-red-600' : 'bg-gray-200'
  };

  const sizeClasses = {
    sm: { toggle: 'h-4 w-8', thumb: 'h-3 w-3' },
    md: { toggle: 'h-6 w-11', thumb: 'h-4 w-4' },
    lg: { toggle: 'h-8 w-14', thumb: 'h-6 w-6' }
  };

  return (
    <div className="flex items-center space-x-2">
      <button
        type="button"
        disabled={disabled}
        onClick={() => onChange(!checked)}
        className={`
          relative inline-flex items-center rounded-full transition-colors duration-200 ease-in-out
          ${sizeClasses[size].toggle}
          ${colorClasses[color]}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-white focus:ring-blue-500'}
        `}
        aria-pressed={checked}
      >
        <motion.span
          animate={{ 
            x: checked ? 
              (size === 'sm' ? 16 : size === 'md' ? 20 : 24) : 
              (size === 'sm' ? 2 : size === 'md' ? 4 : 4)
          }}
          transition={{ duration: 0.2, ease: "easeInOut" }}
          className={`
            inline-block transform rounded-full bg-white shadow-sm transition-transform
            ${sizeClasses[size].thumb}
          `}
        />
      </button>
      {label && (
        <span className={`text-sm ${disabled ? 'text-gray-400' : 'text-gray-700'}`}>
          {label}
        </span>
      )}
    </div>
  );
};

export default StatusToggle;