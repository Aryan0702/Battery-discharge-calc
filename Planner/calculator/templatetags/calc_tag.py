from urllib import request
from django import template
from http.client import HTTPResponse
#from django.shortcuts import render
    
register = template.Library()  
    
@register.simple_tag
#A = request.GET['query']
def calculator():

    # Trip planner : total capacity - external forces*time + regen efficiency -  AC load Energy consumed for AC
    # integral from ty to tx for 2.9 [cooling capcity of AC/EER*% of hour that compresor runs
    # Account for temperature vs discharge later

    import math as mt
    from scipy.integrate import quad

    total_cap = 21.2
    cd = 0.36
    cf = 0.015
    A = 2.2
    d = 1.21
    g = 9.8
    V = 2.8
    m = 1270
    grad = 5
    N = 0.6
    outT = 28
    desT = 20
    car_vol = 0
    EER = 5.118
    coolcap = 3.5


    def conv_v(V):
        V = V*5/18
        return V


    def find_v(dist, t):
        return conv_v(dist/t)

    # INTEGRAL

    def integrand(x, func):
        return func

    # EXT FORCES

    def F_winres(d, v, A):
        F_w = (1/2)*v**2*cd*A*d
        return F_w


    def F_rollres(m):
        F_r = m*g*cf
        return F_r


    def F_slope(m, grad):
        ang = mt.atan(grad/100)
        F_s = m*g*mt.sin(ang)
        return F_s


    def sum_ext_p(d, dist, t, A, m, grad):
        V = find_v(dist, t)
        #V = convert_v(V)
        sum_ext = F_slope(m, grad)+F_rollres(m)+F_winres(d, V, A)
        # print(sum_ext)
        power = sum_ext*V/1000
        return power


    def ext_energy(sum_force, t1, t2):
        I, err = quad(integrand, t1, t2, args=(sum_force))
        return I

    # AC LOADS

    def conv_t(t):
        t = t*3600
        return t


    def calc_ttc(V, EER, coolcap, tin, tfin):
        t = ((V*1.21*0.718*(tin-tfin)+250)*EER)/(coolcap)
        return t


    def full_load(V, EER, coolcap, tin, tfin):
        I, err = quad(integrand, 0, calc_ttc(
            V, EER, coolcap, tin, tfin), args=(2.09))
        return I/3600


    def maintain_temp(coolcap, EER, t, tend):
        integ = (coolcap*0.6/EER)+0.09
        t = conv_t(t)
        I, err = quad(integrand, tend, t, args=(integ))
        return I/3600


    def tot_power_ac(p1, p2):
        ptot = p1+p2
        return ptot

    # REGEN

    def regen(m, Vin, Vfin, tbreak):
        if Vin <= 15:
            return 0
        else:
            vfin = conv_v(Vfin)
            vin = conv_v(Vin)
            a = abs((vfin-vin)/tbreak)
            I, err = quad(integrand, 0, tbreak, args=(a))
            reg_en = (m*N*(I**2))/(7200*1000)
            return reg_en

    # __________________________________________________________________________________________________________


    total_cap -= ext_energy(sum_ext_p(d, 85, 1, A, m, grad), 0, 0.5)
    # print(total_cap)
    total_cap += (regen(m, 85, 0, 100) -
                tot_power_ac(maintain_temp(EER, coolcap, 0.5,
                                            calc_ttc(V, coolcap, EER, 64, 24)),
                            full_load(V, coolcap, EER, 64, 24)))
    #print(total_cap)
    # print(calc_ttc(2.8,5.118,3.5,64,24))
    # print(full_load(2.8,5.118,3.5,64,24))
    #print(maintain_temp(3.5, 5.118, 2,calc_ttc(2.8,5.118,3.5,64,24)))
    #print(tot_power_ac(maintain_temp(3.5, 5.118, 2,calc_ttc(2.8,5.118,3.5,64,24)),
    #full_load(2.8,5.118,3.5,64,24)))
    #print(regen(1500, 80, 0, 100))
    #print(ext_energy(sum_ext_p(d,85, 1, A, m, grad), 0, 0.5))
    #print(F_slope(m, grad))
    # print(F_rollres(m))
    # print(convert_v(V))

    #print(sum_ext_p (d,85, 1, A, m, grad))
    #print(regen(m, conv_v(100)))

    return total_cap