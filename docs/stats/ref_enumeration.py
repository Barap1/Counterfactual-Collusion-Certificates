import itertools, math
def perm_p(F,K,m,side):
    # H0: tau = m where tau = mean(K)-mean(F). Adjusted K' = K-m. exact perms over labels.
    pool=[x for x in F]+[k-m for k in K]; nK=len(K); n=len(pool)
    obs=sum(pool[len(F):])/nK - sum(pool[:len(F)])/len(F)
    tot=sum(pool); cnt=0; N=0
    for idx in itertools.combinations(range(n),nK):
        sK=sum(pool[i] for i in idx); t=sK/nK-(tot-sK)/(n-nK)
        N+=1
        if side=='ge' and t>=obs-1e-12: cnt+=1
        if side=='le' and t<=obs+1e-12: cnt+=1
    return cnt/N
def lower(F,K,alpha=0.05,lo=-60,hi=60,step=0.01):
    # inf{m: p_ge(m)>alpha}; if p(lo)>alpha -> -inf
    m=lo
    while m<=hi:
        if perm_p(F,K,m,'ge')>alpha: return round(m,2)
        m=round(m+step,10)
    return hi
def upper(F,K,alpha=0.05,lo=-60,hi=60,step=0.01):
    # sup{m: p_le(m)>alpha}
    m=hi; 
    while m>=lo:
        if perm_p(F,K,m,'le')>alpha: return round(m,2)
        m=round(m-step,10)
    return lo
if __name__=="__main__":
    print("min p", {(a,b):1/math.comb(a+b,b) for a,b in [(2,2),(3,3),(4,4),(3,4),(5,5),(4,2),(2,4)]})
    F=[0,1,2,3];K=[10,11,12,13]
    print("sep", lower(F,K), upper(F,K))
    F=[4,7,9,12];K=[6,10,13,15]
    print("overlap", lower(F,K), upper(F,K))
    F=[5.0,5.0,5.0,5.0];K=[12.5]*4
    print("degenerate", lower(F,K), upper(F,K))
    F=[3,5,8,6];K=[4,6,7,5]
    print("null-ish", lower(F,K), upper(F,K))
