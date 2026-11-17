import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatStatusLabel(assessment: string): string {
  switch (assessment) {
    case 'APPROVED':
      return 'Approved';
    case 'CAUTION':
      return 'Caution';
    case 'NEEDS_REVIEW':
      return 'Review';
    case 'BLOCKED':
    case 'NOT_APPROVED':
      return 'Blocked';
    default:
      return assessment;
  }
}

export function formatCategoryLabel(category: string): string {
  const map: Record<string, string> = {
    physical_harm_violence: 'Physical Harm & Violence',
    unauthorized_cybersecurity: 'Unauthorized Cybersecurity',
    discrimination_bias: 'Discrimination & Bias',
    fraud_deception: 'Fraud & Deception',
    privacy_surveillance: 'Privacy & Surveillance',
    harassment_abuse: 'Harassment & Abuse',
    misinformation_manipulation: 'Misinformation & Manipulation',
    instruction_integrity: 'Instruction Integrity',
    other_unethical_risk: 'Other Unethical Risk',
    benign_educational: 'Educational & Defensive',
    benign_general: 'General Inquiry',
    ambiguous_context: 'Ambiguous Context',
    // Legacy mappings
    privacy_exposure: 'Privacy',
    fairness_bias: 'Fairness & Bias',
    misleading_communication: 'Deception & Fraud',
    harmful_content: 'Physical Safety',
  };
  return map[category] || category.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
}

export function formatIntentLabel(intent: string): string {
  const map: Record<string, string> = {
    harmful_instruction: 'Harmful Instruction',
    educational_explanation: 'Educational Explanation',
    defensive_safety: 'Defensive / Safety',
    ethical_analysis_quote: 'Ethical Analysis (Quoted)',
    hypothetical_discussion: 'Hypothetical Discussion',
    ambiguous_context: 'Ambiguous Context',
    benign_general: 'General Inquiry',
  };
  return map[intent] || intent.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
}

export function formatAnalysisModeLabel(mode: string): string {
  switch (mode) {
    case 'hybrid':
      return 'Hybrid AI (Rules + Semantic)';
    case 'semantic':
      return 'Semantic AI';
    case 'local':
      return 'Local Policy Rules';
    default:
      return mode;
  }
}

export function formatDateTime(iso: string): string {
  if (!iso) return '—';
  try {
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}
