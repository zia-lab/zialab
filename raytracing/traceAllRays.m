function [ux,uy,x,y] = traceAllRays(sourceRadii,rotationAngles,N_angles,Nr,aperSize,objSize,stopDist,offsets,octMaskOption)

% Function to trace the rays from all of the sources defined in
% 'initializeTraceParameters'.
%
% INPUTS:
%     -sourceRadii: the radius values on the object surface where you'd like
%         to place the emitters
%     -rotationAngles: array of angles by which you rotate each source.
%     -N_angles: NOT the length of rotationAngles--this has to do with the
%         rays defined on the pupil. N_angles is the number of pupil points
%         at the first nonzero radius value. This value gets scaled by the
%         radius on the pupil as the radius increases.
%     -Nr: number of radius values to sample on the pupil.
%     -aperSize: aperture semi-diemeter [lens units]
%     -objSize: semi-diameter of the object surface [lens units]
%     -stopDist: distance from object to stop surface [lens units]
%     -offsets: N_sources x 2 x length(sourceRadii) array that defines the
%         coordinates of all of the sources.
%     -octMaskOption: 0 does nothing, 1 puts an octagonal mask in k space.
%         Note that only 4 sources per radius will be traced for the octMask
%
% OUTPUT:
%     -ux,uy: coordinates in normalized k space
%     -x,y: coordinates on the image surface

N_sources = length(rotationAngles) - 1;     % don't include redundant 2pi

UXcell = cell(1,length(sourceRadii));
UYcell = cell(1,length(sourceRadii));
Xcell = cell(1,length(sourceRadii));
Ycell = cell(1,length(sourceRadii));

% Throw a ring of rays for each source radius
for i = 1:length(sourceRadii)
    [px,py,~,~,hx,hy] = generateRayTraceInputs(N_angles,Nr,aperSize,stopDist,objSize,offsets(1,:,i),octMaskOption);
    
    % Throw rays and delete vignetted ones
    [x,y,vignetted,imageCenter] = shootRays(px,py,hx,hy);
    x  = x(~vignetted);
    y  = y(~vignetted);
    px = px(~vignetted);
    py = py(~vignetted);
    imageCenter

    % Each column has coodinates for each source on the ring
    [PX,PY] = generateRotatedCoordinates(px,py,N_sources,rotationAngles,[0,0]);
    [UX,UY] = pupil2u_matrix(PX,PY,aperSize,stopDist,offsets);    
    [XX,YY] = generateRotatedCoordinates(x,y,N_sources,rotationAngles,imageCenter);
    
    % The number of rays thrown changes with the source radius, so I store
    % each matrix in a cell.
    UXcell{i} = UX;
    UYcell{i} = UY;
    Xcell{i}  = XX;
    Ycell{i}  = YY;
end

ux = [];
uy = [];
x  = [];
y  = [];
for i = 1:length(sourceRadii)
    ux = [ux; UXcell{i}(:)];
    uy = [uy; UYcell{i}(:)];
    x  = [x; Xcell{i}(:)];
    y  = [y; Ycell{i}(:)];   
end

end
%__________________________________________________________________________
function [px,py,ux,uy,hx,hy] = generateRayTraceInputs(N_angles,Nr,aperSize,stopDist,objSize,offset,octMaskOption)

% Function to generate all of the inputs needed for the ray traces in Zemax. 
% INPUTS:
%     -N_angles: number of angles sampled at the first nonzero radius value on
%      the pupil
%     -Nr: number of radii sampled
%     -aperSize: semi-diameter of the aperture stop surface
%     -stopDist: distance from the object to the stop surface
%     -objSize: the semi-diameter of the object surface
%     -octMaskOption: 0 does nothing, 1 puts an octagonal mask in k space
% 
% OUTPUTS:
%     -px,py: normalized pupil corrdinates that determine where the rays hit
%      the stop surface
%     -ux,uy: normalized k vector components u = n*k/k0
%     -hx,hy: normalized object coordinates (determine the xy shift in the
%      object plane)


