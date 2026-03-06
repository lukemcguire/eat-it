import React from 'react';
import { useShoppingList } from '../../hooks';
import { shoppingListTabs, bottomNavItems } from '../../data/mockData';
import { Icon, Button } from '../ui';

interface ShoppingItemRowProps {
  readonly id: string;
  readonly name: string;
  readonly checked: boolean;
  readonly onToggle: () => void;
}

const ShoppingItemRow: React.FC<ShoppingItemRowProps> = ({
  name,
  checked,
  onToggle,
}) => {
  return (
    <div className="flex items-center gap-4 px-6 py-4 transition-colors hover:bg-slate-50 dark:hover:bg-surface-dark">
      <label className="flex flex-1 items-center gap-4 cursor-pointer">
        <input
          type="checkbox"
          checked={checked}
          onChange={onToggle}
          className="h-6 w-6 rounded border-slate-300 dark:border-border-dark bg-transparent text-primary focus:ring-primary focus:ring-offset-0"
        />
        <p
          className={`text-base font-medium ${
            checked ? 'line-through opacity-50' : ''
          }`}
        >
          {name}
        </p>
      </label>
      <Icon name="drag_indicator" className="text-slate-400 cursor-grab" />
    </div>
  );
};

interface ShoppingSectionProps {
  readonly id: string;
  readonly title: string;
  readonly items: readonly { id: string; name: string; checked: boolean }[];
  readonly onToggleItem: (itemId: string) => void;
}

const ShoppingSection: React.FC<ShoppingSectionProps> = ({
  title,
  items,
  onToggleItem,
}) => {
  return (
    <section className="mt-4">
      <div className="flex items-center justify-between px-6 py-2 bg-slate-50 dark:bg-surface-dark">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          {title}
        </h3>
        <span className="text-xs font-medium text-slate-400">
          {items.length} item{items.length !== 1 ? 's' : ''}
        </span>
      </div>
      <div className="divide-y divide-slate-100 dark:divide-border-dark">
        {items.map((item) => (
          <ShoppingItemRow
            key={item.id}
            {...item}
            onToggle={() => onToggleItem(item.id)}
          />
        ))}
      </div>
    </section>
  );
};

interface ShoppingListScreenProps {
  readonly className?: string;
}

export const ShoppingListScreen: React.FC<ShoppingListScreenProps> = ({
  className = '',
}) => {
  const { sections, toggleItem, activeTab, setActiveTab } = useShoppingList();

  return (
    <div
      className={`relative flex h-screen w-full flex-col overflow-hidden bg-background-dark ${className}`}
    >
      {/* Mobile Container */}
      <div className="mx-auto flex h-full w-full max-w-[480px] flex-col border-x border-border-dark bg-background-dark shadow-2xl">
        {/* Header */}
        <header className="flex flex-col border-b border-border-dark pt-4 bg-background-dark sticky top-0 z-10">
          <div className="flex items-center justify-between px-6 pb-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-white">
                <Icon name="shopping_basket" />
              </div>
              <h1 className="text-xl font-bold tracking-tight text-white">
                Weekly Groceries
              </h1>
            </div>
            <div className="flex gap-2">
              <button className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-dark hover:bg-slate-700 transition-colors">
                <Icon name="search" className="text-xl text-slate-200" />
              </button>
              <button className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-dark hover:bg-slate-700 transition-colors">
                <Icon name="more_vert" className="text-xl text-slate-200" />
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex px-6 gap-6">
            {shoppingListTabs.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`border-b-2 pb-3 text-sm font-bold transition-colors ${
                  activeTab === tab
                    ? 'border-primary text-primary'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto pb-32">
          {sections.map((section) => (
            <ShoppingSection
              key={section.id}
              id={section.id}
              title={section.title}
              items={section.items}
              onToggleItem={(itemId) => toggleItem(section.id, itemId)}
            />
          ))}
        </main>

        {/* Floating Action Button */}
        <div className="absolute bottom-20 left-0 right-0 p-6 bg-gradient-to-t from-background-dark via-background-dark/90 to-transparent pointer-events-none">
          <Button
            icon="add"
            size="large"
            className="pointer-events-auto w-full shadow-xl"
          >
            Add Item
          </Button>
        </div>

        {/* Bottom Navigation */}
        <nav className="flex items-center justify-around border-t border-border-dark bg-surface-dark/80 backdrop-blur-md px-4 py-3 pb-8">
          {bottomNavItems.map((item, index) => (
            <button
              key={item.label}
              className={`flex flex-col items-center gap-1 transition-colors ${
                index === 0 ? 'text-primary' : 'text-slate-400 hover:text-primary'
              }`}
            >
              <Icon name={item.icon} />
              <span className="text-[10px] font-bold uppercase tracking-tighter">
                {item.label}
              </span>
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
};

export default ShoppingListScreen;
