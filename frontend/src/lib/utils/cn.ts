import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Utility function to merge class names using clsx and tailwind-merge
 * This allows for conditional classes and proper Tailwind class merging
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Create variant-based className utilities
 */
export function createVariants<T extends Record<string, Record<string, string>>>(
  variants: T
) {
  return function getVariant<K extends keyof T>(
    variant: K,
    value: keyof T[K]
  ): string {
    return variants[variant][value] || "";
  };
}

/**
 * Common variant definitions for consistent styling
 */
export const variants = {
  size: {
    sm: "text-sm px-2 py-1",
    md: "text-base px-3 py-2", 
    lg: "text-lg px-4 py-3",
    xl: "text-xl px-6 py-4",
  },
  intent: {
    primary: "bg-primary text-primary-foreground hover:bg-primary/90",
    secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
    destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
    outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
    ghost: "hover:bg-accent hover:text-accent-foreground",
    link: "text-primary underline-offset-4 hover:underline",
  },
  spacing: {
    tight: "space-y-1",
    normal: "space-y-2", 
    relaxed: "space-y-4",
    loose: "space-y-6",
  },
} as const;

export const getVariant = createVariants(variants);