function heat = binnedIntensityMap(xVals,yVals,I,gridSize)

% Takes a bunch of scattered points (x,y) and associated intensity values
% I, divides them into a grid of bins determined by N, and adds up
% the intensities in each bin.

totalMax = max(abs([xVals;yVals]));

xAxis = linspace(-totalMax,totalMax, gridSize);
yAxis = linspace(-totalMax,totalMax, gridSize);
heat = zeros(gridSize-1,gridSize-1);

for i = 1:gridSize-1
    yidx = find(yVals >= yAxis(i)  &  yVals <= yAxis(i+1));
    xOptions = xVals(yidx);
    IOptions = I(yidx);
    
    for j = 1:gridSize-1
        xidx = find(xOptions >= xAxis(j)  &  xOptions <= xAxis(j+1));  
        if isempty(xidx)
            heat(i,j) = 0;
        else
            heat(i,j) = sum(IOptions(xidx));
        end 
    end  
end

% figure;
% imagesc(xAxis,yAxis,heat)
% set(gca,'YDir','normal')
% colormap('jet')
% xlabel('x [mm]','Interpreter','latex');
% ylabel('y [mm]','Interpreter','latex');
end