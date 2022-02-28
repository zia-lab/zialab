function [BFP_Fields] = Multipole_BFP_3D_Fields_v0p12(multipoleOrder,xpolOutput,uxrange,uyrange,n0,n1,n20,n2e,n3,l,s,d,lambdarange,apodOption)
%   
%   Summary: Generates mulitpole radiation pattern in 4-layer system
%   Based on element-wise operations to handle aribtrary dimension
%   Mutlipole order refers to the last term in the expansion to include ['ED', 'MD', or 'EQ']
%   e.g. entering 'MD' will produce the ED and MD terms

if ~ismember(multipoleOrder,{'ED','MD','EQ'})
    errordlg('Please indicate highest order for multipole expansion: ED, MD, or EQ as string')
end

if nargin==12
   errordlg(['Wrong number of inputs! (Expecting 11: multipoleOrder, xpolOutput, ux, uy, n0, n1, n20, n2e, n3, l, s, d, lambda)'])
end

if length(uxrange)==1 && uxrange~=0
    errordlg('Closed Slit (one-pixel width) ux-range should be ux=0')
end

[~,~,lambda3D]=meshgrid(uxrange,uyrange,lambdarange);
[ux,uy]=meshgrid(uxrange,uyrange);

% Note that ux,uy are normalized versions of kx,ky (i.e. kx=ux*k0=ux*2*pi/lambda)
% Note that ux,uy are 2D arrays --- but lambda3D is a 3D array

% Create Mask
Mask=zeros(size(ux(:,:)));
Mask(find(sqrt(ux(:,:).^2+uy(:,:).^2)<=max(uyrange)*1.001))=1; % 0.1% larger than 1 so that you can capture more than one pixel in the first row
n2=n20;

% Normalized out-of-plane wavenumber uz=kz/k in each layer
uz0 = sqrt(n0^2-ux.^2-uy.^2);
uz1 = sqrt(n1^2-ux.^2-uy.^2);
uz2s = sqrt(n2^2-ux.^2-uy.^2);
uz2p = sqrt(n2^2-(n2/n2e)^2*(ux.^2+uy.^2));
uz3 = sqrt(n3^2-ux.^2-uy.^2);

%Simple Reflection Coefficients for S-Polarization
rs10=(uz1-uz0)./(uz1+uz0);
rs21=(uz2s-uz1)./(uz2s+uz1);

%Total Reflection due to the 1,2 and 1,0 interfaces
% Rs=(rs21+rs10.*exp(2i.*kz1.*l))./(1+rs21.*rs10.*exp(2i.*kz1.*l));
EXP_2i_kz1_l=exp(2i.*bsxfun(@rdivide,uz1,lambda3D)*2*pi*l);
Rs=bsxfun(@plus,rs21,bsxfun(@times,rs10,EXP_2i_kz1_l))./(1+bsxfun(@times,rs21.*rs10,EXP_2i_kz1_l));

clear rs10 rs21

%Reflection Coefficients for P-Polarization
rp10=(n0.^2.*uz1-n1.^2.*uz0)./(n0.^2.*uz1+n1.^2.*uz0);
rp21=(n1.^2.*uz2p-n2.^2.*uz1)./(n1.^2.*uz2p+n2.^2.*uz1);
%Total reflection due to the 1,2 and 1,0 interfraces
% Rp=(rp21+rp10.*exp(2i.*kz1.*l))./(1+rp21.*rp10.*exp(2i.*kz1.*l));
Rp=bsxfun(@plus,rp21,bsxfun(@times,rp10,EXP_2i_kz1_l))./(1+bsxfun(@times,rp21.*rp10,EXP_2i_kz1_l));

clear rp10 rp21 uz0 uz1
clear EXP_2i_kz1_l

% Single Interface Fresnel Coefficients for S-Polarization
ts23=2.*uz2s./(uz3+uz2s);
rs23=(uz2s-uz3)./(uz2s+uz3);

