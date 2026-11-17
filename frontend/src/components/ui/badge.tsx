import React from 'react';
import { cn } from '../../lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'secondary' | 'outline' | 'success' | 'warning' | 'error' | 'info';
}

export const Badge: React.FC<BadgeProps> = ({ className, variant = 'default', ...props }) => {
  const variants = {
    default: 'bg-[#2563EB]/10 text-[#2563EB] border-[#2563EB]/20',
    secondary: 'bg-slate-100 text-[#475569] border-slate-200',
    outline: 'bg-white text-[#475569] border-[#E2E8F0]',
    success: 'bg-emerald-50 text-[#059669] border-emerald-200/80',
    warning: 'bg-amber-50 text-[#D97706] border-amber-200/80',
    error: 'bg-red-50 text-[#DC2626] border-red-200/80',
    info: 'bg-blue-50 text-[#2563EB] border-blue-200/80',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[12px] font-medium leading-tight whitespace-nowrap',
        variants[variant],
        className
      )}
      {...props}
    />
  );
};

export function getAssessmentBadgeVariant(assessment: string): BadgeProps['variant'] {
  switch (assessment) {
    case 'APPROVED':
      return 'success';
    case 'CAUTION':
      return 'warning';
    case 'NEEDS_REVIEW':
      return 'info';
    case 'BLOCKED':
    case 'NOT_APPROVED':
      return 'error';
    default:
      return 'secondary';
  }
}
