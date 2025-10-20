import { useContext } from "react";
import {
  AppFeatureContextType,
  AppFeatureContext,
} from "@/providers/app-features-provider";

export const useAppFeature = (): AppFeatureContextType => {
  const ctx = useContext(AppFeatureContext);
  if (!ctx)
    throw new Error("useAppFeature must be used within AppFeatureProvider");
  return ctx;
};