% Total Trasmission Coefficient through the 2,3 interface including interference and multiple reflections

% Phase Terms for propagtion through emitter layer
EXP_1i_kz2_d=exp(1i.*bsxfun(@rdivide,uz2s,lambda3D)*2*pi*d);
EXP_2i_kz2_ds=exp(2i.*bsxfun(@rdivide,uz2s,lambda3D)*2*pi*(d+s));

%  NB: The sign of the final term in Ts (& Tp) depends on the phase of radiated
%  fields in the direction above and below the emitter, which in turn
%  depends on the orientation of the dipole and its nature (ED vs MD)
%
%  For the cartesian dipoles, emitting on axis into ky=0, you can produce the follwoing table 
%  by looking at the symmetry of the electric field above and below the emitter; 
%
%      | s-pol | p-pol |            | s-pol | p-pol |
%  EDx |   X   | 1-Rp  |        MDx | 1-Rs  |   X   |
%  EDy | 1+Rs  |   X   |        MDy |   X   | 1+Rp  |
%  EDz |   X   | 1+Rp  |        MDz | 1+Rs  |   X   |
%
%  Note that, off axis when ky is not zero, then the x and y terms mix, and yielding the following
%
%      | s-pol | p-pol |            | s-pol | p-pol |
%  EDx | 1+Rs  | 1-Rp  |        MDx | 1-Rs  | 1+Rp  |
%  EDy | 1+Rs  | 1-Rp   |       MDy | 1-Rs  | 1+Rp  |
%  EDz |   X   | 1+Rp  |        MDz | 1+Rs  |   X   |
%
% FOR CONVENIENCE, we adopt the following nomenclature based on the orientations:
%
% Tsxy is the (1-Rs) formula for xy-oriented MDs  
% Tsz  is the (1+Rs) formula for z-oriented MDs   [which also appears for xy-oriented EDs]
%
% Tsxy=ts23.*exp(1i*kz2*d)./(1-rs23.*Rs.*exp(2i*kz2*(d+s))).*(1-Rs.*exp(2i*kz2*s));
% Tsz =ts23.*exp(1i*kz2*d)./(1-rs23.*Rs.*exp(2i*kz2*(d+s))).*(1+Rs.*exp(2i*kz2*s));
Ts=bsxfun(@times,ts23,EXP_1i_kz2_d)./(1-bsxfun(@times,rs23,Rs.*EXP_2i_kz2_ds));

clear ts23 rs23 EXP_1i_kz2_d EXP_2i_kz2_ds

S_EXP_2i_kz2_s=exp(2i.*bsxfun(@rdivide,uz2s,lambda3D)*2*pi*s);
Tsxy=Ts.*(1-Rs.*S_EXP_2i_kz2_s);
Tsz =Ts.*(1+Rs.*S_EXP_2i_kz2_s); 

clear S_EXP_2i_kz2_s Rs Ts


% Single Interface Fresnel Coefficients for P-Polarization
tp23=2.*n3.^2.*uz2p./(n2.^2.*uz3+n3.^2.*uz2p).*(n2./n3);
rp23=(n3.^2.*uz2p-n2.^2.*uz3)./(n3.^2.*uz2p+n2.^2.*uz3);

