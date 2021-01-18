function [xSec,uAxis] = plotBFPImage(q3,heat3,plotLimit,defocus,sourceRadii,uLims,clims,plotCode)

if (plotCode == 0  ||  plotCode == 2)
    figure;
    if clims == 0
        imagesc(q3,q3,heat3)
    else
        imagesc(q3,q3,heat3,clims)
    end

    set(gca,'YDir','normal')
    colormap('hot')
    xlabel('x [mm]','Interpreter','latex');
    ylabel('y [mm]','Interpreter','latex');
%     colorbar;
    t = plotLimit;
    xlim([-t,t]);
    ylim([-t,t]);
    titleStr = ['defocus: ',num2str(defocus),' mm'];
    title(titleStr,'Interpreter','latex');
%     set(gca, 'Color', [0,0,0.56])
end

xSec = 0;
uAxis = 0;

if (plotCode == 1  ||  plotCode == 2)
    figure;
    uAxis = linspace(uLims(1),uLims(2),length(q3));
    xSec = heat3(:,round(length(q3)/2));
    plot(uAxis,xSec,'LineWidth',2)
    xlabel('uy','Interpreter','latex');
    ylabel('Intensity [arb. units]','Interpreter','latex');
    titleStr = ['radius: ',num2str(sourceRadii*1e3),' $\mu$m'];
    title(titleStr, 'Interpreter','latex');
    if length(clims) > 1
        ylim(clims)
    end
    xlim(uLims)    
end

end