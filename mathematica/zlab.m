(* ::Package:: *)

SpectrumColors[x_, UVcut_:400, IRcut_:650]:=(
    If[x<=UVcut,
        Purple,
        If[x<=IRcut,
            ColorData["VisibleSpectrum"][x],
            Magenta]])

SpectrumColorsO[x_,opR_,UVcut_:400, IRcut_:650]:=(
    If[opR>1,
        op=1,
        op=opR];
    If[x<=UVcut,
        Darker[Purple,1-op],
        If[x<=IRcut,
            Darker[ColorData["VisibleSpectrum"][x],1-op],
            Darker[Magenta,1-op]]])

pointTemplate=StringTemplate["`energy` eV (`wave` nm)"];

SpectrumPlot[Swaves0_,SPL0_,std0_, baseline0_:{}, plotLabel0_:""]:=
    Module[{Swaves = Swaves0, SPL = SPL0, std = std0, baseline = baseline0,
    plotLabel = plotLabel0,
    maxSPL, plusSTD, minusSTD, plotPL, minWave, maxWave, cWave, peakA,
    sFun, peakNotes, peaks, p1, p2, prange},
    (
    maxSPL = Max[SPL];
    plusSTD = Transpose[{Swaves,SPL+std}];
    minusSTD = Transpose[{Swaves,SPL-std}];
    plotPL = Transpose[{Swaves,Abs[SPL]}];
    minWave = Swaves[[1]];
    maxWave = Swaves[[-1]];
    cWave = (maxWave+minWave)/2;
    peakA = Association[];
    sFun = Interpolation[Transpose[{Swaves,SPL}]];
    Manipulate[(
        If[KeyExistsQ[peakA,peak\[Sigma]],
            peakNotes = peakA[peak\[Sigma]],
            (
                peaks = FindPeaks[Last /@ plotPL, peak\[Sigma]];
                peaks = (plotPL[[Round[#[[1]]]]])& /@ peaks;
                peakNotes = Flatten[{{Red,Tooltip[Point[#], ToString[Round[10^7/#[[1]]]]<>"cm^-1"]},
                                    {Black,
                                        Text[pointTemplate[<|"energy"->Round[1240/#[[1]],0.001],
                                                            "wave"->Round[#[[1]],0.1]|>],#,
                                                            {-1.1,0},
                                                            {0,1}]}} & /@ peaks];
                peakA[peak\[Sigma]] = peakNotes;
            )
        ];
        prange = {centerWave-viewSpan/2, centerWave+viewSpan/2};
        If[prange[[1]] < minWave,
            prange[[1]] = minWave];
        If[prange[[2]] > maxWave,
            prange[[2]] = maxWave];
        If[baseline == {},
            things = {minusSTD, plusSTD, plotPL},
            things = {minusSTD, plusSTD, plotPL, baseline}];
        If[baseline == {},
            styles = {Transparent, Transparent, Blue},
            styles = {Transparent, Transparent, Blue, Red}];
        things = MovingAverage[#, movAvgBins] & /@ things;
        p1 = ListPlot[things,
            PlotRange->{prange, {0, 1/contrast*maxSPL*1.75}},
            ImageSize->1200,
            AspectRatio->1/5,
            Frame->True,
            FrameLabel->{"\[Lambda]/nm", None},
            PlotLabel->"",
            FrameStyle->Directive[16,Thick],
            Filling->{1->{2}},
            FrameTicks->{{None,None},{All,None}},
            FillingStyle->Directive[Red, Opacity[0.4]],
            PlotStyle->styles,
            Joined->True,
            Epilog->peakNotes
            ];
        p2 = Plot[1,{x,minWave,maxWave},
            ColorFunction->Function[{x,y}, SpectrumColorsO[x,sFun[x]*contrast/maxSPL]],
            ImageSize->1200,
            AspectRatio->1/10,
            Filling->Axis,
            ColorFunctionScaling->False,
            FrameTicks->{{None,None}, {None,None}},
            PlotRange->{prange,{0,1}},
            PlotPoints->1000,
            Frame->True,
            FrameTicks->{Automatic, None},
            Epilog -> Text[
                            Style[plotLabel, 
                                White,
                                Background -> Black], 
                                {prange[[2]], 1}, {1, 1}]
            ];
        Column[{p2,p1}]
    ),
    Row[{
        Column[{
            Control[{{contrast,1}, 1, 100, 0.1}],
            Control[{{peak\[Sigma],5}, 0.1, 10}]
            }
        ],
        Column[{
            Control[{{centerWave,cWave}, minWave, maxWave}],
            Control[{{viewSpan,(maxWave-minWave)}, 0, maxWave-minWave}]
            }
        ],
        Column[{
            Control[{{movAvgBins,1}, 1, 20, 1}]
            }
        ]
        }
    ],
    TrackedSymbols:> {contrast, peak\[Sigma], centerWave, viewSpan, movAvgBins}
    ]
)
        ]
