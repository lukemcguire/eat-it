import { Menu, Settings } from 'lucide-react';
import { TouchButton } from '@/components/ui/TouchButton';

interface HeaderProps {
  title: string;
  onMenuClick?: () => void;
  actions?: React.ReactNode;
}

export function Header({ title, onMenuClick, actions }: HeaderProps) {
  return (
    <header className="sticky top-0 z-40 h-16 bg-[#0f172a]/95 backdrop-blur-md border-b border-[#2e4e6b]">
      <div className="flex items-center justify-between h-full px-4 lg:px-6">
        <div className="flex items-center gap-3">
          {onMenuClick && (
            <TouchButton
              variant="ghost"
              size="icon"
              onClick={onMenuClick}
              className="lg:hidden"
              aria-label="Open menu"
            >
              <Menu className="w-5 h-5" />
            </TouchButton>
          )}
          <h1 className="text-xl font-bold text-white truncate">{title}</h1>
        </div>

        <div className="flex items-center gap-2">
          {actions}
          <TouchButton
            variant="ghost"
            size="icon"
            aria-label="Settings"
          >
            <Settings className="w-5 h-5" />
          </TouchButton>
        </div>
      </div>
    </header>
  );
}