% Total Trasmission Coefficient through the 2,3 interface including interference and multiple reflections
% Tpxy is the (1-Rp) formula for xy-oriented EDs 
% Tpz  is the (1+Rp) formula for z-oriented EDs   [which also appears for xy-oriented MDs]
%
% Tpxy=tp23.*exp(1i*kz2*d)./(1-rp23.*Rp.*exp(2i*kz2*(d+s))).*(1-Rp.*exp(2i*kz2*s));
% Tpz =tp23.*exp(1i*kz2*d)./(1-rp23.*Rp.*exp(2i*kz2*(d+s))).*(1+Rp.*exp(2i*kz2*s));
EXP_1i_kz2_d=exp(1i.*bsxfun(@rdivide,uz2p,lambda3D)*2*pi*d);
EXP_2i_kz2_ds=exp(2i.*bsxfun(@rdivide,uz2p,lambda3D)*2*pi*(d+s));
Tp=bsxfun(@times,tp23,EXP_1i_kz2_d)./(1-bsxfun(@times,rp23,Rp.*EXP_2i_kz2_ds));
clear EXP_1i_kz2_d EXP_2i_kz2_ds tp23 rp23 
P_EXP_2i_kz2_s=exp(2i.*bsxfun(@rdivide,uz2p,lambda3D)*2*pi*s);
Tpxy=Tp.*(1-Rp.*P_EXP_2i_kz2_s);
Tpz =Tp.*(1+Rp.*P_EXP_2i_kz2_s);                                                                      

clear Rp Tp P_EXP_2i_kz2_s

% A = abs(n3./uz3);    %Apodization Factor
%%%%%%%%%%%%%%%%%%%%%%%%%%%
%ELECTRIC DIPOLE CALC
%%%%%%%%%%%%%%%%%%%%%%%%%%%

    % FUNCTIONS DERIVED By Jon Kurvits (Corrected by JK and RZ on 01/08/2014, including coonsistency changed of hpol and vpol to correspond with xpol and ypol)
    % EDx=sqrt(A./3).*(kz3./(kx.^2+ky.^2)).*(hpol.*(kx.^2./k2.*Tpxy+ky.^2./kz2.*Tsz)+vpol.*(kx.*ky./k2.*Tpxy-kx.*ky./kz2.*Tsz));
    % EDy=sqrt(A./3).*(kz3./(kx.^2+ky.^2)).*(hpol.*(kx.*ky./k2.*Tpxy-kx.*ky./kz2.*Tsz)+vpol.*(ky.^2./k2.*Tpxy+kx.^2./kz2.*Tsz));
    % EDz=sqrt(A./3).*(kz3./(kx.^2+ky.^2)).*(hpol.*(kx.*(kx.^2+ky.^2)./(k2.*kz2).*Tpz)+vpol.*(ky.*(kx.^2+ky.^2)./(k2.*kz2).*Tpz));
    %
    % NORMALIZED FORMS for y-polarization (i.e. hpol=0, vpol=1) obtained by substituting k's with u's and n's (i.e. kx->ux, kz2 -> uz2, k2->n2)  
    % ypol.EDx=sqrt(A./3).*(uz3./(ux.^2+uy.^2)).*(ux.*uy./n2.*Tpxy-ux.*uy./uz2.*Tsz);
    % ypol.EDy=sqrt(A./3).*(uz3./(ux.^2+uy.^2)).*(uy.^2./n2.*Tpxy+ux.^2./uz2.*Tsz); 
    % ypol.EDz=sqrt(A./3).*(uz3./(ux.^2+uy.^2)).*(uy.*(ux.^2+uy.^2)./(n2.*uz2).*Tpz);
    
    % x-polarized fields can be obtained by swapping x and y:
    % xpol.EDx = ypol.EDy with ux and uy interchanged
    % xpol.EDy = ypol.EDx with ux and uy interchanged
    % xpol.EDz = ypol.EDz with ux and uy interchanged
    % For case where [ux,uy] form a 2D matrix, the interchange can be performed by transposing the field matrix (using permute(...,[2,1,3]))

if apodOption == 0    
    B=(uz3./(ux.^2+uy.^2));%.*sqrt(abs(1.5./uz3)./3);
else
    B=(uz3./(ux.^2+uy.^2)).*sqrt(abs(1.5./uz3)./3);
