"use client";

import { usePathname } from "next/navigation";
import { createContext, useMemo } from "react";
import { AppFeature, AppFeatureMenu, APP_FEATURES } from "@/lib/app-features";

export interface AppFeatureContextType {
  currentFeature: AppFeature;
  currentMenu: AppFeatureMenu;
  apps: AppFeature[];
}

export const AppFeatureContext = createContext<
  AppFeatureContextType | undefined
>(undefined);

export const AppFeatureProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const pathname = usePathname();

  const value = useMemo(() => {
    const currentFeature =
      APP_FEATURES.find(
        (app) => pathname === app.url || pathname.startsWith(`${app.url}/`)
      ) ?? APP_FEATURES[0];
    const currentMenu =
      currentFeature.menus.find(
        (menu) => pathname === menu.url || pathname.startsWith(`${menu.url}/`)
      ) ?? currentFeature.menus[0];

    return {
      currentFeature,
      currentMenu,
      apps: APP_FEATURES,
    };
  }, [pathname]);

  return (
    <AppFeatureContext.Provider value={value}>
      {children}
    </AppFeatureContext.Provider>
  );
};
