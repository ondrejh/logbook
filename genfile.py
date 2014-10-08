#! /var/bin/python3

from os import listdir,path,makedirs
import datetime

import subprocess

import utils

sourcefile = 'template.html'
filename = 'index.html'
billsdir = 'bills'

#fault fuelconsumption treshold
fault_consp_thld = 2/3

workdir='data'

if __name__ == '__main__':

    #load original html file
    print('Loading HTML template ... ',end='')
    try:
        f = open(sourcefile,'r',encoding='utf-8')
        fdata = f.read()
        fdata = fdata.split('\n')
        f.close()
        print('OK')
    except:
        print('Error')

    #scan directory containing bills
    print('Scanning bill directory ... ',end='')
    fscan = utils.scan_bills_directory(billsdir)
    if fscan==None:
        print('Error')
    else:
        bills = fscan[0]
        errors = fscan[1]
        if len(errors)==0:
            print('{} items'.format(len(bills)))
        else:
            print('{} items ({} errors)'.format(len(bills),len(errors)))
            cnt = 1
            for fname in errors:
                print('   ERROR {} .. {}'.format(cnt,fname))
                cnt += 1

    #sort data by car name
    print('Sorting bills ... ',end='')
    sortdata = utils.sort_data_by_vehicle(bills)
    if sortdata==None:
        print('Error')
    else:
        auta = sortdata[0]
        spotreba = sortdata[1]
        print('{} vehicles found'.format(len(auta)))
        for auto in auta:
            print('   {} .. {} bills'.format(auto,len(spotreba[auto])))

    # test if workdir exist and create it if not
    if (path.isdir(workdir)):
        pass
    else:
        print('Creating workdir ... ',end='')
        try:
            makedirs(workdir)
            print('OK')
        except:
            print('Error')

    #calculate fuel comp. for cars
    print('Calculate fuel consumption ... ',end='')
    try:
        datafiles = []
        for auto in auta:
            #print(auto)
            cnt = 0
            avg = 0
            # calculate fuel consumption 
            for i in range(len(spotreba[auto])):
                if i<(len(spotreba[auto])-1):
                    spotreba[auto][i].append(spotreba[auto][i][2]-spotreba[auto][i+1][2])
                    spotreba[auto][i].append(spotreba[auto][i][1]/(spotreba[auto][i][3]/100))
                    avg+=spotreba[auto][i][-1]
                    cnt+=1
            avg = avg/cnt
            #print(avg)
        
            rcnt = 0
            ravg = 0
            for row in spotreba[auto]:
                #test if fuel consumption isn't too low (means the bill is missing)
                if (len(row)==5) and (row[4]<(avg*fault_consp_thld)):
                    del(row[-1])
                    del(row[-1])
                if (len(row)==5):
                    ravg+=row[4]
                    rcnt+=1
                #print(row)

            ravg = ravg/rcnt
            #print(ravg)

            #save data form plotting
            fname = '{}/{}_data.txt'.format(workdir,auto)
            f = open(fname,'w')
            f.write('# date; fuel consumption[l/100km]\n')
            for raw in spotreba[auto]:
                try:
                    f.write('{:04}{:02}{:02}; {:0.2f}\n'.format(raw[0].year,raw[0].month,raw[0].day,raw[4]))
                except:
                    f.write('{:04}{:02}{:02}; NaN\n'.format(raw[0].year,raw[0].month,raw[0].day))
            f.close()
            datafiles.append(fname)
        print('OK')
        #for f in datafiles:
        #    print('   {}'.format(f))
    except:
        print('Error')

    # create gnuplot script
    print('Create gnuplot script file ... ',end='')
    try:
        fname = '{}/plotit.gp'.format(workdir)
        f = open(fname,'w')
        f.write('#! /usr/bin/gnuplot\n\n')
        f.write('# this script plots fuel consumption from files\n# is\'s probably automatically generated just before plotting so it doesn\'t make\n# a big sence to modify it\n# running the script: gnuplot plotit.gp\n\n')
        f.write('set xdata time\n')
        f.write('set style data lines\n')
        f.write('unset multiplot\n')
        f.write('set term png size 800,400\n')
        f.write('set timefmt "%Y%m%d"\n')
        f.write('set format x "%m/%y"\n')
        f.write('set ylabel "l/100km"\n')
        f.write('set autoscale y\n')
        f.write('set autoscale x\n')
        f.write('set output \'{}/chart.png\'\n'.format(workdir))
        f.write('set datafile separator \';\'\n')
        f.write('set grid\n')
        f.write('plot ')
        afirst = True
        for auto in auta:
            if afirst:
                afirst=False
            else:
                f.write(', \\\n     ')
            f.write('\'{}/{}_data.txt\' using 1:2 t \'{}\' w linespoints linewidth 2.5'.format(workdir,auto,auto))
        f.write('\n')
        f.close()
        print('OK')
    except:
        print('Error')

    # run gnuplot script
    print('Running gnuplot script ... ',end='')
    if subprocess.call('gnuplot {}/plotit.gp'.format(workdir),shell=True)==0:
          print('OK')
    else:
          print('Error')

    # parse html file
    print('Generating HTML file ... ',end='')
    try:
        f = open(filename,'w',encoding='utf-8')
        copynow = True
        
        for line in fdata:
            if copynow: #seek automated section (and copy)
                f.write('{}\n'.format(line))

                #seek table section
                p = line.find('<!-- tabulka uctenky -->')
                if p!=-1: #found table section
                    stepstr = line[:p]
                    cnt = 1
                    f.write('\n{}<table>\n'.format(stepstr))
                    f.write('{}\t<tr><th>pořadí</th><th>datum</th><th>auto</th><th>najeto</th><th>natankováno</th></tr>\n'.format(stepstr))
                    for bill in bills:
                        f.write('{}\t<tr><th><a href="#bill{}">{}</a></th><td>{}</td><td>{}</td><td>{} km</td><td>{} l</td></tr>\n'.format(stepstr,cnt,cnt,bill[0],bill[1],bill[3],bill[2]))
                        cnt += 1
                    f.write('{}</table>\n'.format(stepstr))
                    copynow=False

                #seek images section
                p = line.find('<!-- sekce uctenky -->')
                if p!=-1:
                    stepstr = line[:p]
                    cnt = 1
                    odd = True
                    f.write('\n')
                    for bill in bills:
                        f.write('{}<a name="bill{}"></a>\n'.format(stepstr,cnt))
                        if odd:
                            f.write('{}<figure class="left">\n'.format(stepstr))
                        else:
                            f.write('{}<figure class="right">\n'.format(stepstr))                        
                        f.write('{}\t<a href="{}/{}"><img class="full" src="{}/{}" alt="{} {}l {}km"></a>\n'.format(stepstr,billsdir,bill[4],billsdir,bill[4],bill[1],bill[2],bill[3]))
                        f.write('{}\t<figcaption><b>{}</b>) {} {} {}l {}km</figcaption>\n'.format(stepstr,cnt,bill[0],bill[1],bill[2],bill[3]))
                        f.write('{}</figure>\n\n'.format(stepstr))
                        if not odd:
                            f.write('{}<img class="divider" src="files/divider.png">\n\n'.format(stepstr))
                        odd = not odd
                        cnt+=1
                    copynow=False
                    
            else: #skip to end of automated section (not copy)
                p = line.find('<!-- konec ')
                if p!=-1: #found end of automated section
                    f.write('{}\n'.format(line))
                    copynow=True

        f.close()
        print('OK')
    except:
        print('Error')
