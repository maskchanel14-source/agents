import React from "react";
import {Composition} from "remotion";
const T: React.FC<{t: string}> = ({t}) => (
  <div style={{width:"100%",height:"100%",background:"#101014",color:"#fff",fontFamily:"sans-serif",fontSize:120,display:"flex",alignItems:"center",justifyContent:"center"}}>{t}</div>
);
export const Root: React.FC = () => (
  <>
    <Composition id="T" component={T} durationInFrames={60} fps={30} width={1080} height={1920} defaultProps={{t:"OK"}} />
  </>
);
