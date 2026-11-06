import {Config} from '@remotion/cli/config';

// No WebGL on this box — SwiftShader only, and 2 render concurrency max.
Config.setChromiumOpenGlRenderer('swiftshader');
Config.setConcurrency(2);
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(92);
Config.setCodec('h264');
Config.setCrf(18);
Config.setBrowserExecutable(process.env.REMOTION_BROWSER ?? '');
Config.setChromiumDisableWebSecurity(false);
