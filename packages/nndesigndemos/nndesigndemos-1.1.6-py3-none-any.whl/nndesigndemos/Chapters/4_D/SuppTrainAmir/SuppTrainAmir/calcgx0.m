function [gX] = calcgx0(net,p,a,t) %X,P,A,E)

doflag = net.doflag;
do = net.do;
mask = net.mask;
dflag = net.doflag;
S = net.S;
M = length(S);
[r,q] = size(p);
if r~=net.R
    disp(['Input dimension ' num2str(r) ' does not match network size ' num2str(net.R) '.'])
    return
end
s = cell(1,M);
gw = cell(1,M);
gb = cell(1,M);


dp = net.perf(a{M},t,'d');
df = net.f{M}(a{M},'d');
s{M} = zeros(S{M},q);
if iscell(df)  
    for qq=1:q
        s{M}(:,qq) = df{qq} * dp(:,qq);
    end
else
    s{M} = df .* dp;
end

if do{M}~=1 && doflag
    s{M} = mask{M}.*s{M};     
end        


gw{M} = s{M} * a{M-1}';
gb{M} = s{M} * ones(q,1);


for i=(M-1):-1:1
    % 
    s{i} = net.w{i+1}'*s{i+1};
    
    tf = net.f{i};
    if isequal(tf,@purelin0)
            % purelin does not change s
    elseif isequal(tf,@tansig0)
            s{i} = (1-(a{i}.*a{i})).*s{i};
    elseif isequal(tf,@logsig0)
            s{i} = a{i}.*(1-a{i}) .* s{i};
    else
        Fdot = net.f{i}(a{i},'d'); 
        if iscell(Fdot)  
            for qq=1:Q
                s{i}(:,qq) = Fdot{qq} * s{i}(:,qq);
            end
        else
            s{i} = Fdot .* s{i};
        end  
    end
    
    if do{i}~=1 && doflag
        s{i} = mask{i}.*s{i};     
    end        

    if i==1
        gw{i} =  s{i} * p';
    else
        gw{i} =  s{i} * a{i-1}';
    end
    gb{i} = s{i} * ones(q,1);

end

gX = [];
for i=1:M
    gX = [gX; gw{i}(:)];
    gX = [gX; gb{i}(:)];
end


end
