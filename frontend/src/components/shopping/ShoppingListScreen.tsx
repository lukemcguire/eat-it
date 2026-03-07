import React, { useState, useMemo } from 'react';
import {
  useShoppingList,
  useUpdateShoppingListItem,
  useStoreSections,
} from '../../hooks';
import { bottomNavItems } from '../../data/mockData';
import { Icon, Button } from '../ui';
import type { ShoppingListItem as ShoppingListItemType } from '@/types/shopping';

interface ShoppingItemRowProps {
  readonly item: ShoppingListItemType;
  readonly onToggle: () => void;
}

const ShoppingItemRow: React.FC<ShoppingItemRowProps> = ({
  item,
  onToggle,
}) => {
  return (
    <div className="flex items-center gap-4 px-6 py-4 transition-colors hover:bg-slate-50 dark:hover:bg-surface-dark">
      <label className="flex flex-1 items-center gap-4 cursor-pointer">
        <input
          type="checkbox"
          checked={item.checked}
          onChange={onToggle}
          className="h-6 w-6 rounded border-slate-300 dark:border-border-dark bg-transparent text-primary focus:ring-primary focus:ring-offset-0"
        />
        <p
          className={`text-base font-medium ${
            item.checked ? 'line-through opacity-50' : ''
          }`}
        >
          {item.name}
        </p>
      </label>
      <Icon name="drag_indicator" className="text-slate-400 cursor-grab" />
    </div>
  );
};

interface ShoppingSectionProps {
  readonly title: string;
  readonly items: ShoppingListItemType[];
  readonly onToggleItem: (itemId: number) => void;
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
            item={item}
            onToggle={() => onToggleItem(item.id)}
          />
        ))}
      </div>
    </section>
  );
};

interface ShoppingListScreenProps {
  readonly className?: string;
  readonly listId?: number;
}

export const ShoppingListScreen: React.FC<ShoppingListScreenProps> = ({
  className = '',
  listId = 1,
}) => {
  const [activeTab, setActiveTab] = useState('My List');
  const { data: shoppingList, isLoading } = useShoppingList(listId);
  const { data: sectionsData } = useStoreSections();
  const updateItem = useUpdateShoppingListItem();

  // Group items by section
  const sections = useMemo(() => {
    if (!shoppingList?.items || !sectionsData?.data) {
      return [];
    }

    const sectionMap = new Map<number, string>();
    sectionsData.data.forEach((section) => {
      sectionMap.set(section.id, section.name);
    });

    const grouped = new Map<string, ShoppingListItemType[]>();
    shoppingList.items.forEach((item) => {
      const sectionName = item.section_id
        ? sectionMap.get(item.section_id) || 'Other'
        : 'Other';
      const items = grouped.get(sectionName) || [];
      items.push(item);
      grouped.set(sectionName, items);
    });

    return Array.from(grouped.entries()).map(([title, items]) => ({
      title,
      items,
    }));
  }, [shoppingList?.items, sectionsData?.data]);

  const handleToggleItem = (itemId: number) => {
    const item = shoppingList?.items.find((i) => i.id === itemId);
    if (item) {
      updateItem.mutate({
        listId,
        itemId,
        data: { checked: !item.checked },
      });
    }
  };

  if (isLoading) {
    return (
      <div className={`flex h-screen items-center justify-center ${className}`}>
        <p className="text-slate-400">Loading...</p>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="flex h-screen w-full flex-col overflow-hidden bg-background-dark">
        {/* Mobile Container */}
        <div className="mx-auto flex h-full w-full max-w-[480px] flex-col border-x border-border-dark bg-surface-dark shadow-2xl">
          {/* Header */}
          <header className="flex flex-col border-b border-border-dark pt-4 bg-surface-dark sticky top-0 z-10">
            <div className="flex items-center justify-between px-6 pb-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                  <Icon name="shopping_basket" />
                </div>
                <h1 className="text-xl font-bold tracking-tight">
                  {shoppingList?.name || 'Shopping List'}
                </h1>
              </div>
              <div className="flex gap-2">
                <Button variant="ghost" icon="search" />
                <Button variant="ghost" icon="more_vert" />
              </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-4 px-6">
              {['My List', 'Shared', 'History'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`border-b-2 py-3 text-sm font-bold transition-colors ${
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
            {sections.map((section, index) => (
              <ShoppingSection
                key={index}
                title={section.title}
                items={section.items}
                onToggleItem={handleToggleItem}
              />
            ))}
          </main>

          {/* Floating Action Button */}
          <div className="absolute bottom-20 left-0 right-0 p-6 bg-gradient-to-t from-background-dark via-background-dark/90 to-transparent pointer-events-none">
            <Button
              size="large"
              className="pointer-events-auto w-full shadow-xl"
            >
              <Icon name="add" className="mr-2" />
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
    </div>
  );
};

export default ShoppingListScreen;
