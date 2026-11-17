import React from 'react';
import { cn } from '../../lib/utils';

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'info' | 'success' | 'warning' | 'error';
}

export const Alert: React.FC<AlertProps> = ({ className, variant = 'default', ...props }) => {
  const variants = {
    default: 'bg-slate-50 border-[#E2E8F0] text-[#0F172A]',
    info: 'bg-blue-50/70 border-blue-200 text-blue-950',
    success: 'bg-emerald-50/70 border-emerald-200 text-emerald-950',
    warning: 'bg-amber-50/70 border-amber-200 text-amber-950',
    error: 'bg-red-50/70 border-red-200 text-red-950',
  };

  return (
    <div
      role="alert"
      className={cn(
        'relative flex w-full items-start gap-3 rounded-xl border p-4 text-[13px]',
        variants[variant],
        className
      )}
      {...props}
    />
  );
};

export const AlertTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
  className,
  ...props
}) => <h5 className={cn('font-semibold leading-none tracking-tight mb-1', className)} {...props} />;

export const AlertDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({
  className,
  ...props
}) => <div className={cn('text-[13px] opacity-90 leading-relaxed', className)} {...props} />;
