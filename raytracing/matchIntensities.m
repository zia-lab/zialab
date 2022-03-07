function Ivals = matchIntensities(N_BFP,ux,uy,octMaskOption)

% Function to assign intensity values to a set of ux,uy values
% INPUTS
%     -N_BFP: grid size for the caluclated radiation pattern
%     -ux,uy: k vector components that you want intensities for
%     -octMaskOption: 0 is standard, 1 makes intensities uniform
% OUTPUT:
%     -Ivals: vector of intensity values corresponding to ux,uy


if octMaskOption == 1
    Ivals = ones(length(ux),1);
else
    [urange, radPattern] = bfpTestScript(N_BFP);
    Ivals = transpose(interp2(urange,urange,radPattern,ux,uy));
end

end