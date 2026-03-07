import { NavLink, useLocation } from 'react-router-dom';
import { BookOpen, ShoppingCart, Search, PlusCircle } from 'lucide-react';

const navItems = [
  { path: '/recipes', label: 'Recipe Binder', icon: BookOpen },
  { path: '/shopping', label: 'Shopping List', icon: ShoppingCart },
  { path: '/search', label: 'Search', icon: Search },
  { path: '/import', label: 'Add/Import', icon: PlusCircle },
];

export function BottomNav() {
  const location = useLocation();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-[#0f172a] border-t border-[#2e4e6b] lg:hidden">
      <div className="flex items-center justify-around h-16 max-w-lg mx-auto">
        {navItems.map(({ path, label, icon: Icon }) => {
          const isActive = location.pathname.startsWith(path);
          return (
            <NavLink
              key={path}
              to={path}
              className={`
                flex flex-col items-center justify-center
                min-h-[44px] min-w-[44px] px-3 py-2
                rounded-lg transition-colors
                ${isActive
                  ? 'text-[#207fdf]'
                  : 'text-[#94a3b8] hover:text-[#f1f5f9]'
                }
              `}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon className="w-5 h-5" />
              <span className="text-xs mt-1 font-medium">{label}</span>
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
}
