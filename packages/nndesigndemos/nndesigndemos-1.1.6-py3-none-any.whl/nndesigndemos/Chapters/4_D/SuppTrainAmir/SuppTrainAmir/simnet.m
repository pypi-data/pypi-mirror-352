function [a] = simnet(net,P)

do = net.do;
mask = net.mask;
doflag = net.doflag;
M = length(net.f);
[r,q] = size(P);
if r~=net.R
    disp(['Input dimension ' num2str(r) ' does not match network size ' num2str(net.R) '.'])
    return
end
a = cell(1,M+1);
a{1} = P;

for m=1:M
    n = net.w{m}*a{m} + net.b{m}*ones(1,q);
    a{m+1} = net.f{m}(n,'f');
    if do{m}~=1 && doflag
        a{m+1} = mask{m}.*a{m+1};     
    end        
end

a(1) = [];

end