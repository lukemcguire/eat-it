import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { BottomNav } from './BottomNav';
import { Sidebar } from './Sidebar';

interface AppLayoutProps {
  title?: string;
  actions?: React.ReactNode;
}

export function AppLayout({ title = 'Eat It', actions }: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-[#0f1923]">
      <Sidebar />

      <div className="min-h-screen pb-20 lg:pb-0 lg:ml-64">
        <Header title={title} actions={actions} />
        <main className="p-4 lg:p-6 max-w-7xl mx-auto">
          <Outlet />
        </main>
      </div>

      <BottomNav />
    </div>
  );
}
