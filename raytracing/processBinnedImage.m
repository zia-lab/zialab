function [newImage,axis] = processBinnedImage(x,y,heat,octMaskOption)

xmin = min(x); xmax = max(x); ymin = min(y); ymax = max(y);
totalMax = max(abs([xmin,xmax,ymin,ymax]));

% Smooth the signal by averaging over every 5x5 pixel box
h = 1/25*ones(5);
heat2 = filter2(h,heat);
q2 = linspace(-totalMax,totalMax,length(heat));
[XX, YY] = meshgrid(q2,q2);

clear heat

% Interpolate over a finer grid
N3 = 500;
axis = linspace(-totalMax,totalMax,N3);
[Xq, Yq] = meshgrid(axis,axis);
heat3 = interp2(XX,YY,heat2,Xq,Yq);

% Don't mask the octagon
x0 = (xmin + xmax)/2;
y0 = (ymin + ymax)/2;
a = abs(xmax - x0);
b = abs(ymax - y0);

% Scale the intensities to the area of the image. This corrects for the
% fact that there is a constant number of bins, regardless of the image
% size.
A = a*b;
newImage = heat3/A;

if octMaskOption == 0
    mask = (Xq - x0).^2/a^2 + (Yq - y0).^2/b^2 < 1;
    newImage = heat3.*mask;
end

end