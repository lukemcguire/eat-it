import { NavLink, useLocation } from 'react-router-dom';
import { BookOpen, ShoppingCart, Search, PlusCircle } from 'lucide-react';

const navItems = [
  { path: '/', label: 'Recipe Binder', icon: BookOpen },
  { path: '/shopping', label: 'Shopping List', icon: ShoppingCart },
  { path: '/search', label: 'Search', icon: Search },
  { path: '/import', label: 'Add/Import', icon: PlusCircle },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="fixed left-0 top-0 bottom-0 z-40 w-64 bg-[#0f172a] border-r border-[#2e4e6b] hidden lg:flex flex-col">
      <div className="h-16 flex items-center px-6 border-b border-[#2e4e6b]">
        <span className="text-xl font-bold text-white">Eat It</span>
      </div>

      <nav className="flex-1 py-4 px-3">
        <ul className="space-y-1">
          {navItems.map(({ path, label, icon: Icon }) => {
            const isActive = location.pathname === path;
            return (
              <li key={path}>
                <NavLink
                  to={path}
                  className={`
                    flex items-center gap-3
                    min-h-[44px] px-3 py-3
                    rounded-xl font-medium transition-colors
                    ${isActive
                      ? 'bg-[#207fdf]/20 text-[#207fdf]'
                      : 'text-[#94a3b8] hover:text-[#f1f5f9] hover:bg-[#1a2632]'
                    }
                  `}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon className="w-5 h-5" />
                  <span>{label}</span>
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
}
