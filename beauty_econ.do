*******************************************************
** Task: Applied Econometrics Final Paper
**
** Input: dfps.dta
**
** Output: cfps.log
**
*******************************************************

//Housekeeping
set more off
clear all
xtset, clear

cd "C:\Users\surface\OneDrive - The University of Chicago\Desktop\UChicago\IPAL\Applied Econometrics\Econometrics-final paper" 
capture log close
log using "C:\Users\surface\OneDrive - The University of Chicago\Desktop\UChicago\IPAL\Applied Econometrics\Econometrics-final paper\CFPS", replace text

//Data cleaning 
gen lnincome = log(income)

gen bmi = weight/(height^2)

gen east = 0
replace east = 1 if provcd18==11|provcd18==12|provcd18==13|provcd18==21|provcd18==31|provcd18==32|provcd18==33|provcd18==35|provcd18==37|provcd18==44|provcd18==45|provcd18==46

gen middle = 0
replace middle = 1 if provcd18=14|provcd18==15|provcd18==23|provcd18==22|provcd18==34|provcd18==36|provcd18==41|provcd18==42|provcd18==43

gen west = 0
replace west = 1 if provcd18==50|provcd18==51|provcd18==52|provcd18==53|provcd18==54|provcd18==61|provcd18==62|provcd18==63|provcd18==64|provcd18==65

keep pid income lnincome appearance bmi height weight experience edul tenure hukou east middle west urban gender age marriage state industry 

save CFPS.dta, replace

//OLS regression
reg lnincome appearance bmi experience edul tenure hukou east middle urban gender age marriage state industry, robust

//WLS regression
quietly reg lnincome appearance
predict uhat, residuals
gen uhatsq=uhat^2
gen ln_uhatsq=log(uhatsq)
reg ln_uhatsq lnincome appearancef
predict ghat, xb
gen h_hat=1/exp(ghat)
reg lnincome appearance [aw=h_hat]
est store e1
outreg2 [e1] using out.tex, replace

quietly reg lnincome appearance bmi
predict ahat, residuals
gen ahatsq=uhat^2
gen ln_ahatsq=log(ahatsq)
reg ln_ahatsq lnincome appearance bmi
predict bhat, xb
gen c_hat=1/exp(bhat)
reg lnincome appearance bmi[aw=c_hat]
est store e2
outreg2 [e2] using out.tex, append

quietly reg lnincome appearance bmi experience edul tenure hukou east middle urban gender age marriage state industry
predict dhat, residuals
gen dhatsq=uhat^2
gen ln_dhatsq=log(dhatsq)
reg ln_dhatsq lnincome appearance bmi experience edul tenure hukou east middle urban gender age marriage state industry
predict ehat, xb
gen f_hat=1/exp(ehat)
reg lnincome appearance bmi appearance bmi experience edul tenure hukou east middle urban gender age marriage state industry[aw=f_hat]
est store e3
outreg2 [e3] using out.tex, append

reg lnincome appearance bmi experience edul tenure hukou east middle urban gender age marriage state industry
est store e4
outreg2 [e4] using out.tex, append

//2SLS regression
reg appearance appearance_2 bmi experience edul tenure hukou east middle urban gender age marriage state industry
test appearance_2

ivregress 2sls lnincome bmi experience edul tenure hukou east middle urban gender age marriage state industry (appearance=appearance_2),first  
est store a_2sls
outreg2 [a_2sls] using out.tex, replace

reg lnincome appearance bmi experience edul tenure hukou east middle urban gender age marriage state industry
est store ols
outreg2 [ols] using out.tex, append

hausman a_2sls ols

oprobit lnincome appearance bmi experience edul tenure hukou east middle urban gender age marriage state industry
est store oprobit
outreg2 [oprobit] using out.tex, append