end
clear A;
BFP_Fields.ypol.EDx=bsxfun(@times,B,(bsxfun(@times,ux.*uy./n2,Tpxy)-bsxfun(@times,ux.*uy./uz2s,Tsz)));
BFP_Fields.ypol.EDy=bsxfun(@times,B,(bsxfun(@times,uy.^2./n2,Tpxy)+bsxfun(@times,ux.^2./uz2s,Tsz)));
if strcmp(multipoleOrder,'MD') && length(uxrange)~=1  % Tpxy is not used for MDs, so we can clear unless EQs needed
    clear Tpxy
end
BFP_Fields.ypol.EDz=bsxfun(@times,B.*(uy.*(ux.^2+uy.^2)./(n2.*uz2s)),Tpz);
if strcmp(multipoleOrder,'ED') && length(uxrange)~=1
    clear Tpz Tsz Tsxy
end

if xpolOutput==1
    if length(uxrange)==1 % Special Case Treatment for Closed Slit Case (transposing does not work for array)
        BFP_Fields.xpol.EDx=bsxfun(@times,B,(bsxfun(@times,ux.^2./n2,Tpxy)+bsxfun(@times,uy.^2./uz2s,Tsz)));
        BFP_Fields.xpol.EDy=bsxfun(@times,B,(bsxfun(@times,uy.*ux./n2,Tpxy)-bsxfun(@times,uy.*ux./uz2s,Tsz)));
        BFP_Fields.xpol.EDz=bsxfun(@times,B.*(ux.*(uy.^2+ux.^2)./(n2.*uz2s)),Tpz);
    else
        BFP_Fields.xpol.EDx=permute(BFP_Fields.ypol.EDy,[2,1,3]);
        BFP_Fields.xpol.EDy=permute(BFP_Fields.ypol.EDx,[2,1,3]);
        BFP_Fields.xpol.EDz=permute(BFP_Fields.ypol.EDz,[2,1,3]);
    end
end



