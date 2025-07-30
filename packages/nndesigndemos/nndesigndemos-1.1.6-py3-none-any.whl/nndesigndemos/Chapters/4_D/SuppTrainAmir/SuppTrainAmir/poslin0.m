function out = poslin0(n,code)


switch code
    case 'f'
        a = max(0,n);
        out = a;
    case 'd'
        a = n;
        d = sign(a);
        out = d;
end
