"use client";

import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { useAppFeature } from "@/hooks/use-app-features";

export function NavMain() {
  const { currentFeature, currentMenu } = useAppFeature();

  return (
    <SidebarGroup className="">
      <SidebarGroupLabel>{currentFeature.name}</SidebarGroupLabel>
      <SidebarMenu>
        {currentFeature.menus.map((menu) => (
          <SidebarMenuItem key={menu.name}>
            <SidebarMenuButton asChild isActive={currentMenu?.id === menu.id}>
              <a href={menu.url}>
                <menu.icon />
                <span>{menu.name}</span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
    </SidebarGroup>
  );
}
