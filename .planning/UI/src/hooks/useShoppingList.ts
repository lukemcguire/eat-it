import { useState, useCallback } from 'react';
import {
  shoppingListSections,
  type ShoppingSection,
  type ShoppingItem,
} from '../data/mockData';

export interface UseShoppingListReturn {
  readonly sections: readonly ShoppingSection[];
  readonly toggleItem: (sectionId: string, itemId: string) => void;
  readonly activeTab: string;
  readonly setActiveTab: (tab: string) => void;
}

export function useShoppingList(): UseShoppingListReturn {
  const [sections, setSections] = useState<readonly ShoppingSection[]>(
    shoppingListSections
  );
  const [activeTab, setActiveTab] = useState('My List');

  const toggleItem = useCallback(
    (sectionId: string, itemId: string) => {
      setSections((prevSections) =>
        prevSections.map((section) =>
          section.id === sectionId
            ? {
                ...section,
                items: section.items.map((item) =>
                  item.id === itemId
                    ? { ...item, checked: !item.checked }
                    : item
                ),
              }
            : section
        )
      );
    },
    []
  );

  return {
    sections,
    toggleItem,
    activeTab,
    setActiveTab,
  } as const;
}
