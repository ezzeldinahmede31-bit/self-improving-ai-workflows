import React from 'react';
import { Composition, AbsoluteFill, Sequence } from 'remotion';
import { Scene1 } from './scenes/Scene1';
import { Scene2 } from './scenes/Scene2';
import { Scene3 } from './scenes/Scene3';
import { Scene4 } from './scenes/Scene4';
import { Scene5 } from './scenes/Scene5';
import { Scene6 } from './scenes/Scene6';
import { WIDTH, HEIGHT, FPS, DURATION_IN_SECONDS } from './constants';

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="AIAutomationMotion"
        component={MainVideo}
        durationInFrames={DURATION_IN_SECONDS * FPS}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    </>
  );
};

const MainVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: '#050505' }}>
      <Sequence from={0} durationInFrames={5 * FPS}>
        <Scene1 />
      </Sequence>
      <Sequence from={5 * FPS} durationInFrames={5 * FPS}>
        <Scene2 />
      </Sequence>
      <Sequence from={10 * FPS} durationInFrames={5 * FPS}>
        <Scene3 />
      </Sequence>
      <Sequence from={15 * FPS} durationInFrames={7 * FPS}>
        <Scene4 />
      </Sequence>
      <Sequence from={22 * FPS} durationInFrames={7 * FPS}>
        <Scene5 />
      </Sequence>
      <Sequence from={29 * FPS} durationInFrames={7 * FPS}>
        <Scene6 />
      </Sequence>
    </AbsoluteFill>
  );
};
