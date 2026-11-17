import React from 'react';
import { cn } from '../../lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'secondary' | 'outline' | 'ghost' | 'destructive';
  size?: 'default' | 'sm' | 'lg' | 'icon';
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'default', ...props }, ref) => {
    const variants = {
      default: 'bg-[#2563EB] text-white hover:bg-[#1D4ED8] shadow-sm border border-transparent',
      secondary: 'bg-slate-100 text-[#0F172A] hover:bg-slate-200 border border-transparent',
      outline: 'bg-[#FFFFFF] text-[#0F172A] border border-[#E2E8F0] hover:bg-slate-50 shadow-sm',
      ghost: 'bg-transparent text-[#64748B] hover:bg-slate-100 hover:text-[#0F172A]',
      destructive: 'bg-[#DC2626] text-white hover:bg-red-700 shadow-sm border border-transparent',
    };

    const sizes = {
      default: 'h-9 px-4 py-2 text-[13px]',
      sm: 'h-8 px-3 text-[12px]',
      lg: 'h-10 px-5 text-[14px]',
      icon: 'h-9 w-9 p-0',
    };

    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2563EB]/40 disabled:pointer-events-none disabled:opacity-50',
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';
