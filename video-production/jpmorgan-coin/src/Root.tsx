import React from "react";
import { Composition } from "remotion";
import { COINFilm } from "./COINFilm";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="COINFilm"
    component={COINFilm}
    durationInFrames={900}
    fps={30}
    width={1920}
    height={1080}
  />
);