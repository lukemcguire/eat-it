import React, { useState, useMemo } from "react";
import {
  useShoppingList,
  useUpdateShoppingListItem,
  useStoreSections,
} from "@/hooks";
import { bottomNavItems } from "@/data/mockData";
import { Button, Checkbox, Tabs, TabsList, TabsTrigger } from "@/components/shadcn";
import { cn } from "@/lib/utils";
import type { ShoppingListItem as ShoppingListItemType } from "@/types/shopping";

interface ShoppingItemRowProps {
  readonly item: ShoppingListItemType;
  readonly onToggle: () => void;
}

const ShoppingItemRow: React.FC<ShoppingItemRowProps> = ({
  item,
  onToggle,
}) => {
  return (
    <div className="flex items-center gap-4 px-6 py-4 transition-colors hover:bg-muted/50">
      <div className="flex flex-1 items-center gap-4">
        <Checkbox
          checked={item.checked}
          onCheckedChange={onToggle}
          className="h-6 w-6"
        />
        <p
          className={cn(
            "text-base font-medium transition-all",
            item.checked && "line-through opacity-50"
          )}
        >
          {item.name}
        </p>
      </div>
      <span className="material-symbols-outlined text-muted-foreground cursor-grab">
        drag_indicator
      </span>
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
      <div className="flex items-center justify-between px-6 py-2 bg-muted/50">
        <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
          {title}
        </h3>
        <span className="text-xs font-medium text-muted-foreground">
          {items.length} item{items.length !== 1 ? 's' : ''}
        </span>
      </div>
      <div className="divide-y divide-border">
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
  className,
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
      <div className={cn("flex h-screen items-center justify-center", className)}>
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "relative flex h-screen w-full flex-col overflow-hidden bg-background",
        className
      )}
    >
      {/* Mobile Container */}
      <div className="mx-auto flex h-full w-full max-w-[480px] flex-col border-x border-border bg-background shadow-2xl">
        {/* Header */}
        <header className="flex flex-col border-b border-border pt-4 bg-background sticky top-0 z-10">
          <div className="flex items-center justify-between px-6 pb-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <span className="material-symbols-outlined">shopping_basket</span>
              </div>
              <h1 className="text-xl font-bold tracking-tight">
                {shoppingList?.name || 'Shopping List'}
              </h1>
            </div>
            <div className="flex gap-2">
              <Button variant="ghost" size="icon">
                <span className="material-symbols-outlined text-xl">search</span>
              </Button>
              <Button variant="ghost" size="icon">
                <span className="material-symbols-outlined text-xl">more_vert</span>
              </Button>
            </div>
          </div>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="px-6">
              {['My List', 'Shared', 'History'].map((tab) => (
                <TabsTrigger key={tab} value={tab}>
                  {tab}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
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
        <div className="absolute bottom-20 left-0 right-0 p-6 bg-gradient-to-t from-background via-background/90 to-transparent pointer-events-none">
          <Button className="pointer-events-auto w-full shadow-xl" size="lg">
            <span className="material-symbols-outlined">add</span>
            Add Item
          </Button>
        </div>

        {/* Bottom Navigation */}
        <nav className="flex items-center justify-around border-t border-border bg-muted/80 backdrop-blur-md px-4 py-3 pb-8">
          {bottomNavItems.map((item, index) => (
            <button
              key={item.label}
              className={cn(
                "flex flex-col items-center gap-1 transition-colors",
                index === 0 ? "text-primary" : "text-muted-foreground hover:text-primary"
              )}
            >
              <span className="material-symbols-outlined">{item.icon}</span>
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
