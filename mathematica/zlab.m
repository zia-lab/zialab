(* ::Package:: *)


UVcut = 400;
IRcut = 700;

SpectrumColors[x_]:=(If[x<=UVcut,
Purple,
If[x<=IRcut,
ColorData["VisibleSpectrum"][x],
Magenta]])

SpectrumPlot[wavespectrumRaw_,plotLabelRaw_:""]:=(
minWave=Min[First/@wavespectrumRaw];
maxWave=Max[First/@wavespectrumRaw];
plotLabel=plotLabelRaw;
Manipulate[(
wavespectrum=wavespectrumRaw[[;;;;downSample]];
wavespectrum=MovingAverage[wavespectrum,smoothBins];
(*wavespectrum=Transpose[{(First/@wavespectrum)[[2;;;;]],Differences[Last/@wavespectrum]}];*)
If[logscale,wavespectrum={#[[1]],Log[#[[2]]]}&/@wavespectrum];
maxLight=Max[Last/@wavespectrum];
wavespectrum={#[[1]],#[[2]]/maxLight}&/@wavespectrum;
wavespectrum={#[[1]],#[[2]]*contrast}&/@wavespectrum;
wavespectrum={#[[1]],If[#[[2]]>=1,1,#[[2]]]}&/@wavespectrum;
d\[Lambda]=Abs[wavespectrum[[1,1]]-wavespectrum[[2,1]]];
h=3;
d=0.5;
pointTemplate=StringTemplate["`energy` eV (`wave` nm)"];
peaks=FindPeaks[Last/@wavespectrum,peak\[Sigma]];
peaks=(wavespectrum[[Round[#[[1]]]]])&/@peaks;
peaks={#[[1]],#[[2]]*h+h+d}&/@peaks;
peakNotes=Flatten[{{Red,Point[#]},{Black,Text[pointTemplate[<|"energy"->Round[1240/#[[1]],0.001],"wave"->Round[#[[1]],0.1]|>],#,{-1.1,0},{1,2}]}}&/@peaks];
notices={};
If[minWave<UVcut,
notices=Append[notices,{Dashed,Purple,Line[{{UVcut,0},{UVcut,h}}]}]];
If[maxWave>IRcut,
notices=Append[notices,{Dashed,Red,Line[{{IRcut,0},{IRcut,h}}]}]];
graph = Labeled[
Framed[
Graphics[{peakNotes,
{Darker[If[monochrome,White,SpectrumColors[#[[1]]]],Abs[1-#[[2]]]],Rectangle[{#[[1]],0},{#[[1]]+d\[Lambda],h}]}&/@wavespectrum,
notices,
AxisObject[{"Horizontal",h+d},TickDirection->Down,TicksStyle->Black],AxisObject[{"Horizontal",-d},TickDirection->Up,TicksStyle->Black,AxisLabel->Placed["\[Lambda]/nm",Center]],
Line[{#[[1]],#[[2]]*h+h+d}&/@wavespectrum]},
ImageSize-> ((WindowSize/.AbsoluteOptions[EvaluationNotebook[]])[[1]]-200),
AspectRatio->1/5,
PlotRange->{{\[Lambda]range[[1]]-0.75,\[Lambda]range[[2]]+0.75},All}]
,FrameMargins->10
,RoundingRadius->5]
,label,Top];
Column[{graph,
Button["Save",
 Export[SystemDialogInput["FileSave"],Framed[graph,FrameStyle->Transparent,FrameMargins->20]],Method->"Queued"]}]
),
Row[{
Spacer[10],
Column[{Control[{{\[Lambda]range,{minWave,maxWave}},minWave,maxWave,ControlType->IntervalSlider}],
Control[{{downSample,2},1,10,1}]}],
Spacer[10],
Column[{Control[{{contrast,1},1,10,0.1}],
Control[{{logscale,False},{True,False}}]}],
Spacer[10],
Column[{Control[{{smoothBins,2},1,10,1}],
Control[{{peak\[Sigma],2.5},0.1,10}]}],
Spacer[10],
Column[{
Control[{{label,plotLabel},ControlType->InputField}],
Control[{{monochrome,False},{True,False}}]
}]
}],
TrackedSymbols:>True]);

