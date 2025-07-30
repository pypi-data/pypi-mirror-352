function out = tansig0(n,code)


switch code
    case 'f'
        a = 2 ./ (1 + exp(-2*n)) - 1;
        i = find(~isfinite(a));
        a(i) = sign(n(i));
        out = a;
    case 'd'
        a = n;
        d = 1-(a.*a);
        out = d;
end
