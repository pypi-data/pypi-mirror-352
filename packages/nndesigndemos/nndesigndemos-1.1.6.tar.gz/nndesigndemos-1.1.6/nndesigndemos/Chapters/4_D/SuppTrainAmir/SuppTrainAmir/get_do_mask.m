function [net] = get_do_mask(net,P)

do = net.do;
s = net.S;
M = length(net.f);
[~,q] = size(P);

mask = cell(1,M);

for m=1:M
    if do{m}~=1
        sm = s{m};
        num = round(do{m}*sm);
        ind1 = randperm(sm);
        ind1 = ind1(1:num);
        temp = zeros(sm,1);
        temp(ind1) = 1;
        mask{m} = temp*ones(1,q);        
    end        
end

net.mask = mask;

end