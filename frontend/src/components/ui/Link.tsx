import Link from 'next/link';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const linkVariants = cva(
  'font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'text-primary-600 hover:text-primary-700',
        destructive: 'text-danger-600 hover:text-danger-700',
        outline: 'border border-gray-300 bg-white hover:bg-gray-50',
        secondary: 'text-gray-600 hover:text-gray-900',
        ghost: 'hover:bg-gray-100',
        link: 'text-primary-600 underline-offset-4 hover:underline',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

export interface LinkProps
  extends React.AnchorHTMLAttributes<HTMLAnchorElement>,
    VariantProps<typeof linkVariants> {
  href: string;
}

const CustomLink = ({ className, variant, href, ...props }: LinkProps) => {
  return (
    <Link
      href={href}
      className={cn(linkVariants({ variant, className }))}
      {...props}
    />
  );
};

CustomLink.displayName = 'Link';

export { CustomLink as Link, linkVariants };
