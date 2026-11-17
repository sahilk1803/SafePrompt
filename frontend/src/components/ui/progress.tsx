import React from 'react';
import { cn } from '../../lib/utils';

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number;
  indicatorClassName?: string;
}

export const Progress: React.FC<ProgressProps> = ({
  value = 0,
  className,
  indicatorClassName,
  ...props
}) => {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div
      className={cn('relative h-2 w-full overflow-hidden rounded-full bg-slate-100', className)}
      {...props}
    >
      <div
        className={cn('h-full rounded-full bg-[#2563EB] transition-all duration-300', indicatorClassName)}
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
};
