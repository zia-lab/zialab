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

SpectrumPlotManipulate[Swaves0_, SPL0_, std0_, baseline0_:{}, plotLabel0_:"", avgBins0_:1, startSigma0_:5, bottomY0_:0]:=
    Module[{Swaves = Swaves0, SPL = SPL0, std = std0, baseline = baseline0,
    plotLabel = plotLabel0,
    avgBins = avgBins0,
    startSigma = startSigma0,
    bottomY = bottomY0,
    maxSPL, plusSTD, minusSTD, plotPL, minWave, maxWave, cWave, peakA,
    sFun, peakNotes, peaks, p1, p2, prange, plotPLR, plusSTDR, minusSTDR,
    movingAverages, plotstd, movingWaves, stdR},
    (
    maxSPL = Max[SPL];
    stdR = std;
    plusSTDR = Transpose[{Swaves,SPL+std}];
    minusSTDR = Transpose[{Swaves,SPL-std}];
    plotPLR = Transpose[{Swaves,SPL}];
    minWave = Swaves[[1]];
    maxWave = Swaves[[-1]];
    cWave = (maxWave+minWave)/2;
    peakA = Association[];
    movingAverages = Association[];
    Manipulate[(
        If[KeyExistsQ[movingAverages, movAvgBins],
            (plotPL  = movingAverages[movAvgBins]["plotPL"];
            minusSTD = movingAverages[movAvgBins]["minusSTD"];
            plusSTD  = movingAverages[movAvgBins]["plusSTD"];
            sFun     = movingAverages[movAvgBins]["sFun"];),
            (plotPL  = MovingAverage[plotPLR, movAvgBins];
            movingWaves = First /@ plotPL;
            plotstd = Sqrt[MovingAverage[stdR^2, movAvgBins]]/Sqrt[movAvgBins]; 
            minusSTD = Transpose[{movingWaves, (Last /@ plotPL) - plotstd}];
            plusSTD = Transpose[{movingWaves, (Last /@ plotPL) + plotstd}];
            sFun = Interpolation[plotPL];
            movingAverages[movAvgBins] = Association[{"plotPL"-> plotPL,
                                        "minusSTD"-> minusSTD,
                                        "plusSTD"-> plusSTD,
                                        "sFun"-> sFun}];
            )
        ];

        minWave = plotPL[[1,1]];
        maxWave = plotPL[[-1,1]];
        If[KeyExistsQ[peakA, {peak\[Sigma], movAvgBins}],
            peakNotes = peakA[ {peak\[Sigma], movAvgBins}],
            (
                peaks = FindPeaks[Last /@ plotPL, peak\[Sigma]];
                peaks = (plotPL[[Round[#[[1]]]]])& /@ peaks;
                peakNotes = Flatten[{{Red,Tooltip[Point[#], ToString[Round[10^7/#[[1]]]]<>"cm^-1"]},
                                    {Black,
                                        Text[pointTemplate[<|"energy"->Round[1240/#[[1]],0.001],
                                                            "wave"->Round[#[[1]],0.1]|>],#,
                                                            {-1.1,0},
                                                            {0,1}]}} & /@ peaks];
                peakA[{peak\[Sigma], movAvgBins}] = peakNotes;
            )
        ];
        prange = {centerWave-viewSpan/2, centerWave+viewSpan/2};
        If[prange[[1]] < minWave,
            prange[[1]] = minWave];
        If[prange[[2]] > maxWave,
            prange[[2]] = maxWave];
        If[baseline == {},
            things = {minusSTD, plusSTD, plotPL},
            things = {minusSTD, plusSTD, plotPL, MovingAverage[baseline,movAvgBins]}];
        If[baseline == {},
            styles = {Transparent, Transparent, Blue},
            styles = {Transparent, Transparent, Blue, Red}];

        p1 = ListPlot[things,
            PlotRange->{prange, {bottomY, 1/contrast*maxSPL*1.75}},
            ImageSize->1200,
            AspectRatio->1/5,
            Frame->True,
            FrameLabel->{"\[Lambda]/nm", None},
            PlotLabel->"",
            Axes->None,
            FrameStyle->Directive[16,Thick],
            Filling->{1->{2}},
            FrameTicks->{{None,None},{All,None}},
            FillingStyle->Directive[Red, Opacity[0.4]],
            PlotStyle->styles,
            Joined->True,
            Epilog->peakNotes,
            ImagePadding->{{20,20},{Automatic,0}}
            ];
        p2 = Plot[1,{x,minWave,maxWave},
            ColorFunction->Function[{x,y}, SpectrumColorsO[x, sFun[x]*contrast/maxSPL]],
            ImageSize->1200,
            ImagePadding->{{20,20},{0,0}},
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
            Control[{{contrast,1}, 1, 10, 0.1}],
            Control[{{peak\[Sigma], startSigma}, 0.1, 10}]
            }
        ],
        Column[{
            Control[{{centerWave,cWave}, minWave, maxWave}],
            Control[{{viewSpan,(maxWave-minWave)}, 0, maxWave-minWave}]
            }
        ],
        Column[{
            Control[{{movAvgBins, avgBins}, 1, 20, 1}]
            }
        ]
        }
    ],
    TrackedSymbols:> {contrast, peak\[Sigma], centerWave, viewSpan, movAvgBins}
    ]
)
        ]


SpectrumPlot[Swaves0_, SPL0_, std0_, baseline0_:{}, plotLabel0_:"", avgBins0_:1, startSigma0_:5, bottomY0_:0]:=
    Module[{Swaves = Swaves0, SPL = SPL0, std = std0, baseline = baseline0,
    plotLabel = plotLabel0,
    avgBins = avgBins0,
    startSigma = startSigma0,
    bottomY = bottomY0,
    maxSPL, plusSTD, minusSTD, plotPL, minWave, maxWave, cWave, peakA,
    sFun, peakNotes, peaks, p1, p2, prange, plotPLR, plusSTDR, minusSTDR,
    movingAverages, plotstd, movingWaves, stdR},
    (
    maxSPL = Max[SPL];
    stdR = std;
    plusSTDR = Transpose[{Swaves,SPL+std}];
    minusSTDR = Transpose[{Swaves,SPL-std}];
    plotPLR = Transpose[{Swaves,SPL}];
    minWave = Swaves[[1]];
    maxWave = Swaves[[-1]];
    cWave = (maxWave+minWave)/2;
    peakA = Association[];
    movingAverages = Association[];
    contrast = 1;
    peak\[Sigma] = startSigma;
    centerWave = cWave;
    viewSpan = (maxWave-minWave);
    movAvgBins = avgBins;
    (
        If[KeyExistsQ[movingAverages, movAvgBins],
            (plotPL  = movingAverages[movAvgBins]["plotPL"];
            minusSTD = movingAverages[movAvgBins]["minusSTD"];
            plusSTD  = movingAverages[movAvgBins]["plusSTD"];
            sFun     = movingAverages[movAvgBins]["sFun"];),
            (plotPL  = MovingAverage[plotPLR, movAvgBins];
            movingWaves = First /@ plotPL;
            plotstd = Sqrt[MovingAverage[stdR^2, movAvgBins]]/Sqrt[movAvgBins]; 
            minusSTD = Transpose[{movingWaves, (Last /@ plotPL) - plotstd}];
            plusSTD = Transpose[{movingWaves, (Last /@ plotPL) + plotstd}];
            sFun = Interpolation[plotPL];
            movingAverages[movAvgBins] = Association[{"plotPL"-> plotPL,
                                        "minusSTD"-> minusSTD,
                                        "plusSTD"-> plusSTD,
                                        "sFun"-> sFun}];
            )
        ];

        minWave = plotPL[[1,1]];
        maxWave = plotPL[[-1,1]];
        If[KeyExistsQ[peakA, {peak\[Sigma], movAvgBins}],
            peakNotes = peakA[ {peak\[Sigma], movAvgBins}],
            (
                peaks = FindPeaks[Last /@ plotPL, peak\[Sigma]];
                peaks = (plotPL[[Round[#[[1]]]]])& /@ peaks;
                peakNotes = Flatten[{{Red,Tooltip[Point[#], ToString[Round[10^7/#[[1]]]]<>"cm^-1"]},
                                    {Black,
                                        Text[pointTemplate[<|"energy"->Round[1240/#[[1]],0.001],
                                                            "wave"->Round[#[[1]],0.1]|>],#,
                                                            {-1.1,0},
                                                            {0,1}]}} & /@ peaks];
                peakA[{peak\[Sigma], movAvgBins}] = peakNotes;
            )
        ];
        prange = {centerWave-viewSpan/2, centerWave+viewSpan/2};
        If[prange[[1]] < minWave,
            prange[[1]] = minWave];
        If[prange[[2]] > maxWave,
            prange[[2]] = maxWave];
        If[baseline == {},
            things = {minusSTD, plusSTD, plotPL},
            things = {minusSTD, plusSTD, plotPL, MovingAverage[baseline,movAvgBins]}];
        If[baseline == {},
            styles = {Transparent, Transparent, Blue},
            styles = {Transparent, Transparent, Blue, Red}];

        p1 = ListPlot[things,
            PlotRange->{prange, {bottomY, 1/contrast*maxSPL*1.75}},
            ImageSize->1200,
            AspectRatio->1/5,
            Axes->None,
            Frame->True,
            FrameLabel->{"\[Lambda]/nm", None},
            PlotLabel->"",
            FrameStyle->Directive[16,Thick],
            Filling->{1->{2}},
            FrameTicks->{{None,None},{All,None}},
            FillingStyle->Directive[Red, Opacity[0.4]],
            PlotStyle->styles,
            Joined->True,
            Epilog->peakNotes,
            ImagePadding->{{20,20},{Automatic,0}}
            ];
        p2 = Plot[1,{x,minWave,maxWave},
            ColorFunction->Function[{x,y}, SpectrumColorsO[x, sFun[x]*contrast/maxSPL]],
            ImageSize->1200,
            ImagePadding->{{20,20},{0,20}},
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

        
    );
);
        Return[{p2,p1}]
]

SpectrumPlotAlt[Swaves0_, SPL0_, std0_, baseline0_:{}, plotLabel0_:"", avgBins0_:1, startSigma0_:5, bottomY0_:0, plotFun_:ListPlot, extraTop0_:1.75]:=
    Module[{Swaves = Swaves0, SPL = SPL0, std = std0, baseline = baseline0,
    plotLabel = plotLabel0,
    avgBins = avgBins0,
    startSigma = startSigma0,
    bottomY = bottomY0,
    extraTop = extraTop0,
    maxSPL, plusSTD, minusSTD, plotPL, minWave, maxWave, cWave, peakA,
    sFun, peakNotes, peaks, p1, p2, prange, plotPLR, plusSTDR, minusSTDR,
    movingAverages, plotstd, movingWaves, stdR},
    (
    maxSPL = Max[SPL];
    stdR = std;
    plusSTDR = Transpose[{Swaves,SPL+std}];
    minusSTDR = Transpose[{Swaves,SPL-std}];
    plotPLR = Transpose[{Swaves,SPL}];
    minWave = Swaves[[1]];
    maxWave = Swaves[[-1]];
    cWave = (maxWave+minWave)/2;
    peakA = Association[];
    movingAverages = Association[];
    contrast = 1;
    peak\[Sigma] = startSigma;
    centerWave = cWave;
    viewSpan = (maxWave-minWave);
    movAvgBins = avgBins;
    (
        If[KeyExistsQ[movingAverages, movAvgBins],
            (plotPL  = movingAverages[movAvgBins]["plotPL"];
            minusSTD = movingAverages[movAvgBins]["minusSTD"];
            plusSTD  = movingAverages[movAvgBins]["plusSTD"];
            sFun     = movingAverages[movAvgBins]["sFun"];),
            (plotPL  = MovingAverage[plotPLR, movAvgBins];
            movingWaves = First /@ plotPL;
            plotstd = Sqrt[MovingAverage[stdR^2, movAvgBins]]/Sqrt[movAvgBins];  
            minusSTD = Transpose[{movingWaves, (Last /@ plotPL) - plotstd}];
            plusSTD = Transpose[{movingWaves, (Last /@ plotPL) + plotstd}];
            sFun = Interpolation[plotPL];
            movingAverages[movAvgBins] = Association[{"plotPL"-> plotPL,
                                        "minusSTD"-> minusSTD,
                                        "plusSTD"-> plusSTD,
                                        "sFun"-> sFun}];
            )
        ];

        minWave = plotPL[[1,1]];
        maxWave = plotPL[[-1,1]];
        If[plotFun === ListLogPlot,
        scaleFun = Log,
        scaleFun = Identity
        ];
        If[KeyExistsQ[peakA, {peak\[Sigma], movAvgBins}],
            peakNotes = peakA[ {peak\[Sigma], movAvgBins}],
            (
                peaks = FindPeaks[Last /@ plotPL, peak\[Sigma]];
                peaks = (plotPL[[Round[#[[1]]]]])& /@ peaks;
                peakNotes = Flatten[{{Red,Tooltip[Point[{#[[1]],scaleFun[#[[2]]]}], ToString[Round[10^7/#[[1]]]]<>"cm^-1"]},
                                    {Black,
                                        Text[pointTemplate[<|"energy"->Round[1240/#[[1]],0.001],
                                                            "wave"->Round[#[[1]],0.1]|>],{#[[1]],scaleFun[#[[2]]]},
                                                            {-1.1,0},
                                                            {0,1}]}} & /@ peaks];
                peakA[{peak\[Sigma], movAvgBins}] = peakNotes;
            )
        ];
        prange = {centerWave-viewSpan/2, centerWave+viewSpan/2};
        If[prange[[1]] < minWave,
            prange[[1]] = minWave];
        If[prange[[2]] > maxWave,
            prange[[2]] = maxWave];
        If[baseline == {},
            things = {minusSTD, plusSTD, plotPL},
            things = {minusSTD, plusSTD, plotPL, MovingAverage[baseline,movAvgBins]}];
        If[baseline == {},
            styles = {Transparent, Transparent, Blue},
            styles = {Transparent, Transparent, Blue, Red}];

        p1 = plotFun[things,
            PlotRange->{prange, {bottomY, 1/contrast*maxSPL*extraTop}},
            ImageSize->1200,
            AspectRatio->1/5,
            Axes->None,
            Frame->True,
            FrameLabel->{"\[Lambda]/nm", None},
            PlotLabel->"",
            FrameStyle->Directive[16,Thick],
            Filling->{1->{2}},
            FrameTicks->{{Automatic,None},{All,None}},
            FrameTicksStyle -> {{Directive[FontOpacity -> 0, FontSize -> 0],     Automatic}, {Automatic, Automatic}},
            FillingStyle->Directive[Red, Opacity[0.4]],
            PlotStyle->styles,
            Joined->True,
            Epilog->peakNotes,
            ImagePadding->{{20,20},{Automatic,0}}
            ];
        maxSPL = scaleFun[maxSPL];
        p2 = Plot[1,{x,minWave,maxWave},
            ColorFunction->Function[{x,y}, SpectrumColorsO[x, scaleFun[sFun[x]]*contrast/maxSPL]],
            ImageSize->1200,
            ImagePadding->{{20,20},{0,20}},
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

        
    );
);
        Return[{p2,p1}]
]