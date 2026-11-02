export const FPS = 30;
export const DURATION = 1230;

export type CaptionCue = {
  start: number;
  end: number;
  text: string;
  emphasis?: string;
};

export const captions: CaptionCue[] = [
  {start: 0, end: 78, text: 'ONE MUSHROOM MAY MAKE PEOPLE SEE TINY HUMANS.', emphasis: 'TINY HUMANS'},
  {start: 78, end: 270, text: 'REPORTS DESCRIBE MINIATURE FIGURES MOVING AROUND REAL OBJECTS.', emphasis: 'REAL OBJECTS'},
  {start: 270, end: 420, text: 'DNA LINKS THE CHINESE AND PHILIPPINE MUSHROOMS TO ONE SPECIES.', emphasis: 'DNA LINKS'},
  {start: 420, end: 580, text: 'NO USUAL PSILOCYBIN OR IBOTENIC-ACID PATHWAYS.', emphasis: 'NO USUAL'},
  {start: 580, end: 700, text: 'THE ACTIVE CHEMICAL IS STILL UNKNOWN.', emphasis: 'UNKNOWN'},
  {start: 700, end: 828, text: 'A LEAD — NOT A NEW DRUG DISCOVERY.', emphasis: 'A LEAD'},
  {start: 828, end: 942, text: 'PAPUA NEW GUINEA REPORTS REMAIN UNVERIFIED.', emphasis: 'UNVERIFIED'},
  {start: 942, end: 1050, text: 'DO NOT TEST IT. WILD MUSHROOMS CAN POISON.', emphasis: 'DO NOT'},
  {start: 1050, end: 1155, text: 'TINY PEOPLE ARE THE HEADLINE.', emphasis: 'TINY PEOPLE'},
  {start: 1155, end: 1230, text: 'THE UNKNOWN MOLECULE IS THE MYSTERY.', emphasis: 'UNKNOWN MOLECULE'},
];

export const sceneForFrame = (frame: number) => {
  if (frame < 270) return 'visions';
  if (frame < 420) return 'dna';
  if (frame < 580) return 'reveal';
  if (frame < 828) return 'molecule';
  if (frame < 942) return 'evidence';
  if (frame < 1050) return 'warning';
  return 'outro';
};
