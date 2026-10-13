import { createContext, useContext } from "react";
import type { Filters } from "./filters";
import type { TabId } from "./urlState";

/**
 * Cross-view navigation: any panel can send the reader to another view
 * with a filter patch applied (e.g. a coverage segment opens the
 * comparison table already filtered to that bucket).
 */
export interface Navigation {
  go: (tab: TabId, patch?: Partial<Filters>) => void;
}

export const NavContext = createContext<Navigation>({ go: () => {} });

export const useNav = () => useContext(NavContext);