%%%%%%%%%%%%%%%%%%%%%%%%%%%
%MAGNETIC DIPOLE CALC
%%%%%%%%%%%%%%%%%%%%%%%%%%%
if ismember(multipoleOrder,{'MD','EQ'})
    
        % FUNCTIONS DERIVED By Jon Kurvits (Corrected by JK and RZ on 01/08/2014, including coonsistency changed of hpol and vpol to correspond with xpol and ypol)
        % MDx=sqrt(A./3).*(kz3./(kx.^2+ky.^2)).*(hpol.*(kx.*ky./kz2.*Tpz-kx.*ky./k2.*Tsxy)+vpol.*(ky.^2./kz2.*Tpz+kx.^2./k2.*Tsxy));
        % MDy=sqrt(A./3).*(kz3./(kx.^2+ky.^2)).*(hpol.*(kx.^2./kz2.*Tpz+ky.^2./k2.*Tsxy)+vpol.*(-kx.*ky./k2.*Tsxy+kx.*ky./kz2.*Tpz));  Corrected sign in final term, should be -Tsxy +Tpz
        % MDz=sqrt(A./3).*(kz3./(kx.^2+ky.^2)).*(hpol.*(ky.*(kx.^2+ky.^2)./(k2.*kz2).*Tsz)-vpol.*(kx.*(kx.^2+ky.^2)./(k2.*kz2).*Tsz)); Corrected sign in final term, should be -Tsz
        %
        % NEW DERIVATION BASED ON TRANSFORMING ED EQUATIONS,  s<->p  and vMD = hED whereas hMD = -vED NOTE SIGN CHANGE
        % MDx=sqrt(A./3).*(kz3./(kx.^2+ky.^2)).*(vpol.*(kx.^2./k2.*Tsxy+ky.^2./kz2.*Tpz)-hpol.*(kx.*ky./k2.*Tsxy-kx.*ky./kz2.*Tpz));
        % MDy=sqrt(A./3).*(kz3./(kx.^2+ky.^2)).*(vpol.*(kx.*ky./k2.*Tsxy-kx.*ky./kz2.*Tpz)-hpol.*(ky.^2./k2.*Tsxy+kx.^2./kz2.*Tpz));
        % MDz=sqrt(A./3).*(kz3./(kx.^2+ky.^2)).*(vpol.*(kx.*(kx.^2+ky.^2)./(k2.*kz2).*Tsz)-hpol.*(ky.*(kx.^2+ky.^2)./(k2.*kz2).*Tsz));
                
        % old: MDx= sqrt(A./3).*(kz3./(kx.^2+ky.^2)).*(hpol.*(kx.*ky./kz2.*Tpz-kx.*ky./k2.*Tsxy)+vpol.*(ky.^2./kz2.*Tpz+kx.^2./k2.*Tsxy));
        % new: MDx= sqrt(A./3).*(kz3./(kx.^2+ky.^2)).*(hpol.*(kx.*ky./kz2.*Tpz-kx.*ky./k2.*Tsxy)+vpol.*(ky.^2./kz2.*Tpz+kx.^2./k2.*Tsxy));  
        % old: MDy= sqrt(A./3).*(kz3./(kx.^2+ky.^2)).*(hpol.*(kx.^2./kz2.*Tpz+ky.^2./k2.*Tsxy)+vpol.*(-kx.*ky./k2.*Tsxy+kx.*ky./kz2.*Tpz));
        % new: MDy=-sqrt(A./3).*(kz3./(kx.^2+ky.^2)).*(hpol.*(kx.^2./kz2.*Tpz+ky.^2./k2.*Tsxy)+vpol.*(-kx.*ky./k2.*Tsxy+kx.*ky./kz2.*Tpz)); Differ only by sign, perhaps sign convention
        % old: MDz= sqrt(A./3).*(kz3./(kx.^2+ky.^2)).*(hpol.*(ky.*(kx.^2+ky.^2)./(k2.*kz2).*Tsz)-vpol.*(kx.*(kx.^2+ky.^2)./(k2.*kz2).*Tsz));
        % new: MDz=-sqrt(A./3).*(kz3./(kx.^2+ky.^2)).*(hpol.*(ky.*(kx.^2+ky.^2)./(k2.*kz2).*Tsz)-vpol.*(kx.*(kx.^2+ky.^2)./(k2.*kz2).*Tsz)); Differ only by sign, perhaps sign convention

        % NORMALIZED FORMS OF OLD FORMS for y-polarization (i.e. hpol=0, vpol=1) obtained by substituting k's with u's and n's (i.e. kx->ux, kz2 -> uz2, k2->n2)  
        % ypol.MDx=sqrt(A./3).*(uz3./(ux.^2+uy.^2)).*(uy.^2./uz2.*Tpz+ux.^2./n2.*Tsxy);
        % ypol.MDy=-sqrt(A./3).*(uz3./(ux.^2+uy.^2)).*(ux.*ky./n2.*Tsxy-ux.*uy./uz2.*Tpz);
        % ypol.MDz=-sqrt(A./3).*(uz3./(ux.^2+uy.^2)).*(ux.*(ux.^2+uy.^2)./(n2.*uz2).*Tsz);
        %
        % x-polarized fields can be obtained by swapping x and y with overall sign change:
        % xpol.MDx = -hMDy with ux and uy interchanged
        % xpol.MDy = -hMDx with ux and uy interchanged
        % xpol.MDz = -hMDz with ux and uy interchanged

        
    BFP_Fields.ypol.MDz=-bsxfun(@times,B.*(ux.*(ux.^2+uy.^2)./(n2.*uz2s)),Tsz);
        if strcmp(multipoleOrder,'MD') && length(uxrange)~=1
            clear Tsz
        end
    BFP_Fields.ypol.MDx=-bsxfun(@times,B,(bsxfun(@times,uy.^2./uz2p,Tpz)+bsxfun(@times,ux.^2./n2,Tsxy))); 
    BFP_Fields.ypol.MDy=-bsxfun(@times,B,(bsxfun(@times,ux.*uy./n2,Tsxy)-bsxfun(@times,ux.*uy./uz2p,Tpz))); 
  
    if length(uxrange)~=1
        clear  Tsxy
            if strcmp(multipoleOrder,'MD')
              clear Tpz
            end
    end

    if xpolOutput==1
        if length(uxrange)==1 % Special Case Treatment for Closed Slit Case (transposing does not work for array, so explicitly switched ux and uy)
            BFP_Fields.xpol.MDx=-bsxfun(@times,B,(bsxfun(@times,uy.*ux./n2,Tsxy)-bsxfun(@times,uy.*ux./uz2p,Tpz))); 
            BFP_Fields.xpol.MDy=-bsxfun(@times,B,(bsxfun(@times,ux.^2./uz2p,Tpz)+bsxfun(@times,uy.^2./n2,Tsxy))); 
            BFP_Fields.xpol.MDz=-bsxfun(@times,B.*(uy.*(uy.^2+ux.^2)./(n2.*uz2s)),Tsz);
        else
            BFP_Fields.xpol.MDx=-permute(BFP_Fields.ypol.MDy,[2,1,3]);
            BFP_Fields.xpol.MDy=-permute(BFP_Fields.ypol.MDx,[2,1,3]);
            BFP_Fields.xpol.MDz=-permute(BFP_Fields.ypol.MDz,[2,1,3]);
        end
    end
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%
%ELECTRIC QUADRUPOLE CALC
%%%%%%%%%%%%%%%%%%%%%%%%%%%
if strcmp(multipoleOrder,'EQ')    %Generate BFP_Fields output
       
    % FUNCTIONS DERIVED By Jon Kurvits (Corrected by JK and RZ on 01/08/2014, including coonsistency changed of hpol and vpol to correspond with xpol and ypol)
    % pEQxz=(1./k2).*sqrt(A.*5./4).*(kz3./(kx.^2+ky.^2)).*(hpol.*(kx.^2.*(kx.^2+ky.^2)./(k2.*kz2).*Tpz-kx.^2.*kz3./k2.*Tpxy-ky.^2.*kz3./kz2.*Tsz)+...
    %          vpol.*(kx.*ky.*(kx.^2+ky.^2)./(k2.*kz2).*Tpz-ky.*kx.*kz3./k2.*Tpxy+kx.*ky.*kz3./kz2.*Tsz));  
    % sEQyz=(1./k2).*sqrt(A.*5./4).*(kz3./(kx.^2+ky.^2)).*(hpol.*(kx.*ky.*(kx.^2+ky.^2)./(k2.*kz2).*Tpz-ky.*kx.*kz3./k2.*Tpxy+kx.*ky.*kz3./kz2.*Tsz)+...
    %          vpol.*(ky.^2.*(kx.^2+ky.^2)./(k2.*kz2).*Tpz-ky.^2.*kz3./k2.*Tpxy-kx.^2.*kz3./kz2.*Tsz));
    % pEQzz=(1./k2).*sqrt(A.*5./4).*(kz3./(kx.^2+ky.^2)).*(hpol.*(1./2.*kx.*(kx.^2+ky.^2)./k2.*Tpxy+kx.*kz3.*(kx.^2+ky.^2)./(k2.*kz2).*Tpz)+...
    %          vpol.*(1./2.*ky.*(kx.^2+ky.^2)./k2.*Tpxy+ky.*kz3.*(kx.^2+ky.^2)./(k2.*kz2).*Tpz));
    % sEQxy=(1./k2).*sqrt(A.*5./4).*(kz3./(kx.^2+ky.^2)).*(hpol.*(2.*kx.^2.*ky./k2.*Tpxy+ky./kz2.*(ky.^2-kx.^2).*Tsz)+...
    %          vpol.*(2.*ky.^2.*kx./k2.*Tpxy+kx./kz2.*(kx.^2-ky.^2).*Tsz));
    % pEQxxyy=sqrt(A).*(qQ(1,1)*kz3./(kx.^2+ky.^2)).*(hpol.*(2.*kx.*ky.^2./kz2.*Tsz+kx./k2.*Tpxy.*(kx.^2-ky.^2))+...
    %          vpol.*(ky./k2.*Tpxy.*(kx.^2-ky.^2)-2*kx.^2.*ky./kz2.*Tsz));
    %
    % NORMALIZED FORMS for y-polarization (i.e. hpol=0, vpol=1) obtained by substituting k's with u's and n's (i.e. kx->ux, kz2 -> uz2, k2->n2)  
    % ypol.EQxz=(1./n2).*sqrt(A.*5./4).*(uz3./(ux.^2+uy.^2)).*(ux.*uy.*(ux.^2+uy.^2)./(n2.*uz2).*Tpz-uy.*ux.*uz3./n2.*Tpxy+ux.*uy.*uz3./uz2.*Tsz);
    % ypol.EQyz=(1./n2).*sqrt(A.*5./4).*(uz3./(ux.^2+uy.^2)).*(uy.^2.*(ux.^2+uy.^2)./(n2.*uz2).*Tpz-uy.^2.*uz3./n2.*Tpxy-ux.^2.*uz3./uz2.*Tsz);
    % ypol.EQzz=(1./n2).*sqrt(A.*5./4).*(uz3./(ux.^2+uy.^2)).*(1./2.*uy.*(ux.^2+uy.^2)./n2.*Tpxy+uy.*uz3.*(ux.^2+uy.^2)./(n2.*uz2).*Tpz);  %NB: There may be an overall sign convection difference for EQzz
    % ypol.EQxy=(1./n2).*sqrt(A.*5./4).*(uz3./(ux.^2+uy.^2)).*(2.*uy.^2.*ux./n2.*Tpxy+ux./uz2.*(ux.^2-uy.^2).*Tsz);
    % ypol.EQxxyy=(1./n2).*sqrt(A.*5./4).*(uz3./(ux.^2+uy.^2)).*(uy./n2.*Tpxy.*(ux.^2-uy.^2)-2*ux.^2.*uy./uz2.*Tsz);
  
    % x-polarized fields can ALMOST be obtained by swapping x and y alone, except for EQxxyy which requires an additional sign change:
    % xpol.EQxz = ypol.EQyz with ux and uy interchanged
    % xpol.EQyz = ypol.EQxz with ux and uy interchanged
    % xpol.EQzz = ypol.EQzz with ux and uy interchanged
    % xpol.EQxy = ypol.EQxy with ux and uy interchanged
    % xpol.EQxxyy = -ypol.EQxxyy with ux and uy interchanged
    B=(1./n2).*sqrt(abs(1.5./uz3).*5./4).*(uz3./(ux.^2+uy.^2));
    BFP_Fields.ypol.EQxz=bsxfun(@times,B,bsxfun(@times,ux.*uy.*(ux.^2+uy.^2)./(n2.*uz2p),Tpz)-bsxfun(@times,uy.*ux.*uz3./n2,Tpxy)+bsxfun(@times,ux.*uy.*uz3./uz2s,Tsz));
    BFP_Fields.ypol.EQyz=bsxfun(@times,B,bsxfun(@times,uy.^2.*(ux.^2+uy.^2)./(n2.*uz2p),Tpz)-bsxfun(@times,uy.^2.*uz3./n2,Tpxy)-bsxfun(@times,ux.^2.*uz3./uz2s,Tsz));
    BFP_Fields.ypol.EQzz=bsxfun(@times,B,bsxfun(@times,1./2.*uy.*(ux.^2+uy.^2)./n2,Tpxy)+bsxfun(@times,uy.*uz3.*(ux.^2+uy.^2)./(n2.*uz2p),Tpz));
    if length(uxrange)~=1 
        clear Tpz
    end
    
    BFP_Fields.ypol.EQxy=bsxfun(@times,B,bsxfun(@times,2.*uy.^2.*ux./n2,Tpxy)+bsxfun(@times,ux./uz2s.*(ux.^2-uy.^2),Tsz));
    BFP_Fields.ypol.EQxxyy=bsxfun(@times,B,bsxfun(@times,uy./n2.*(ux.^2-uy.^2),Tpxy)-bsxfun(@times,2*ux.^2.*uy./uz2s,Tsz));
    if length(uxrange)~=1 
        clear Tpxy Tsz    
    end
    
    if xpolOutput==1
        if length(uxrange)==1 % Special Case Treatment for Closed Slit Case (transposing does not work for array, so explicitly switched ux and uy)
            BFP_Fields.xpol.EQyz=bsxfun(@times,B,bsxfun(@times,uy.*ux.*(uy.^2+ux.^2)./(n2.*uz2p),Tpz)-bsxfun(@times,ux.*uy.*uz3./n2,Tpxy)+bsxfun(@times,uy.*ux.*uz3./uz2s,Tsz));
            BFP_Fields.xpol.EQxz=bsxfun(@times,B,bsxfun(@times,ux.^2.*(uy.^2+ux.^2)./(n2.*uz2p),Tpz)-bsxfun(@times,ux.^2.*uz3./n2,Tpxy)-bsxfun(@times,uy.^2.*uz3./uz2s,Tsz));
            BFP_Fields.xpol.EQzz=bsxfun(@times,B,bsxfun(@times,1./2.*ux.*(uy.^2+ux.^2)./n2,Tpxy)+bsxfun(@times,ux.*uz3.*(uy.^2+ux.^2)./(n2.*uz2s),Tpz));
            BFP_Fields.xpol.EQxy=bsxfun(@times,B,bsxfun(@times,2.*ux.^2.*uy./n2,Tpxy)+bsxfun(@times,uy./uz2.*(uy.^2-ux.^2),Tsz));
            BFP_Fields.xpol.EQxxyy=(-1)*bsxfun(@times,B,bsxfun(@times,ux./n2.*(uy.^2-ux.^2),Tpxy)-bsxfun(@times,2*uy.^2.*ux./uz2s,Tsz));
        else
            BFP_Fields.xpol.EQxz=permute(BFP_Fields.ypol.EQyz,[2,1,3]);
            BFP_Fields.xpol.EQyz=permute(BFP_Fields.ypol.EQxz,[2,1,3]);
            BFP_Fields.xpol.EQzz=permute(BFP_Fields.ypol.EQzz,[2,1,3]);
            BFP_Fields.xpol.EQxy=permute(BFP_Fields.ypol.EQxy,[2,1,3]);
            BFP_Fields.xpol.EQxxyy=(-1)*permute(BFP_Fields.ypol.EQxxyy,[2,1,3]);
        end
    end
    
end 

polNames=fieldnames(BFP_Fields);
for nn=1:length(polNames)
    basisNames=fieldnames(BFP_Fields.(polNames{nn}));
    for mm=1:length(basisNames)
        BFP_Fields.(polNames{nn}).(basisNames{mm})=bsxfun(@times,Mask,BFP_Fields.(polNames{nn}).(basisNames{mm}));
        %Removes NaNs from Data    
        TempNaNs=find(isnan(BFP_Fields.(polNames{nn}).(basisNames{mm})));
        if ~isempty(TempNaNs)
            BFP_Fields.(polNames{nn}).(basisNames{mm})(TempNaNs)=0.5*(BFP_Fields.(polNames{nn}).(basisNames{mm})(TempNaNs-1)+BFP_Fields.(polNames{nn}).(basisNames{mm})(TempNaNs+1));
        end
        clear TempNaNs
    end
end