s = size(offset);
px = [];
py = [];
ux = [];
uy = [];
hx = [];
hy = [];

for i = 1:s(1)
    xOffset = offset(i,1);
    yOffset = offset(i,2);
    
    % Find image pupil that results from uniform angular emission
    [ppxx, ppyy] = generatePupilImage(N_angles, Nr, aperSize, stopDist, offset(i,:));
    px = [px; ppxx'];
    py = [py; ppyy'];
    
    % Convert determined pupil coordinates to u coordinates for later use
    [uuxx, uuyy] = pupil2u(ppxx,ppyy,aperSize,stopDist,xOffset,yOffset);
    ux = [ux; uuxx'];
    uy = [uy; uuyy'];
    
    % Store the shifts for later use
    hx = [hx; ones(length(ppxx),1)*xOffset/objSize];
    hy = [hy; ones(length(ppyy),1)*yOffset/objSize];
end

% Optional octagonal mask
if octMaskOption == 1
    idx = kSpace_octMask(51,0.5,ux,uy);
    ux = ux(idx);
    uy = uy(idx);
    px = px(idx);
    py = py(idx);
    hx = hx(idx);
    hy = hy(idx);
end

end
%__________________________________________________________________________
function  idx = kSpace_octMask(gridSize,normalizedRadius,ux,uy)

% Function to put an octagonal mask over the k space radiation pattern
% INPUTS:
%     -gridSize: number of points inside the octagon (must be multiple of 3)
%     -normalizedRadius: the "radius" of the octagon in k space, as a fraction
%      of 1.5
%     -ux,uy: normalized k vector values u = n*k/k0
% 
% OUTPUT:
%     -idx: indicies for ux,uy at which the points fall inside the mask

Noct = gridSize;
uRadius = normalizedRadius;

% Make an octagon
oct = strel('octagon',Noct);
oct = oct.getnhood;

% Put that octagon in the center of a bigger array
octAxis = linspace(-1.5*uRadius,1.5*uRadius,length(oct));
newsize = round(1/uRadius*length(octAxis));
n = round(0.5*(newsize - length(octAxis)));
mask = zeros(newsize,newsize);
mask(n:n+length(oct)-1, n:n+length(oct)-1) = oct;
uAxis = linspace(-1.5,1.5,length(mask));

% Get the mask in vector form (to match the actual (ux,uy) coordinates)
mask2 = interp2(uAxis,uAxis,mask,ux,uy);
idx = find(mask2==1);

end
%__________________________________________________________________________
function [px,py] = generatePupilImage(N_angles,N_radii,aperSize,stopDist,offset)

% Function to generate all the pupil positions in Zemax 
% INPUTS:
%     -N_angles: number of angles sampled at the first nonzero radius value on
%      the pupil
%     -N_radii: number of radii sampled
%     -aperSize: semi-diameter of the aperture stop surface
%     -stopDist: distance from the object to the stop surface
%     -objSize: the semi-diameter of the object surface
% 
% OUTPUTS:
%     -px,py: normalized pupil corrdinates that determine where the rays hit
%      the stop surface


xOffset = offset(1);
yOffset = offset(2);

% Account for an off-axis emitter
alpha = sqrt(xOffset^2 + yOffset^2) + aperSize;

% Space radii values on pupil according to uniform angular emission 
thetaMax = atan(alpha/stopDist);
qr = stopDist*tan(linspace(0,thetaMax,N_radii));

% Do qr = 0 separately
qx = 0;
qy = 0;

% Then do the rest
for i = 2:length(qr)
    nTheta = round(N_angles*qr(i)/qr(2));
    angles = linspace(0, 2*pi, nTheta);
    qx = [qx, qr(i)*cos(angles)];
    qy = [qy, qr(i)*sin(angles)];
end

% Account for an off-axis emitter
px = (qx - xOffset)/aperSize;
py = (qy - yOffset)/aperSize;

% Cut values outside a unit circle (otherwise you'd miss the stop surface)
circleCut = px.^2 + py.^2 <= 1;
px = px(circleCut);
py = py(circleCut);

end
%__________________________________________________________________________
function [x,y,vignetted,imageCenter] = shootRays(px,py,hx,hy)

% Function that shoots a bunch of rays in Zemax.
% INPUTS
%     -px,py: normalized pupil corrdinates that determine where the rays hit
%      the stop surface
%     -hx,hy: normalized object coordinates (determine the xy shift in the
%      object plane)
% 
% OUTPUTS
%     -x,y: positions at which the rays land on the image surface


x = zeros(length(px),1);
y = zeros(length(px),1);
vignetted = zeros(length(px),1);

imageCenter = zeros(1,2);
rayTraceData = zGetTrace(1,0,-1,0,0,0,0);
imageCenter(1) = rayTraceData(3);        % These are real space coordinates, in
imageCenter(2) = rayTraceData(4);        % whatever units you're working with in Zemax.


for i = 1:length(px)
    rayTraceData = zGetTrace(1,0,-1,hx(i),hy(i),px(i),py(i));
    x(i) = rayTraceData(3);        % These are real space coordinates, in
    y(i) = rayTraceData(4);        % whatever units you're working with in Zemax.
    if rayTraceData(2) ~= 0
        vignetted(i) = 1;
    else
        vignetted(i) = 0;
    end
end

end
%__________________________________________________________________________
function [XX,YY] = generateRotatedCoordinates(x,y,N_sources,rotationAngles,center)

% Takes a set of (x,y) coordinates on the image plane and duplicates them at
% different angles. The results are 2 matricies--the columns of
% the matricies give the x and y coords for the points at each rotation
% angle
% 
% INPUTS:
%     -x,y: coordinates on the image plane from a single-point trace
%     -N_sources: the number of sources (each emitting from a different spot)
%     -rotationAngles: the angles that determine where the sources are
%  
% OUTPUTS:
%     -XX,YY: length(x) X N_sources matricies giving the all the xy coords

XX = zeros(length(x),N_sources);
YY = zeros(length(x),N_sources);
XX(:,1) = x;
YY(:,1) = y;

T = [1,0,-center(1);0,1,-center(2);0,0,1];
Tinv = inv(T);

if isequal(center,[0,0])
    
    v = [x';y'];
    for i = 2:N_sources
        R = [cos(rotationAngles(i)) -sin(rotationAngles(i));...
            sin(rotationAngles(i)),cos(rotationAngles(i))];
        v2 = R*v;
        x2 = v2(1,:);
        y2 = v2(2,:);
        XX(:,i) = x2';
        YY(:,i) = y2';
    end
    
else
    
    v = [x';y';ones(1,length(x))];
    for i = 2:N_sources
        R = [cos(rotationAngles(i)),-sin(rotationAngles(i)),0;...
             sin(rotationAngles(i)),cos(rotationAngles(i)), 0;...
             0,0,1];
        v2 = Tinv*R*T*v;
        x2 = v2(1,:);
        y2 = v2(2,:);
        XX(:,i) = x2';
        YY(:,i) = y2';
    end
    
end
end
%__________________________________________________________________________
function [UX,UY] = pupil2u_matrix(PX,PY,aperSize,stopDist,offsets)

% Converts pupil coords to ux,uy coords

s = size(PX);

UX = zeros(s(1),s(2));
UY = zeros(s(1),s(2));

for i = 1:s(2)
    [uuxx, uuyy] = pupil2u(PX(:,i),PY(:,i),aperSize,stopDist,offsets(i,1),offsets(i,2));
    UX(:,i) = uuxx;
    UY(:,i) = uuyy;
end

end
%__________________________________________________________________________