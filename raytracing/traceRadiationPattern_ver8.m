function traceRadiationPattern_ver8(defocus,sourceRadii,N_sources,plotLimit,plotCode,octMaskOption)
% MUST HAVE AN OPEN DDE CHANNEL TO ZEMAX BEFORE RUNNING!!! (use zDDEInit)
% Aperture in Zemax should be set to 'Float by Stop Size'!!


% This function starts with a radiation pattern generated by the parameters
% in 'bfpTestScript'. It then defines a set of rays that would be produced by
% point sources on the object surface emitting uniformily in angles. The
% locations of the point sources on the object surface are determined by
% sourceRadii and N_sources (you will have N_sources points at each
% sourceRadii value.

% After defining the rays, the function assigns an intensity value to each
% ray and traces the rays in Zemax. It then bins the rays at the image
% surface, and adds up the intensities in each bin to generate a final image.

% INPUTS:
%    -defocus: displacement of the bertrand lens. you'll have to set the
%        parameters in 'moveBertrandLens' to make sure you're defocusing at
%        the correct spot.
%    -sourceRadii: the radius values on the object surface where you'd like
%        to place the emitters
%    -N_sources: number of sources at each sourceRadii value
%    -plotLimit: sets the bound for the final plot. The xlim and ylim will
%        be -plotLimit to plotLimit. If plotLimit = 0, then it will autoscale
%    -plotCode: 0 gives a radiation pattern, 1 gives a cross section, 2
%        gives both
%    -octMaskOption: 0 does nothing, 1 puts an octagonal mask in k space.
%        Note that only 4 sources per radius will be traced for the octMask
%
% OUTPUT:
%     a figure showing the traced radiation pattern on the image plane


%% STEP 1: Initialization
[N_BFP,N_angles,Nr,numBins,clims,aperSize,stopDist,objSize,rotationAngles,offsets] = ...
    initializeTraceParameters(defocus,sourceRadii,N_sources,octMaskOption);

%% STEP 2: Define and throw the rays. Associate a (ux,uy) value with each ray.
[ux,uy,x,y] = traceAllRays(sourceRadii,rotationAngles,N_angles,Nr,...
    aperSize,objSize,stopDist,offsets,octMaskOption);

%% STEP 3: Use the calculated radiation pattern values to associate intensities with each (ux,uy)
Ivals = matchIntensities(N_BFP,ux,uy,octMaskOption);
uyMax = max(uy);
uyMin = min(uy);
clear ux uy

%% STEP 4: Bin the (x,y) points and add intensities within each bin.
heat = binnedIntensityMap(x, y, Ivals, numBins);

%% STEP 5: Process the image
[finalImage,axis] = processBinnedImage(x,y,heat,octMaskOption);

%% STEP 6: Plot
if plotLimit == 0
    plotLimit = max(abs([x;y]));
end
plotBFPImage(axis,finalImage,plotLimit,defocus,sourceRadii,[uyMin,uyMax],clims,plotCode);

end