function [urange, radPattern] = bfpTestScript(N) %

% Just sets up the 'Multipole_BFP...' function to get a radiation pattern
% so I don't mix up all of the inputs. This assumes a square grid of kx,ky,
% and N is the number of points along one axis of the grid.

xpolOutput = 1;
urange = linspace(-1.39, 1.39, N);
n0 = 1;
n1 = 1;
n20 = 1.7;
n2e = 1.7;
n3 = 1.5;
l = 0;
s = 10;
d = 10;
lambdarange = 500;

field = Multipole_BFP_3D_Fields_v0p12('MD',xpolOutput,urange,urange,n0,n1,n20,n2e,n3,l,s,d,lambdarange,0);

edx = 0;
edy = 0;
edz = 0;
mdx = 0;
mdy = 0;
mdz = 1;

pol = 0;

if pol == 0
    radPattern = edx*abs(field.xpol.EDx).^2 + edy*abs(field.xpol.EDy).^2 + edz*abs(field.xpol.EDz).^2 + ...
        mdx*abs(field.xpol.MDx).^2 + mdy*abs(field.xpol.MDy).^2 + mdz*abs(field.xpol.MDz).^2;
elseif pol ==1
    radPattern = edx*abs(field.ypol.EDx).^2 + edy*abs(field.ypol.EDy).^2 + edz*abs(field.ypol.EDz).^2 + ...
        mdx*abs(field.ypol.MDx).^2 + mdy*abs(field.ypol.MDy).^2 + mdz*abs(field.ypol.MDz).^2;
end
figure;
imagesc(urange, urange, radPattern);
set(gca,'YDir','normal');
xlabel('k$_{x}$/k$_{0}$','Interpreter','latex');
ylabel('k$_{y}$/k$_{0}$','Interpreter','latex');
title('Raw Radiation Pattern','Interpreter','latex');
colormap('hot')
% 
% figure;
% xSection = radPattern(:, round(N/2));
% % p = cos(asin(urange/1.5));
% plot(urange, xSection/max(xSection));
% xlabel('ky/k0')

end
