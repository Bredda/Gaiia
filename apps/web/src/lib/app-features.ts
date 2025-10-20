import {
  BotMessageSquare,
  History,
  Home,
  LucideIcon,
  Play,
  Settings,
  Telescope,
} from "lucide-react";

export interface AppFeature {
  id: string;
  name: string;
  tagline: string;
  icon: LucideIcon;
  url: string;
  menus: AppFeatureMenu[];
}

export interface AppFeatureMenu {
  id: string;
  name: string;
  icon: LucideIcon;
  url: string;
}

export const RootApp: AppFeature = {
  id: "root",
  name: "Gaiia",
  tagline: "Your AI Assistant",
  icon: Home,
  url: "/",
  menus: [
    {
      id: "home",
      name: "Home",
      icon: Home,
      url: "/",
    },
  ],
};

export const APP_FEATURES: AppFeature[] = [
  RootApp,
  {
    id: "ai-got-beef",
    name: "AI Got Beef",
    tagline: "AI-powered beef management",
    icon: BotMessageSquare,
    url: "/ai-got-beef",
    menus: [
      {
        id: "ai-got-beef-home",
        name: "Home",
        icon: Home,
        url: "/ai-got-beef",
      },
      {
        id: "ai-got-beef-run",
        name: "Run",
        icon: Play,
        url: "/ai-got-beef/run",
      },
    ],
  },
  {
    id: "verifai",
    name: "VerfiAI",
    tagline: "AI-powered image and video analysis",
    icon: Telescope,
    url: "/verifai",
    menus: [
      {
        id: "clarifai_home",
        name: "Home",
        icon: Home,
        url: "/verifai",
      },
      {
        id: "clarifai_history",
        name: "History",
        icon: History,
        url: "/verifai/history",
      },
      {
        id: "clarifai_settings",
        name: "Settings",
        icon: Settings,
        url: "/verifai/settings",
      },
    ],
  },
];
