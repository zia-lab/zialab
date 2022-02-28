function [N_BFP,N_angles,Nr,numBins,clims,aperSize,stopDist,objSize,rotationAngles,offsets] = ...
    initializeTraceParameters(defocus,sourceRadii,N_sources,octMaskOption)

% ALL LENGTHS ARE IN LENS UNITS--whatever units you're using in Zemax.
% These will usually be mm.

moveBertrandLens(defocus);

N_BFP = 400;        % Grid Size for the caluclated radiation pattern (~200 is good)
N_angles = 6;       % Number of points on the ring with the smallest r (~6-8 is good)
Nr = 100;            % Number of radius values on pupil to sample (~90 is good)
numBins = 100;      % binnedIntensityMap has numBins X numBins bins (~100 is good)
clims = 0;          % colormap values for imagesc (clims=0 will scale automatically)

aper = zGetSystemAper;
aperSize = aper(3);                   % Aperture semi-diemeter [lens units]
stopSurface = aper(2);
objSize = zGetSurfaceData(0,5);       % Semi-diameter of object [lens units]

stopDist = 0;                         % Distance from object to stop surface [lens units]
for i = 0:stopSurface-1
    stopDist = stopDist + zGetSurfaceData(i,3);
end

% No rotational symmetry for the octagon, so just do 4 points per source
% radius
if octMaskOption == 1  &&  N_sources >= 3
    N_sources = 4;
    warning('only 4 sources per radius traced when using octmask')
end
rotationAngles = transpose(linspace(0,2*pi,N_sources+1));

% Source locations on the object surface
offsets = zeros(N_sources,2,length(sourceRadii));
for i = 1:length(sourceRadii)
    offsets(:,:,i) = sourceRadii(i)*[cos(rotationAngles(1:end-1)), sin(rotationAngles(1:end-1))];
end

end
%__________________________________________________________________________
function moveBertrandLens(displacement)

% x = 179.2;
x = 217.3;
zSetSurfaceData(24,3,x + displacement);
% zSetSurfaceData(44,3,47.172 - displacement);
zPushLens(5);

end