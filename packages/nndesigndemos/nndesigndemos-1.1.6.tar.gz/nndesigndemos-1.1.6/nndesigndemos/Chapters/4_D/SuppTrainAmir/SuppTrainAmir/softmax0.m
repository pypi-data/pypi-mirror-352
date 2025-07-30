function [out] = softmax0(n,code)


switch code
    case 'f'
        [s,q] = size(n);
        numer = exp(n);
        denom = 1 ./ sum(numer,1);
        a = numer .* denom(ones(1,s),:);
        out = a;
    case 'd'
        a = n;
        [Sm,Q] = size(a);
        d = cell(1,Q);
        for q=1:Q
            d{q} = diag(a(:,q))*sum(a(:,q)) - kron(a(:,q)',a(:,q));
        end
        out = d;
end

end