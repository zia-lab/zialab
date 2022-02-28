function [ux,uy] = pupil2u(px,py,a,d,xOffset,yOffset)

% Converts from normalized pupil coordinates to normalized k space
% coordinates. px and py are corresponding vectors for the pupil
% coordinates, a is the aperture stop semi diameter, and d is the distance
% from the object to the stop surface.

cx = (px*a - xOffset)/d;
cy = (py*a - yOffset)/d;
n = 1.5;

ux = n* cx./sqrt(1 + cx.^2 + cy.^2);
uy = n* cy./sqrt(1 + cx.^2 + cy.^2);

end