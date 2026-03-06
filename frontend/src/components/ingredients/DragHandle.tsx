import { GripVertical } from 'lucide-react';
import { cn } from '@/lib/utils';
import { forwardRef, type HTMLAttributes } from 'react';

interface DragHandleProps extends HTMLAttributes<HTMLDivElement> {}

export const DragHandle = forwardRef<HTMLDivElement, DragHandleProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'cursor-grab active:cursor-grabbing text-slate-400 hover:text-slate-200',
          'p-1 touch-none select-none',
          className
        )}
        {...props}
      >
        <GripVertical className="w-4 h-4" />
      </div>
    );
  }
);

DragHandle.displayName = 'DragHandle';
