#! /var/bin/python3

from os import listdir
from datetime import datetime

def scan_bills_directory(dir_name):

    ''' scan bills directory:
    returns table of bills([date1,car1,vol1,kmage1,fname1],[..2,..2,...],...)
    and list of error files (files which cant be parsed)
    if returns none directory cant be listed '''

    try:
        dirlist = listdir(dir_name)
    except:
        return None

    dirlist.sort(reverse=True)

    bills = []
    errors = []
    for fname in dirlist:
        try:
            sname = fname.split('.')[0].split('_')
            date = datetime.strptime(sname[0],'%Y%m%d').date()
            car = sname[1]
            vol = sname[2].split('l')
            vol = float('{}.{}'.format(vol[0],vol[1]))
            kmage = int(sname[3][:-2])
            bills.append([date,car,vol,kmage,fname])
        except:
            errors.append(fname)

    return(bills,errors)


def sort_data_by_vehicle(bills):

    ''' sort bills by vehicle:
    return list of vehicles and touple of bills,
    if returns none something went wrong '''

    auta = []
    spotreba = {}
    
    try:
        for bill in bills:
            if bill[1] not in spotreba:
                auta.append(bill[1])
                spotreba[bill[1]] = [[bill[0],bill[2],bill[3]],]
            else:
                spotreba[bill[1]].append([bill[0],bill[2],bill[3]])
    except:
        return None

    return(auta,spotreba)
            

def rename_vehicle(dir_name,previous_name,new_name):

    pass    
